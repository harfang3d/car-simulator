import json
import os

def GetBlockTracks():
	path = os.getcwd() + "/assets/road_tracks"

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