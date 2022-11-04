import harfang as hg
from math import sqrt
from utils import RangeAdjust, MetersPerSecondToKMH


def CarModelCreate(name, instance_node_name, scene, scene_physics, resources, start_position, start_rotation):
	o = {}
	o['start_position'] = start_position
	o['start_rotation'] = start_rotation
	o['name'] = name

	# Instance_node is not affected by physics.
	o['instance_node'] = scene.GetNode(instance_node_name)
	if not o['instance_node'].IsValid():
		print("ERROR - Instance node not found !")
		return

	o['instance_node'].GetTransform().SetPos(hg.Vec3(0, 0, 0))
	o['scene_view'] = o['instance_node'].GetInstanceSceneView()
	o['nodes'] = o['scene_view'].GetNodes(scene)
	o['chassis_node'] = o['scene_view'].GetNode(scene, "car_body")
	if not o['chassis_node'].IsValid():
		print("ERROR - Parent node not found !")
		return

	o['chassis_node'].GetTransform().SetPos(o['start_position'])
	o['chassis_node'].GetTransform().SetRot(o['start_rotation'])
	o['thrust'] = o['scene_view'].GetNode(scene, "thrust")
	if not o['thrust'].IsValid():
		print("ERROR - Thrust node not found !")
		return

	o['wheels'] = []
	for n in range(4):
		wheel = o['scene_view'].GetNode(scene, "wheel_" + str(n))
		if not wheel.IsValid():
			print("ERROR - Wheel_" + str(n) + " node not found !")
			return
		o['wheels'].append(wheel)

	o['ray_dir'] = None
	obj = o['wheels'][1].GetObject()
	f, bounds = obj.GetMinMax(resources)
	o['wheels_ray'] = bounds.mx.y
	o['ray_max_dist'] = o['wheels_ray'] + 0.2

	o['wheels_rot_speed'] = [0, 0, 0, 0]
	o['ground_hits'] = [False, False, False, False]
	o['ground_impacts'] = [None, None, None, None]

	# Constants

	o['mass'] = 1000
	o['spring_friction'] = 2500
	o['tires_reaction'] = 25
	o['tires_grip'] = 5000
	o['steering_angle_max'] = 45
	o['thrust_power'] = 400000  # Acceleration
	o['brakes_power'] = 1000000
	o['steering_speed'] = 150
	o['max_speed'] = 130

	# Variables

	o['steering_angle'] = 0

	# Get wheels rays

	o['local_rays'] = []
	for wheel in o['wheels']:
		o['local_rays'].append(wheel.GetTransform().GetPos())

	return o


def CarModelReset(rccar, scene_physics):
	scene_physics.NodeResetWorld(rccar['chassis_node'], hg.TransformationMat4(
		rccar['start_position'], rccar['start_rotation']))


def CarModelForceSteering(rccar, angle, steering_wheel):
	if angle > 0.01:
		rccar['steering_angle'] = RangeAdjust(
			angle, 0.3, 1, 0, rccar['steering_angle_max'])
		rccar['thrust'].GetTransform().SetRot(
			hg.Deg3(0, rccar['steering_angle'], 0))
		steering_wheel_rot = steering_wheel.GetTransform().GetRot()
		steering_wheel.GetTransform().SetRot(hg.Deg3(steering_wheel_rot.x, 180 -
													 rccar['steering_angle'] * 3, steering_wheel_rot.z))
	elif angle < -0.01:
		rccar['steering_angle'] = RangeAdjust(
			angle, -0.3, -1, 0, -rccar['steering_angle_max'])
		rccar['thrust'].GetTransform().SetRot(
			hg.Deg3(0, rccar['steering_angle'], 0))
		steering_wheel_rot = steering_wheel.GetTransform().GetRot()
		steering_wheel.GetTransform().SetRot(hg.Deg3(steering_wheel_rot.x, 180 -
													 rccar['steering_angle'] * 3, steering_wheel_rot.z))

def CarModelIncreaseSteering(car_model, angle):
	car_model['steering_angle'] = max(min(car_model['steering_angle'] + angle, car_model['steering_angle_max']), -car_model['steering_angle_max'])
	car_model['thrust'].GetTransform().SetRot(
			hg.Deg3(0, car_model['steering_angle'], 0))


def CarModelApplyAcceleration(rccar, value, scene_physics):
	f = 0
	for i in range(2):
		if rccar['ground_hits'][i]:
			f = f + 0.5

	pos = hg.GetT(rccar['thrust'].GetTransform().GetWorld())
	dir = hg.GetZ(rccar['thrust'].GetTransform().GetWorld())
	v = scene_physics.NodeGetLinearVelocity(rccar['chassis_node'])
	v_kmh = MetersPerSecondToKMH(hg.Len(v))
	if v_kmh > (0.9 * rccar['max_speed']):
		adjusted_accel = RangeAdjust(
			v_kmh, 0.9 * rccar['max_speed'], rccar['max_speed'], 1, 0)
		scene_physics.NodeAddImpulse(
			rccar['chassis_node'], dir * f * value * (1/60) * adjusted_accel, pos)
	else:
		scene_physics.NodeAddImpulse(
			rccar['chassis_node'], dir * f * value * (1/60), pos)


def CarModelApplyBrake(rccar, value, scene_physics):
	f = 0
	for i in range(4):
		if rccar['ground_hits'][i]:
			f = f + 0.25

	v = scene_physics.NodeGetLinearVelocity(rccar['chassis_node'])
	value = value * min(hg.Len(v), 1)
	pos = hg.GetT(rccar['thrust'].GetTransform().GetWorld())
	scene_physics.NodeAddImpulse(
		rccar['chassis_node'], hg.Normalize(v) * (1 / 60) * f * -value, pos)


