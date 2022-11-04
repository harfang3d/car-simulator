import harfang as hg
from utils import *

def CarCameraCreate(instance_node_name, scene):
	o = {}
	o['instance_node'] = scene.GetNode(instance_node_name)
	if not o['instance_node'].IsValid():
		print("!CarCameraCreate(): Instance node '" + instance_node_name + "' not found!")
		return

	o['scene_view'] = o['instance_node'].GetInstanceSceneView()
	o['nodes'] = o['scene_view'].GetNodes(scene)
	o['root_node'] = o['scene_view'].GetNode(scene, "car_body")
	if not o['root_node'].IsValid():
		print("!CarCameraCreate(): Parent node not found !")
		return

	o['camera_list'] = []
	for camera_name in {"camera_interior", "camera_exterior_rear"}:
		_n = o['scene_view'].GetNode(scene, camera_name)
		_f = hg.Normalize(hg.GetZ(_n.GetTransform().GetWorld()))
		_p = _n.GetTransform().GetPos()
		o['camera_list'].append({'node' : _n, 'trs' : _n.GetTransform(), 'vec_front' : _f, 'pos' : _p})

	o['current_camera'] = 0

	return o

def CarCameraUpdate(o, scene, kb, dt, car_velocity, render_mode):
	updated = False	
	if kb.Pressed(hg.K_C):
		o['current_camera'] = o['current_camera'] + 1
		if o['current_camera'] == len(o['camera_list']):
			o['current_camera'] = 0
		scene.SetCurrentCamera(o['camera_list'][o['current_camera']]['node'])
		updated = True
		

	# simulate head inertia
	if render_mode == "normal":
		_p = o['camera_list'][o['current_camera']]['pos']
		_f = Clamp(Map(hg.Len(car_velocity), -20.0, 20.0, 0.0, 1.0), 0.0, 1.0)
		_f = EaseInOutQuick(_f)
		_f = Map(_f, 0.0, 1.0, -0.1, 0.1)
		_p = _p + o['camera_list'][o['current_camera']]['vec_front'] * _f
		o['camera_list'][o['current_camera']]['trs'].SetPos(_p)
	# return current camera node
	return o['camera_list'][o['current_camera']]['node'], updated
