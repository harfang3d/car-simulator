import harfang as hg
import json, os
from utils import *

def CreateNewCar(scene, res, pos):
	node, _ = hg.CreateInstanceFromAssets(scene, hg.TranslationMat4(pos), "vehicles/ai_vehicle/drivable_car.scn", res, hg.GetForwardPipelineInfo())
	return node

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