def CarModelUpdate(rccar, scene, scene_physics, dts):
	scene_physics.NodeWake(rccar['chassis_node'])
	rccar['ray_dir'] = hg.Reverse(
		hg.GetY(rccar['chassis_node'].GetTransform().GetWorld()))

	for i in range(4):
		CarModelUpdateWheel(rccar, scene, scene_physics, i, dts)

	car_velocity = scene_physics.NodeGetLinearVelocity(rccar['chassis_node'])
	car_world = rccar['chassis_node'].GetTransform().GetWorld()
	car_pos = hg.GetT(car_world)
	car_lines = [[car_pos + hg.GetX(car_world) * 2, car_pos - hg.GetX(car_world) * 2, hg.Color.Red], [car_pos + hg.GetY(car_world) * 2,
																									  car_pos - hg.GetY(car_world) * 2, hg.Color.Green], [car_pos + hg.GetZ(car_world) * 2, car_pos - hg.GetZ(car_world) * 2, hg.Color.Blue]]
	wheel_rays_debug = {"car_matrix": rccar['chassis_node'].GetTransform(
	).GetWorld(), "rays": rccar['local_rays'], "ray_dir":  rccar['ray_dir'], "ray_max_dist": rccar['ray_max_dist'], "ground_impacts" : rccar['ground_impacts'], "ground_hits": rccar['ground_hits']}

	return car_velocity, car_pos, car_lines, wheel_rays_debug


def CarModelUpdateWheel(rccar, scene, scene_physics, id, dts):

	wheel = rccar['wheels'][id]
	mat = rccar['chassis_node'].GetTransform(
	).GetWorld()  # Ray position in World space
	ray_pos = mat * rccar['local_rays'][id]

	hit = scene_physics.RaycastFirstHit(
		scene, ray_pos, rccar['ray_dir'] * rccar['ray_max_dist'] + ray_pos)
	rccar['ground_hits'][id] = False

	if hit.t > 0 and hit.t < rccar['ray_max_dist']:
		rccar['ground_impacts'][id] = hit
		hit_distance = hg.Len(rccar['ground_impacts'][id].P - ray_pos)
		if hit_distance <= rccar['ray_max_dist']:
			rccar['ground_hits'][id] = True

	if rccar['ground_hits'][id]:

		v = hg.Reverse(scene_physics.NodeGetPointVelocity(
			rccar['chassis_node'], ray_pos))

		# Spring bounce

		v_dot_ground_n = hg.Dot(rccar['ground_impacts'][id].N, v)
		if v_dot_ground_n > 0:
			v_bounce = rccar['ground_impacts'][id].N * v_dot_ground_n
			scene_physics.NodeAddImpulse(
				rccar['chassis_node'], v_bounce * rccar['spring_friction'] * dts, ray_pos)

		# Tire/Ground reaction

		wheel_reaction = sqrt(
			rccar['ray_max_dist'] - hit_distance) * rccar['tires_reaction']
		scene_physics.NodeAddForce(
			rccar['chassis_node'], rccar['ground_impacts'][id].N * wheel_reaction * rccar['mass'] / 4, ray_pos)

		# Wheel lateral friction

		x_axis = hg.GetX(wheel.GetTransform().GetWorld())
		proj = hg.Dot(x_axis, v)
		v_lat = x_axis * proj
		scene_physics.NodeAddImpulse(
			rccar['chassis_node'], v_lat * rccar['tires_grip'] * dts, ray_pos)

		# Adjust wheel on the ground

		wheel_p = wheel.GetTransform().GetPos()
		wheel_p.y = rccar['local_rays'][id].y - \
			hit_distance + rccar['wheels_ray']
		wheel.GetTransform().SetPos(wheel_p)

		# Wheel rotation

		z_axis = hg.Normalize(hg.Cross(x_axis, rccar['ray_dir']))
		vlin = hg.Dot(z_axis, v)  # Linear speed (along Z axis)
		rccar['wheels_rot_speed'][id] = (vlin / rccar['wheels_ray'])
	else:
		rccar['wheels_rot_speed'][id] = rccar['wheels_rot_speed'][id] * \
			0.95  # Wheel slow-down

	rot = wheel.GetTransform().GetRot()
	rot.x = rot.x + rccar['wheels_rot_speed'][id] * dts
	if id == 0 or id == 1:
		rot.y = hg.Deg(rccar['steering_angle'])

	wheel.GetTransform().SetRot(rot)


def CarModelGetParentNode(rccar):
	return rccar['chassis_node']


def CarModelControl(rccar, scene_physics, kb, dts, steering_wheel, joystick, control_keyboard):
	brake = reverse = False
	if joystick.Down(7) or kb.Down(hg.K_Up):
		CarModelApplyAcceleration(
			rccar,  rccar['thrust_power'] * dts, scene_physics)

	if kb.Down(hg.K_Down):
		CarModelApplyAcceleration(
			rccar, -rccar['thrust_power'] * dts, scene_physics)
		reverse = True

	if joystick.Down(6) or kb.Down(hg.K_Space):
		CarModelApplyBrake(rccar, rccar['brakes_power'] * dts, scene_physics)
		brake = True

	if control_keyboard:
		if kb.Down(hg.K_Left):
			CarModelIncreaseSteering(rccar, -rccar['steering_speed'] * dts)
		if kb.Down(hg.K_Right):
			CarModelIncreaseSteering(rccar, rccar['steering_speed'] * dts)

	else:
		CarModelForceSteering(rccar, joystick.Axes(0), steering_wheel)

	if kb.Pressed(hg.K_Backspace):
		CarModelReset(rccar, scene_physics)

	return brake, reverse
