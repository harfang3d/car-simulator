hg = require("harfang")

function CreateRCCar(name, instance_node_name, scene, scene_physics, resources, start_position, start_rotation)
    local o = {}
    o.start_position = start_position or hg.Vec3(0, 0, 0)
    o.start_rotation = start_rotation or hg.Vec3(0, 0, 0)
    o.name = name
   
    -- Instance_node is not affected by physics.
    o.instance_node = scene:GetNode(instance_node_name)
    if not o.instance_node:IsValid() then
        print("ERROR - Instance node not found !")
        return
    end
    o.instance_node:GetTransform():SetPos(hg.Vec3(0, 0, 0))
    o.scene_view = o.instance_node:GetInstanceSceneView()
    o.nodes = o.scene_view:GetNodes(scene)
    o.chassis_node = o.scene_view:GetNode(scene, "car_body")
    if not o.chassis_node:IsValid() then
        print("ERROR - Parent node not found !")
        return
    end
    o.chassis_node:GetTransform():SetPos(o.start_position)
    o.chassis_node:GetTransform():SetRot(o.start_rotation)
    o.thrust = o.scene_view:GetNode(scene, "thrust")
    if not o.thrust:IsValid() then
        print("ERROR - Thrust node not found !")
        return
    end
    o.wheels = {}
    for n = 0, 3 do
        wheel = o.scene_view:GetNode(scene, "wheel_" .. n)
        if not wheel:IsValid() then
            print("ERROR - Wheel_"..n.." node not found !")
            return
        end
        table.insert(o.wheels, wheel)
    end
    
    o.ray_dir = nil
    obj = o.wheels[1]:GetObject()
    f,bounds = obj:GetMinMax(resources)
    o.wheels_ray = bounds.mx.y
    o.ray_max_dist = o.wheels_ray + 0.2

    o.wheels_rot_speed = {0, 0, 0, 0}
    o.ground_hits = {false, false, false, false}
    o.ground_impacts = {nil, nil, nil, nil}

    -- Constants
    
    o.mass = 1000
    o.spring_friction = 2500
    o.tires_reaction = 25
    o.tires_adhesion = 1500
    o.front_angle_max = 45
    o.thrust_power = 400000 -- Acceleration
    o.brakes_power = 1000000
    o.turn_speed = 150
   
    -- Variables

    o.front_angle = 0
   
    -- Setup physics

    o.chassis_rigid = scene:CreateRigidBody()
    o.chassis_rigid:SetType(hg.RBT_Dynamic)
    o.chassis_node:SetRigidBody(o.chassis_rigid)
    colbox = scene:CreateCollision()
    colbox:SetType(hg.CT_Cube)
    colbox:SetSize(hg.Vec3(1, 0.5, 3))
    colbox:SetMass(o.mass)
    colbox:SetLocalTransform(hg.TransformationMat4(hg.Vec3(0, 0, 0), hg.Deg3(0, 0, 0)))
    o.chassis_node:SetCollision(1,colbox)
    o.chassis_rigid:SetAngularDamping(0)
    o.chassis_rigid:SetLinearDamping(0)
    scene_physics:NodeCreatePhysicsFromAssets(o.chassis_node)


    -- Get wheels rays

    o.local_rays = {}
    for _, wheel in pairs(o.wheels) do
        table.insert(o.local_rays, wheel:GetTransform():GetPos())
    end
   
    return o
end

function RCCarReset(rccar, scene_physics)
    scene_physics:NodeResetWorld(rccar.chassis_node, hg.TransformationMat4(rccar.start_position, rccar.start_rotation))
end

function RCCarTurn(rccar, angle, steering_wheel)
    rccar.front_angle = math.max(math.min(rccar.front_angle + angle, rccar.front_angle_max), -rccar.front_angle_max)
    rccar.thrust:GetTransform():SetRot(hg.Deg3(0, rccar.front_angle, 0))
    steering_wheel_rot = steering_wheel:GetTransform():GetRot()
    steering_wheel:GetTransform():SetRot(hg.Deg3(steering_wheel_rot.x, 180 - rccar.front_angle * 2, steering_wheel_rot.z))
end

function RCCarAccelerate(rccar, value, scene_physics)
    f = 0
    for i = 1, 2 do
        if rccar.ground_hits[i] then
            f = f + 0.5
        end
    end
    pos = hg.GetT(rccar.thrust:GetTransform():GetWorld())
    dir = hg.GetZ(rccar.thrust:GetTransform():GetWorld())
    scene_physics:NodeAddImpulse(rccar.chassis_node, dir *  f * value * (1/60), pos)
end

