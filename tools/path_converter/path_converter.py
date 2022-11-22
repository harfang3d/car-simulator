import json
import os

path = os.getcwd() + "/"

file_dir_in = "in/"
file_dir_out = "out/"

files = []

for r, d, f in os.walk(path + file_dir_in):
    for file in f:
            files.append(os.path.join(r, file))

for f in files:
    file_name = os.path.basename(f).replace(".nms", "")

    with open(file_dir_in + file_name + '.nms', 'r') as f:
        lines = f.readlines()
        current_line = 0
        max_lines = len(lines)
        final_object = []
        while current_line < max_lines:
            line = lines[current_line]
            if "<Motion=" in line:
                motion_json = {'x': [], 'z': [], 'y': []}
                found_motion = current_line
                # print("Line of motion : " + str(found_motion))
                found_motion += 1
                line_after = lines[found_motion]
                if "<Id=" in line_after:
                    # print(line_after)
                    found_motion += 1
                    line_after = lines[found_motion]
                    if "<Channel=" in line_after:
                        # print(line_after)
                        found_motion += 1
                        line_after = lines[found_motion]
                        if '<Id="PositionX">' in line_after:
                            # print(line_after)
                            found_motion += 1
                            line_after = lines[found_motion]
                            if "<Curve=" in line_after:
                                # print(line_after)
                                found_motion += 1
                                line_after = lines[found_motion]
                                if "<Knot=" in line_after:
                                    # print(line_after)
                                    found_motion += 1
                                    line_after = lines[found_motion]
                                    if "<Count=" in line_after:
                                        # print(line_after)
                                        count = ""
                                        for i in range(line_after.find("<Count="), len(line_after)):
                                            if i > line_after.find("<Count=") + 6:
                                                if line_after[i] != '>':
                                                    count += line_after[i]
                                        # print("Count of x : " + count)
                                        found_motion += 1
                                        line_after = lines[found_motion]
                                        count = int(count)
                                        for i in range(count):
                                            if "<Knot=" in line_after:
                                                # print(line_after)
                                                coordinate = ""
                                                for i in range(line_after.find(":"), len(line_after)):
                                                    if i > line_after.find(":"):
                                                        if line_after[i] != '>' and line_after[i] != '"':
                                                            coordinate += line_after[i]
                                                # print("Coordinate : " + coordinate)
                                                motion_json['x'].append(float(coordinate))

                                                found_motion += 1
                                                line_after = lines[found_motion]

                                        if ">" in line_after:
                                            # print(line_after)
                                            found_motion += 1
                                            line_after = lines[found_motion]
                                            if ">" in line_after:
                                                # print(line_after)
                                                found_motion += 1
                                                line_after = lines[found_motion]
                                                if ">" in line_after:
                                                    # print(line_after)
                                                    found_motion += 1
                                                    line_after = lines[found_motion]
                                                    if "<Channel=" in line_after:
                                                        # print(line_after)
                                                        found_motion += 1
                                                        line_after = lines[found_motion]
                                                        if '<Id="PositionZ">' in line_after:
                                                            # print(line_after)
                                                            found_motion += 1
                                                            line_after = lines[found_motion]
                                                            if "<Curve=" in line_after:
                                                                # print(line_after)
                                                                found_motion += 1
                                                                line_after = lines[found_motion]
                                                                if "<Knot=" in line_after:
                                                                    # print(line_after)
                                                                    found_motion += 1
                                                                    line_after = lines[found_motion]
                                                                    if "<Count=" in line_after:
                                                                        # print(line_after)
                                                                        count = ""
                                                                        for i in range(line_after.find("<Count="), len(line_after)):
                                                                            if i > line_after.find("<Count=") + 6:
                                                                                if line_after[i] != '>':
                                                                                    count += line_after[i]
                                                                        # print("Count of Z : " + count)
                                                                        found_motion += 1
                                                                        line_after = lines[found_motion]
                                                                        count = int(count)
                                                                        for i in range(count):
                                                                            if "<Knot=" in line_after:
                                                                                # print(line_after)
                                                                                coordinate = ""
                                                                                for i in range(line_after.find(":"), len(line_after)):
                                                                                    if i > line_after.find(":"):
                                                                                        if line_after[i] != '>' and line_after[i] != '"':
                                                                                            coordinate += line_after[i]
                                                                                # print("Coordinate : " + coordinate)
                                                                                motion_json['z'].append(float(coordinate))


                                                                                found_motion += 1
                                                                                line_after = lines[found_motion]

                                                                        if ">" in line_after:
                                                                            # print(line_after)
                                                                            found_motion += 1
                                                                            line_after = lines[found_motion]
                                                                            if ">" in line_after:
                                                                                # print(line_after)
                                                                                found_motion += 1
                                                                                line_after = lines[found_motion]
                                                                                if ">" in line_after:
                                                                                    # print(line_after)
                                                                                    found_motion += 1
                                                                                    line_after = lines[found_motion]
                                                                                    if "<Channel=" in line_after:
                                                                                        # print(line_after)
                                                                                        found_motion += 1
                                                                                        line_after = lines[found_motion]
                                                                                        if '<Id="PositionY">' in line_after:
                                                                                            # print(line_after)
                                                                                            found_motion += 1
                                                                                            line_after = lines[found_motion]
                                                                                            if "<Curve=" in line_after:
                                                                                                # print(line_after)
                                                                                                found_motion += 1
                                                                                                line_after = lines[found_motion]
                                                                                                if "<Knot=" in line_after:
                                                                                                    # print(line_after)
                                                                                                    found_motion += 1
                                                                                                    line_after = lines[found_motion]
                                                                                                    if "<Count=" in line_after:
                                                                                                        # print(line_after)
                                                                                                        count = ""
                                                                                                        for i in range(line_after.find("<Count="), len(line_after)):
                                                                                                            if i > line_after.find("<Count=") + 6:
                                                                                                                if line_after[i] != '>':
                                                                                                                    count += line_after[i]
                                                                                                        # print("Count of Y : " + count)
                                                                                                        found_motion += 1
                                                                                                        line_after = lines[found_motion]
                                                                                                        count = int(count)
                                                                                                        for i in range(count):
                                                                                                            if "<Knot=" in line_after:
                                                                                                                # print(line_after)
                                                                                                                coordinate = ""
                                                                                                                for i in range(line_after.find(":"), len(line_after)):
                                                                                                                    if i > line_after.find(":"):
                                                                                                                        if line_after[i] != '>' and line_after[i] != '"':
                                                                                                                            coordinate += line_after[i]
                                                                                                                # print("Coordinate : " + coordinate)
                                                                                                                motion_json['y'].append(float(coordinate))


                                                                                                                found_motion += 1
                                                                                                                line_after = lines[found_motion]

                                                                                                        if ">" in line_after:
                                                                                                            # print(line_after)
                                                                                                            found_motion += 1
                                                                                                            line_after = lines[found_motion]
                                                                                                            if ">" in line_after:
                                                                                                                # print(line_after)
                                                                                                                found_motion += 1
                                                                                                                line_after = lines[found_motion]
                                                                                                                if ">" in line_after:
                                                                                                                    # print(line_after)
                                                                                                                    found_motion += 1
                                                                                                                    line_after = lines[found_motion]
                                                                                                                    if "<DataKnot=" in line_after:
                                                                                                                        # print(line_after)
                                                                                                                        found_motion += 1
                                                                                                                        line_after = lines[found_motion]
                                                                                                                        if "<Knot=" in line_after:
                                                                                                                            # print(line_after)
                                                                                                                            speed = ""
                                                                                                                            for i in range(line_after.find(":speed="), len(line_after)):
                                                                                                                                if i > line_after.find(":speed=") + 6:
                                                                                                                                    if line_after[i] != '>' and line_after[i] != '"':
                                                                                                                                        speed += line_after[i]
                                                                                                                            # print("Speed : " + speed)
                                                                                                                            motion_json['speed'] = int(speed)

                                                                                                                            found_motion += 1
                                                                                                                            line_after = lines[found_motion]
                final_object.append(motion_json)

            current_line += 1
        json_to_write = []
        for index, infos in enumerate(final_object):
            object_correct = {'id' : 'track_' + str(index), 'pos' : [], 'speed': infos['speed']}
            no_coordinates = len(infos['x'])
            for i in range(no_coordinates):
                object_correct['pos'].append([infos['x'][i], infos['y'][i], infos['z'][i]])
            json_to_write.append(object_correct)

        final_json = json.dumps(json_to_write, indent=4)
        with open(file_dir_out + file_name + '.json', 'w') as outfile:
            outfile.write(final_json)
