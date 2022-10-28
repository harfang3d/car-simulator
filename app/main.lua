-- HARFANG® 3D - www.harfang3d.com - Raycast Car demo sample

hg = require("harfang")
rcar = require("car")

-- HARFANG3D inits

hg.InputInit()
hg.WindowSystemInit()

res_x, res_y = 1280, 720
win = hg.RenderInit('Raycast car', res_x, res_y, hg.RF_VSync | hg.RF_MSAA4X)

pipeline = hg.CreateForwardPipeline()
res = hg.PipelineResources()

hg.AddAssetsFolder("assets")

-- Display physics debug lines

vtx_lines = hg.VertexLayout()
vtx_lines:Begin()
vtx_lines:Add(hg.A_Position, 3, hg.AT_Float)
vtx_lines:Add(hg.A_Color0, 3, hg.AT_Float)
vtx_lines:End()
lines_program = hg.LoadProgramFromAssets("shaders/pos_rgb")

-- Load scene

scene = hg.Scene()
hg.LoadSceneFromAssets("main.scn", scene, res, hg.GetForwardPipelineInfo())
-- cam = scene:GetNode("CameraInterior")
cam = scene:GetNode("Camera")
scene:SetCurrentCamera(cam)
steering_wheel = scene:GetNode("steering_wheel")

-- Ground

vs_decl= hg.VertexLayoutPosFloatNormUInt8()
cube_mdl = hg.CreateCubeModel(vs_decl, 10, 10, 10)
cube_ref = res:AddModel('cube', cube_mdl)
ground_mdl = hg.CreateCubeModel(vs_decl, 100, 0.01, 100)
ground_ref = res:AddModel('ground', ground_mdl)
prg_ref = hg.LoadPipelineProgramRefFromAssets('core/shader/pbr.hps', res, hg.GetForwardPipelineInfo())

function create_material(ubc, orm)
    mat = hg.Material()
    hg.SetMaterialProgram(mat, prg_ref)
    hg.SetMaterialValue(mat, "uBaseOpacityColor", ubc)
    hg.SetMaterialValue(mat, "uOcclusionRoughnessMetalnessColor", orm)
    return mat
end

mat_ground = create_material(hg.Vec4(22/255, 42/255, 42/255, 1),hg.Vec4(1, 1, 0, 1))

cube_node = hg.CreatePhysicCube(scene, hg.Vec3(10,10,10), hg.TransformationMat4(hg.Vec3(0, -2.5, -10),hg.Deg3(30, 0, 10)), cube_ref, {mat_ground}, 0)
ground_node = hg.CreatePhysicCube(scene, hg.Vec3(100, 0.01, 100), hg.TranslationMat4(hg.Vec3(0, -0.005, 0)), ground_ref, {mat_ground}, 0)

cube_node:GetRigidBody():SetType(hg.RBT_Kinematic)
ground_node:GetRigidBody():SetType(hg.RBT_Kinematic)

-- Scene physics

clocks = hg.SceneClocks()
physics = hg.SceneBullet3Physics()
car = CreateRCCar("Kubolid", "car", scene, physics, res, hg.Vec3(0, 1.5, 0))
physics:SceneCreatePhysicsFromAssets(scene)

-- Inputs

keyboard = hg.Keyboard()
mouse = hg.Mouse()
hg.ResetClock()

-- Main loop

while not keyboard:Pressed(hg.K_Escape) do

    keyboard:Update()
    mouse:Update()

	dt = hg.TickClock()
    dts = hg.time_to_sec_f(dt)

    -- Car updates

    RCCarControl(car, physics, keyboard, dts, steering_wheel)
    RCCarUpdate(car, scene, physics, dts)

    -- Scene updates

    hg.SceneUpdateSystems(scene, clocks, dt, physics, hg.time_from_sec_f(1/60), 3)
	vid, passId = hg.SubmitSceneToPipeline(0, scene, hg.IntRect(0, 0, res_x, res_y), true, pipeline, res)

    -- Debug physics

    hg.SetViewClear(vid, 0, 0, 1.0, 0)
    hg.SetViewRect(vid, 0, 0, res_x, res_y)
    cam_mat = cam:GetTransform():GetWorld()
    view_matrix = hg.InverseFast(cam_mat)
    c = cam:GetCamera()
    projection_matrix = hg.ComputePerspectiveProjectionMatrix(c:GetZNear(), c:GetZFar(), hg.FovToZoomFactor(c:GetFov()), hg.Vec2(res_x / res_y, 1))
    hg.SetViewTransform(vid, view_matrix, projection_matrix)
    rs = hg.ComputeRenderState(hg.BM_Opaque, hg.DT_Disabled, hg.FC_Disabled)
    physics:RenderCollision(vid, vtx_lines, lines_program, rs, 0)

    -- EoF

	hg.Frame()
	hg.UpdateWindow(win)    

end

hg.RenderShutdown()
hg.DestroyWindow(win)
