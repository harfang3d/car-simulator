import harfang as hg
import json
import os
from utils import *
from math import pi
from gui import DrawLine
from random import uniform, randint


# Detect the closest track (attached to a node in the scene) to a given position.
def DetectClosestTrack(nodes_track_data, target_pos):
    closest_track_data = None
    closest_vector = None
    closest_track = None
    closest_default = True
    for nodes_data in nodes_track_data:
        track_min_max = nodes_data['min_max']

        for track in nodes_data['track_data']:
            for vec_index, vector in enumerate(track['pos']):
                if not closest_track_data:
                    closest_track_data = nodes_data
                    closest_vector = vector
                    closest_track = [vec_index, track]
                else:
                    if hg.Contains(track_min_max, target_pos):
                        if hg.Dist(target_pos, vector) < hg.Dist(target_pos, closest_vector):
                            closest_track_data = nodes_data
                            closest_vector = vector
                            closest_track = [vec_index, track]
                            closest_default = False

    if closest_default:  # need to detect by node because we are not sure that the track is the correct one
        closest_vector = hg.Vec3(99999, 99999, 99999)  # reset closest vector
        closest_track_data = None  # reset closest track
        for nodes_data in nodes_track_data:
            node = nodes_data['node']
            if not closest_track_data:
                closest_track_data = nodes_data
                for track in nodes_data['track_data']:
                    for vec_index, vector in enumerate(track['pos']):
                        if hg.Dist(target_pos, vector) < hg.Dist(target_pos, closest_vector):
                            closest_vector = vector
                            closest_track = [vec_index, track]
            if hg.Dist(target_pos, node.GetTransform().GetPos()) < hg.Dist(target_pos, closest_track_data['node'].GetTransform().GetPos()):
                closest_track_data = nodes_data
                for track in nodes_data['track_data']:
                    for vec_index, vector in enumerate(track['pos']):
                        if hg.Dist(target_pos, vector) < hg.Dist(target_pos, closest_vector):
                            closest_vector = vector
                            closest_track = [vec_index, track]

    return closest_track_data, closest_vector, closest_track


# Grab a random vector from a track within a certain distance from the given car position (will be a lerped position if track only contains two vectors)
def GetRandomVectorsOnTrack(node_track_data, car_pos):
    track_data = node_track_data['track_data']
    track_vectors = []
    for track in track_data:
        random_vec = hg.Vec3(99999, 99999, 99999)
        turn_index = 0
        lerp_value = 0

        while hg.Dist(car_pos, random_vec) > 300 or hg.Dist(car_pos, random_vec) < 100:
            lerp_value = uniform(0, 1)
            if len(track['pos']) == 2:
                turn_index = 0
                random_vec = hg.Lerp(
                    track['pos'][0], track['pos'][1], lerp_value)
            else:
                turn_index = randint(0, len(track['pos']) - 2)
                random_vec = hg.Lerp(
                    track['pos'][turn_index], track['pos'][turn_index + 1], lerp_value)

        track_vectors.append({'vector': random_vec,
                              'turn_index': turn_index, 'lerp_value': lerp_value, 'track': track})

    return track_vectors


