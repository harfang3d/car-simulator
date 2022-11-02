import harfang as hg
from utils import metersPerSecondToKMH

def draw_gui(res_x, res_y, dt, dts, car_vel, vid, debug_physic, car_pos, debug_car):
	hg.ImGuiBeginFrame(res_x, res_y, dt, hg.ReadMouse(), hg.ReadKeyboard())
	hg.ImGuiBegin("Debug", True, hg.ImGuiWindowFlags_NoMove | hg.ImGuiWindowFlags_NoResize)
	hg.ImGuiSetWindowSize("Debug", hg.Vec2(350, 150), hg.ImGuiCond_Once)
	hg.ImGuiText("dt = " + str(round(dts, 4)))
	hg.ImGuiText("speed = " + str(round(metersPerSecondToKMH(hg.Len(car_vel)))) + " km/h")
	hg.ImGuiText("car position = Vec3(" + str(round(car_pos.x, 4)) + ", " + str(round(car_pos.y, 4)) + ", " + str(round(car_pos.z, 4)) + ")")
	was_clicked, debug_physic = hg.ImGuiCheckbox('Physic Debug', debug_physic)
	was_clicked, debug_car = hg.ImGuiCheckbox('Car Debug', debug_car)

	hg.ImGuiEnd()
	hg.ImGuiEndFrame(vid)

	return debug_physic, debug_car

def draw_line(pos_a, pos_b, line_color, vid, vtx_line_layout, line_shader):
	vtx = hg.Vertices(vtx_line_layout, 2)
	vtx.Begin(0).SetPos(pos_a).SetColor0(line_color).End()
	vtx.Begin(1).SetPos(pos_b).SetColor0(line_color).End()
	hg.DrawLines(vid, vtx, line_shader)