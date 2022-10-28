def CarLightsCreate(instance_node_name, scene):
    o = {}
    o['instance_node'] = scene.GetNode(instance_node_name)
    if not o['instance_node'].IsValid():
        print("!CarLightsCreate(): Instance node '" + instance_node_name + "' not found!")
        return

    # carlights
    # carlight_reverse, carlight_head_light, carlight_day_light, carlight_brake, carlight_backLight, carlight_turn_left, carlight_turn_right

    scene_view = o['instance_node'].GetInstanceSceneView()
    root_node = scene_view.GetNode(scene, "carlights")
    if not root_node.IsValid():
        print("!CarLightsCreate(): Carlights node not found !")
        return

    o['car_view'] = root_node.GetInstanceSceneView()
    o['carlight_list'] = {}
    for carlight_name in {"reverse", "head_light", "day_light", "brake", "backLight", "turn_left", "turn_right"}:
        _n = o['car_view'].GetNode(scene, "carlight_" + carlight_name)
        o['carlight_list']["carlight_" + carlight_name] = {'node' : _n, 'enabled' : False}
        _n.Disable()
    return o

def CarLightsSetBrake(o, state):
    o['carlight_list']['carlight_brake']['enabled'] = state

def CarLightsSetReverse(o, state):
    o['carlight_list']['carlight_reverse']['enabled'] = state

def CarLightsUpdate(o, scene, dt):
    for carlight_name in o['carlight_list']:
        if o['carlight_list'][carlight_name]['enabled']:
            o['carlight_list'][carlight_name]['node'].Enable()
        else:
            o['carlight_list'][carlight_name]['node'].Disable()