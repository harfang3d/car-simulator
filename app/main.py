# HARFANG® 3D - www.harfang3d.com - Raycast Car demo sample
import harfang as hg
from car import *
from car_camera import *
from car_lights import *
from gui import *
import sys

render_mode = "normal"
if len(sys.argv) > 1:
	render_mode = "vr" if sys.argv[1] == "--vr" else "normal"

# HARFANG3D inits

hg.InputInit()
hg.WindowSystemInit()

res_x, res_y = 1900, 1000
win = hg.RenderInit('Raycast car', res_x, res_y, hg.RF_VSync | hg.RF_MSAA4X)

pipeline = hg.CreateForwardPipeline()
res = hg.PipelineResources()

render_data = hg.SceneForwardPipelineRenderData()  # this object is used by the low-level scene rendering API to share view-independent data with both eyes

# OpenVR initialization
if render_mode == "vr":
	if not hg.OpenVRInit():
		sys.exit()

vr_left_fb = hg.OpenVRCreateEyeFrameBuffer(hg.OVRAA_MSAA4x)
vr_right_fb = hg.OpenVRCreateEyeFrameBuffer(hg.OVRAA_MSAA4x)

hg.AddAssetsFolder("assets")

# ImGUI

if render_mode == "normal":
	imgui_prg = hg.LoadProgramFromAssets('core/shader/imgui')
	imgui_img_prg = hg.LoadProgramFromAssets('core/shader/imgui_image')

	hg.ImGuiInit(10, imgui_prg, imgui_img_prg)

# Display physics debug lines

vtx_lines = hg.VertexLayout()
vtx_lines.Begin()
vtx_lines.Add(hg.A_Position, 3, hg.AT_Float)
vtx_lines.Add(hg.A_Color0, 3, hg.AT_Float)
vtx_lines.End()
vtx_line_layout = hg.VertexLayoutPosFloatColorUInt8()
lines_program = hg.LoadProgramFromAssets("shaders/pos_rgb")

# Load scene

scene = hg.Scene()
hg.LoadSceneFromAssets("main.scn", scene, res, hg.GetForwardPipelineInfo())

# Ground

vs_decl= hg.VertexLayoutPosFloatNormUInt8()
cube_mdl = hg.CreateCubeModel(vs_decl, 10, 10, 10)
cube_ref = res.AddModel('cube', cube_mdl)
ground_mdl = hg.CreateCubeModel(vs_decl, 150, 0.01, 150)
ground_ref = res.AddModel('ground', ground_mdl)
prg_ref = hg.LoadPipelineProgramRefFromAssets('core/shader/pbr.hps', res, hg.GetForwardPipelineInfo())

def create_material(ubc, orm):
	mat = hg.Material()
	hg.SetMaterialProgram(mat, prg_ref)
	hg.SetMaterialValue(mat, "uBaseOpacityColor", ubc)
	hg.SetMaterialValue(mat, "uOcclusionRoughnessMetalnessColor", orm)
	return mat


mat_ground = create_material(hg.Vec4(22/255, 42/255, 42/255, 1),hg.Vec4(1, 1, 0, 1))

# cube_node = hg.CreatePhysicCube(scene, hg.Vec3(10,10,10), hg.TransformationMat4(hg.Vec3(0, -2.5, -10),hg.Deg3(30, 0, 10)), cube_ref, [mat_ground], 0)
# ground_node = hg.CreatePhysicCube(scene, hg.Vec3(150, 0.01, 150), hg.TranslationMat4(hg.Vec3(0, -0.005, 50)), ground_ref, [mat_ground], 0)

# cube_node.GetRigidBody().SetType(hg.RBT_Kinematic)
# ground_node.GetRigidBody().SetType(hg.RBT_Kinematic)

# Scene physics

clocks = hg.SceneClocks()
physics = hg.SceneBullet3Physics()
car = CreateRCCar("Generic Car", "car", scene, physics, res, hg.Vec3(-10, 1.5, 1000), hg.Vec3(0, 0, 0))
carlights = CarLightsCreate("car", scene)
physics.SceneCreatePhysicsFromAssets(scene)

# Setup 2D rendering to display eyes textures
quad_layout = hg.VertexLayout()
quad_layout.Begin().Add(hg.A_Position, 3, hg.AT_Float).Add(hg.A_TexCoord0, 3, hg.AT_Float).End()