# Algorithm handling the position, rotation and wheel rotation of the autonomous cars
def HandleAutomatedCars(scene, res, nodes_track_data, local_pos, spawned_cars, dt, physics):
    dts = hg.time_to_sec_f(dt)
    closest_track_data, _, _ = DetectClosestTrack(
        nodes_track_data, local_pos)

    for car in spawned_cars:
        if hg.Dist(
                local_pos, car['node'].GetTransform().GetPos()) > 300:
            car['node'].DestroyInstance()

    spawned_cars = [car for car in spawned_cars if hg.Dist(
        local_pos, car['node'].GetTransform().GetPos()) < 300]

    if len(spawned_cars) < 10:
        track_vectors = GetRandomVectorsOnTrack(closest_track_data, local_pos)
        for track_vector in track_vectors:
            pos = track_vector['vector']
            node, _ = hg.CreateInstanceFromAssets(scene, hg.TranslationMat4(
                pos), "vehicles/ai_vehicle/drivable_car.scn", res, hg.GetForwardPipelineInfo())
            print("Just spawned a car at Vec3(" + str(pos.x) +
                  ", " + str(pos.y) + ", " + str(pos.z) + ")")
            spawned_cars
            track_vector['node'] = node
            spawned_cars.append(track_vector)
            physics.SceneCreatePhysicsFromAssets(scene)

    for car in spawned_cars:
        max_index = len(car['track']['pos']) - 1
        if car['lerp_value'] >= 1 and car['turn_index'] < max_index - 1:
            car['turn_index'] += 1
            car['lerp_value'] = 0
        if car['lerp_value'] >= 1 and car['turn_index'] == max_index - 1:
            _, closest_vector, closest_track = DetectClosestTrack(nodes_track_data, car['node'].GetTransform(
            ).GetPos() + hg.GetZ(car['node'].GetTransform().GetWorld()) * 10)
            if closest_track[0] != len(closest_track[1]['pos']) - 1:
                car['track'] = closest_track[1]
                car['vector'] = closest_vector
                car['lerp_value'] = 0
                car['turn_index'] = closest_track[0]

        dist_vectors = hg.Dist(
            car['track']['pos'][car['turn_index']], car['track']['pos'][car['turn_index'] + 1])
        new_car_lerp = car['lerp_value'] + \
            ((KMHtoMPS(car['track']['speed']) / dist_vectors) * dts)
        if new_car_lerp > 1:
            new_car_lerp = 1
        car['lerp_value'] = new_car_lerp
        if car['turn_index'] < max_index:
            car['vector'] = hg.Lerp(car['track']['pos'][car['turn_index']],
                                    car['track']['pos'][car['turn_index'] + 1], car['lerp_value'])
            car['node'].GetTransform().SetPos(car['vector'])
            if car['lerp_value'] < 1:
                wanted_rot = hg.GetRotation(hg.Mat4LookAt(
                    car['node'].GetTransform().GetPos(), car['track']['pos'][car['turn_index'] + 1]))
                car['node'].GetTransform().SetRot(hg.Vec3(0, wanted_rot.y, 0))

        car_wheels = []
        scene_view_node = car['node'].GetInstanceSceneView()
        for n in range(4):
            wheel = scene_view_node.GetNode(scene, "wheel_" + str(n))
            if not wheel.IsValid():
                print("ERROR - Wheel_" + str(n) + " node not found !")
                return
            car_wheels.append(wheel)

        for wheel in car_wheels:
            wheel_rot = wheel.GetTransform().GetRot()
            wheel_circumference = 0.35 * pi * 2  # 0.35 : wheel radius
            rps = KMHtoMPS(car['track']['speed']) / wheel_circumference
            # 360 = one revolution, rps = revolutions per second, dts = seconds since last frame
            angle_to_add = dts * rps * 360
            new_wheel_rot = wheel_rot
            new_wheel_rot.x += hg.Rad(angle_to_add)
            wheel.GetTransform().SetRot(new_wheel_rot)

    return spawned_cars


# Returns the list of all the nodes that correspond to a track in a scene, with transformed positions and bounding box
def GetTrackDataByNode(scene, track_data):
    node_track_data = []
    scene_nodes = scene.GetNodes()
    for node_idx in range(scene_nodes.size()):
        node_name = scene_nodes.at(node_idx).GetName()
        for k in track_data:
            if node_name == k:
                node_transformed_tracks = []
                node = scene_nodes.at(node_idx)
                node_world = node.GetTransform().GetWorld()
                list_x = []
                list_y = []
                list_z = []
                for track in track_data[k]:
                    transformed_track_data = {
                        'id': track['id'], 'pos': [], 'speed': track['speed']}
                    track_pos = track['pos']
                    for vec3 in track_pos:
                        transformed_vector = node_world * hg.Vec3(vec3[0], vec3[1], vec3[2])
                        list_x.append(transformed_vector.x)
                        list_y.append(transformed_vector.y)
                        list_z.append(transformed_vector.z)
                        transformed_track_data['pos'].append(transformed_vector)
                    node_transformed_tracks.append(transformed_track_data)
                min_x = min(list_x)
                min_y = min(list_y)
                min_z = min(list_z)
                max_x = max(list_x)
                max_y = max(list_y)
                max_z = max(list_z)
                min_y -= 5
                max_y += 5
                track_min_max = hg.MinMax(
                    hg.Vec3(min_x, min_y, min_z), hg.Vec3(max_x, max_y, max_z))
                node_track_data.append(
                    {'node': node, 'id': node_idx, 'track_data': node_transformed_tracks, 'min_max': track_min_max})

    return node_track_data


# Draws green lines between each vector of a given track
def DrawTrackData(node_track_data, opaque_view_id, vtx_line_layout, lines_program):
    tracks = node_track_data['track_data']
    for index, track in enumerate(tracks):
        # index 123 roads in the same direction as driver
        positions_list = track['pos']
        current_index = 0
        max_index = len(positions_list) - 1
        for i in range(max_index):
            DrawLine(hg.Vec3(positions_list[current_index].x, positions_list[current_index].y + 0.05, positions_list[current_index].z), hg.Vec3(positions_list[current_index + 1].x, positions_list[current_index + 1].y + 0.05, positions_list[current_index + 1].z),
                     hg.Color.Green, opaque_view_id, vtx_line_layout, lines_program)
            current_index += 1
