import harfang as hg
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