quad_model = hg.CreatePlaneModel(quad_layout, 1, 1, 1, 1)
quad_render_state = hg.ComputeRenderState(hg.BM_Alpha, hg.DT_Disabled, hg.FC_Disabled)

eye_t_size = res_x / 2.5
eye_t_x = (res_x - 2 * eye_t_size) / 6 + eye_t_size / 2
quad_matrix = hg.TransformationMat4(hg.Vec3(0, 0, 0), hg.Vec3(hg.Deg(90), hg.Deg(0), hg.Deg(0)), hg.Vec3(eye_t_size, 1, eye_t_size))

tex0_program = hg.LoadProgramFromAssets("shaders/sprite")

quad_uniform_set_value_list = hg.UniformSetValueList()
quad_uniform_set_value_list.clear()
quad_uniform_set_value_list.push_back(hg.MakeUniformSetValue("color", hg.Vec4(1, 1, 1, 1)))

quad_uniform_set_texture_list = hg.UniformSetTextureList()


# Car camera

car_camera = CarCameraCreate("car", scene)
steering_wheel = scene.GetNode("steering_wheel")
default_camera = scene.GetNode("Camera")
# Inputs

keyboard = hg.Keyboard()
mouse = hg.Mouse()
joystick = hg.Joystick()
hg.ResetClock()

# Main loop

vr_state = None
initial_head_matrix = hg.TransformationMat4(hg.Vec3(0, 0, 0), hg.Vec3(0, 0, 0))
vr_calibrated = False
physics_debug = False
car_debug = False

highway_turn_node = scene.GetNode("block_highway_turn_in")
mesh_col = scene.CreateCollision()
mesh_col.SetType(hg.CT_Mesh)
mesh_col.SetCollisionResource("road_blocks/block_highway_turn_in/block_highway_turn_in_42.physics_bullet")
mesh_col.SetMass(0)
highway_turn_node.SetCollision(0, mesh_col)
# create rigid body
rb = scene.CreateRigidBody()
rb.SetType(hg.RBT_Static)
rb.SetFriction(0.498)
rb.SetRollingFriction(0)
highway_turn_node.SetRigidBody(rb)
physics.NodeCreatePhysicsFromAssets(highway_turn_node)

