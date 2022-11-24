import harfang as hg
import json
import os
from utils import *
from gui import DrawLine
from random import uniform, randint


def GetRandomVectorsOnTrack(node_track_data, car_pos):
	track_data = node_track_data['track_data']
	track_vectors = []
	for track in track_data:
		random_vec = hg.Vec3(99999, 99999, 99999)
		track_straight = None
		turn_index = 0
		lerp_value = 0
		if len(track['pos']) == 2:
			track_straight = True
			while hg.Dist(car_pos, random_vec) > 300 or hg.Dist(car_pos, random_vec) < 100:
				lerp_value = uniform(0, 1)
				random_vec = hg.Lerp(
					track['pos'][0], track['pos'][1], lerp_value)
				print(hg.Dist(car_pos, random_vec))

		elif len(track['pos']) > 2:
			track_straight = False
			while hg.Dist(car_pos, random_vec) > 300 or hg.Dist(car_pos, random_vec) < 100:
				turn_index = randint(0, len(track['pos']) - 1)
				random_vec = track['pos'][turn_index]

		track_vectors.append({'straight': track_straight, 'vector': random_vec,
							  'turn_index': turn_index, 'lerp_value': lerp_value, 'track': track})

	return track_vectors


def HandleFakeCars(scene, res, nodes_track_data, local_pos, spawned_cars):
	closest_node = None
	closest_node_data = None

	for nodes_data in nodes_track_data:
		node = nodes_data['node']
		if not closest_node:
			closest_node = node
			closest_node_data = nodes_data
		else:
			if hg.Dist(local_pos, node.GetTransform().GetPos()) < hg.Dist(local_pos, closest_node.GetTransform().GetPos()):
				closest_node = node
				closest_node_data = nodes_data

	for car in spawned_cars:
		if hg.Dist(
				local_pos, car['node'].GetTransform().GetPos()) > 300:
			car['node'].DestroyInstance()

	spawned_cars = [car for car in spawned_cars if hg.Dist(
		local_pos, car['node'].GetTransform().GetPos()) < 300]

	if len(spawned_cars) < 6:
		track_vectors = GetRandomVectorsOnTrack(closest_node_data, local_pos)
		for track_vector in track_vectors:
			pos = track_vector['vector']
			node, _ = hg.CreateInstanceFromAssets(scene, hg.TranslationMat4(
				pos), "vehicles/ai_vehicle/drivable_car.scn", res, hg.GetForwardPipelineInfo())
			print("Just spawned a car at Vec3(" + str(pos.x) +
				  ", " + str(pos.y) + ", " + str(pos.z) + ")")
			spawned_cars
			track_vector['node'] = node
			spawned_cars.append(track_vector)
   
	# for car in spawned_cars:
		

	return spawned_cars


def HandleCarMovement(carnode, physics):
	carnode_transform = carnode.GetTransform()
	car_pos = carnode_transform.GetPos()
	# print("carpos : (" + str(car_pos.x) + ", " + str(car_pos.y) + ", " + str(car_pos.z) + ")")
	car_pos.z += 0.65
	carnode_transform.SetPos(car_pos)
	# physics.NodeWake(carnode)


def GetBlockTracks():
	file_dir_out = "out/"
	path = os.getcwd() + "/../tools/path_converter/" + file_dir_out

	files = []

	for r, d, f in os.walk(path):
		for file in f:
			files.append(os.path.join(r, file))

	final_data = {}

	for f in files:
		with open(f, 'r') as json_file:
			file_name = os.path.basename(f).replace(".json", "")
			node_name = file_name.replace("_tracks", "")
			data = json.loads(json_file.read())
			final_data[node_name] = data

	return final_data


def GetTrackDataByNode(scene, track_data):
	node_track_data = []
	scene_nodes = scene.GetNodes()
	for node_idx in range(scene_nodes.size()):
		node_name = scene_nodes.at(node_idx).GetName()
		for k in track_data:
			if node_name == k:
				node_localized_tracks = []
				node = scene_nodes.at(node_idx)
				node_world = node.GetTransform().GetWorld()
				for track in track_data[k]:
					localized_track_data = {'id': track['id'], 'pos': []}
					track_pos = track['pos']
					for vec3 in track_pos:
						localized_track_data['pos'].append(
							node_world * hg.Vec3(vec3[0], vec3[1], vec3[2]))
					node_localized_tracks.append(localized_track_data)
				node_track_data.append(
					{'node': node, 'id': node_idx, 'track_data': node_localized_tracks})

	return node_track_data


def DrawTrackData(node_track_data, opaque_view_id, vtx_line_layout, lines_program):
	tracks = node_track_data['track_data']
	for index, track in enumerate(tracks):
		# index 123 roads in the same direction as driver
		positions_list = track['pos']
		current_index = 0
		max_index = len(positions_list) - 1
		for i in range(max_index):
			DrawLine(positions_list[current_index], positions_list[current_index + 1],
					 hg.Color.Green, opaque_view_id, vtx_line_layout, lines_program)
			current_index += 1