function RCCarBrake(rccar, value, scene_physics)
    f = 0
    for i = 1, 4 do
        if rccar.ground_hits[i] then
            f = f + 0.25
        end
    end
    v = scene_physics:NodeGetLinearVelocity(rccar.chassis_node)
    value = value * math.min(hg.Len(v), 1)
    pos = hg.GetT(rccar.thrust:GetTransform():GetWorld())
    scene_physics:NodeAddImpulse(rccar.chassis_node,hg.Normalize(v) * (1 / 60) * f * -value, pos)
end

function RCCarUpdate(rccar, scene, scene_physics, dts)
    scene_physics:NodeWake(rccar.chassis_node)
    rccar.ray_dir = hg.Reverse(hg.GetY(rccar.chassis_node:GetTransform():GetWorld()))

    for i = 1, 4 do
        RCCarUpdateWheel(rccar, scene, scene_physics, i, dts)
    end
end

function RCCarUpdateWheel(rccar, scene, scene_physics, id, dts)

    wheel = rccar.wheels[id]
    mat = rccar.chassis_node:GetTransform():GetWorld()  -- Ray position in World space
    ray_pos = mat * rccar.local_rays[id]

    hit = scene_physics:RaycastFirstHit(scene,ray_pos, rccar.ray_dir * rccar.ray_max_dist + ray_pos)
    rccar.ground_hits[id] = false
    
    if hit.t > 0 and hit.t < rccar.ray_max_dist then
        rccar.ground_impacts[id] = hit
        hit_distance = hg.Len(rccar.ground_impacts[id].P - ray_pos)
        if hit_distance <= rccar.ray_max_dist then
            rccar.ground_hits[id] = true
        end
    end

    if rccar.ground_hits[id] then
        
        v = hg.Reverse(scene_physics:NodeGetPointVelocity(rccar.chassis_node, ray_pos))

        -- Spring bounce

        v_dot_ground_n = hg.Dot(rccar.ground_impacts[id].N, v)
        if v_dot_ground_n > 0 then
            v_bounce = rccar.ground_impacts[id].N * v_dot_ground_n
            scene_physics:NodeAddImpulse(rccar.chassis_node,v_bounce * rccar.spring_friction * dts, ray_pos)
        end

        -- Tire/Ground reaction

        wheel_reaction = math.sqrt(rccar.ray_max_dist - hit_distance) * rccar.tires_reaction
        scene_physics:NodeAddForce(rccar.chassis_node, rccar.ground_impacts[id].N * wheel_reaction * rccar.mass / 4, ray_pos)

        -- Wheel lateral friction
        
        x_axis = hg.GetX(wheel:GetTransform():GetWorld())
        proj = hg.Dot(x_axis, v)
        v_lat = x_axis * proj
        scene_physics:NodeAddImpulse(rccar.chassis_node, v_lat * rccar.tires_adhesion * dts, ray_pos)

        -- Adjust wheel on the ground

        wheel_p = wheel:GetTransform():GetPos()
        wheel_p.y = rccar.local_rays[id].y - hit_distance + rccar.wheels_ray
        wheel:GetTransform():SetPos(wheel_p)

        -- Wheel rotation

        z_axis = hg.Normalize(hg.Cross(x_axis, rccar.ray_dir))
        vlin = hg.Dot(z_axis, v)  -- Linear speed (along Z axis)
        rccar.wheels_rot_speed[id] = (vlin / rccar.wheels_ray)
    else
        rccar.wheels_rot_speed[id] = rccar.wheels_rot_speed[id] * 0.95  -- Wheel slow-down
    end

    rot = wheel:GetTransform():GetRot()
    rot.x = rot.x + rccar.wheels_rot_speed[id] * dts
    if id == 1 or id == 2 then
        rot.y = hg.Deg(rccar.front_angle)
    end
    wheel:GetTransform():SetRot(rot)
end

function RCCarGetParentNode(rccar)
    return rccar.chassis_node
end

function RCCarControl(rccar, scene_physics, kb, dts, steering_wheel)
    if kb:Down(hg.K_Up) then
        RCCarAccelerate(rccar,  rccar.thrust_power * dts, scene_physics)
    end
    if kb:Down(hg.K_Down) then
        RCCarAccelerate(rccar, -rccar.thrust_power * dts, scene_physics)
    end
    if kb:Down(hg.K_Space) then
        RCCarBrake(rccar, rccar.brakes_power * dts, scene_physics)
    end
    if kb:Down(hg.K_Left) then
        RCCarTurn(rccar, -rccar.turn_speed * dts, steering_wheel)
    end
    if kb:Down(hg.K_Right) then
        RCCarTurn(rccar, rccar.turn_speed * dts, steering_wheel)
    end
    if kb:Pressed(hg.K_Backspace) then
        RCCarReset(rccar, scene_physics)
    end
end