while not keyboard.Pressed(hg.K_Escape):

	keyboard.Update()
	mouse.Update()
	joystick.Update()

	# for i in range(joystick.ButtonsCount()):
	# 	if joystick.Down(i):
	# 		print(i)

	# for i in range(joystick.AxesCount()):
	# 	print(joystick.Axes(i))

	dt = hg.TickClock()
	dts = hg.time_to_sec_f(dt)


	# Car updates
	brake, reverse = RCCarControl(car, physics, keyboard, dts, steering_wheel, joystick)
	car_vel, car_pos, car_lines = RCCarUpdate(car, scene, physics, dts)
	CarLightsSetBrake(carlights, brake)
	CarLightsSetReverse(carlights, reverse)
	CarLightsUpdate(carlights, scene, dt)
	current_camera_node, camera_update = CarCameraUpdate(car_camera, scene, keyboard, dt, car_vel, render_mode)

	# Scene updates
	vid = 0  # keep track of the next free view id
	passId = hg.SceneForwardPipelinePassViewId()
	hg.SceneUpdateSystems(scene, clocks, dt, physics, hg.time_from_sec_f(1/60), 3)
	if render_mode == "normal":
		vid, passId = hg.SubmitSceneToPipeline(0, scene, hg.IntRect(0, 0, res_x, res_y), True, pipeline, res)

		if physics_debug:
			# Debug physics
			hg.SetViewClear(vid, 0, 0, 1.0, 0)
			hg.SetViewRect(vid, 0, 0, res_x, res_y)
			cam_mat = scene.GetCurrentCamera().GetTransform().GetWorld()
			view_matrix = hg.InverseFast(cam_mat)
			c = scene.GetCurrentCamera().GetCamera()
			projection_matrix = hg.ComputePerspectiveProjectionMatrix(c.GetZNear(), c.GetZFar(), hg.FovToZoomFactor(c.GetFov()), hg.Vec2(res_x / res_y, 1))
			hg.SetViewTransform(vid, view_matrix, projection_matrix)
			rs = hg.ComputeRenderState(hg.BM_Opaque, hg.DT_Disabled, hg.FC_Disabled)
			physics.RenderCollision(vid, vtx_lines, lines_program, rs, 0)

		if car_debug:
			opaque_view_id = hg.GetSceneForwardPipelinePassViewId(passId, hg.SFPP_Opaque)
			for line in car_lines:
				draw_line(line[0], line[1], line[2], opaque_view_id, vtx_line_layout, lines_program)

	# EoF
	if render_mode == "vr":
		main_camera_matrix = scene.GetCurrentCamera().GetTransform().GetWorld()
		if vr_state and not vr_calibrated and not camera_update:
			mat_head = hg.InverseFast(vr_state.body) * vr_state.head
			rot = hg.GetR(mat_head)
			rot.x = 0
			rot.z = 0
			initial_head_matrix = hg.TransformationMat4(hg.GetT(mat_head), rot)
			head_pos = vr_state.head
			vr_calibrated = True
		if camera_update:
			vr_calibrated = False

		actor_body_mtx = main_camera_matrix * hg.InverseFast(initial_head_matrix)

		vr_state = hg.OpenVRGetState(actor_body_mtx, 0.1, 1000)

		left, right = hg.OpenVRStateToViewState(vr_state)

		vid = 0  # keep track of the next free view id
		passId = hg.SceneForwardPipelinePassViewId()

		# Prepare view-independent render data once
		vid, passId = hg.PrepareSceneForwardPipelineCommonRenderData(vid, scene, render_data, pipeline, res, passId)
		vr_eye_rect = hg.IntRect(0, 0, vr_state.width, vr_state.height)

		# Prepare the left eye render data then draw to its framebuffer
		vid, passId = hg.PrepareSceneForwardPipelineViewDependentRenderData(vid, left, scene, render_data, pipeline, res, passId)
		vid, passId = hg.SubmitSceneToForwardPipeline(vid, scene, vr_eye_rect, left, pipeline, render_data, res, vr_left_fb.GetHandle())

		# Prepare the right eye render data then draw to its framebuffer
		vid, passId = hg.PrepareSceneForwardPipelineViewDependentRenderData(vid, right, scene, render_data, pipeline, res, passId)
		vid, passId = hg.SubmitSceneToForwardPipeline(vid, scene, vr_eye_rect, right, pipeline, render_data, res, vr_right_fb.GetHandle())

		# Display the VR eyes texture to the backbuffer
		hg.SetViewRect(vid, 0, 0, res_x, res_y)
		vs = hg.ComputeOrthographicViewState(hg.TranslationMat4(hg.Vec3(0, 0, 0)), res_y, 0.1, 100, hg.ComputeAspectRatioX(res_x, res_y))
		hg.SetViewTransform(vid, vs.view, vs.proj)

		quad_uniform_set_texture_list.clear()
		quad_uniform_set_texture_list.push_back(hg.MakeUniformSetTexture("s_tex", hg.OpenVRGetColorTexture(vr_left_fb), 0))
		hg.SetT(quad_matrix, hg.Vec3(eye_t_x, 0, 1))
		hg.DrawModel(vid, quad_model, tex0_program, quad_uniform_set_value_list, quad_uniform_set_texture_list, quad_matrix, quad_render_state)

		quad_uniform_set_texture_list.clear()
		quad_uniform_set_texture_list.push_back(hg.MakeUniformSetTexture("s_tex", hg.OpenVRGetColorTexture(vr_right_fb), 0))
		hg.SetT(quad_matrix, hg.Vec3(-eye_t_x, 0, 1))
		hg.DrawModel(vid, quad_model, tex0_program, quad_uniform_set_value_list, quad_uniform_set_texture_list, quad_matrix, quad_render_state)


		hg.OpenVRSubmitFrame(vr_left_fb, vr_right_fb)
	
	if render_mode == "normal":
		vid += 1
		physics_debug, car_debug = draw_gui(res_x, res_y, dt, dts, car_vel, vid, physics_debug, car_pos, car_debug)

	hg.Frame()
	hg.UpdateWindow(win)    

hg.RenderShutdown()
hg.DestroyWindow(win)