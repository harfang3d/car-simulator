import harfang as hg
from utils import MetersPerSecondToKMH


def DrawGui(res_x, res_y, dt, dts, car_vel, vid, debug_physic, car_pos, car_mass, debug_car, control_keyboard, road_track):
	hg.ImGuiBeginFrame(res_x, res_y, dt, hg.ReadMouse(), hg.ReadKeyboard())
	hg.ImGuiBegin("Debug", True, hg.ImGuiWindowFlags_NoMove | hg.ImGuiWindowFlags_NoResize)
	hg.ImGuiSetWindowSize("Debug", hg.Vec2(350, 200), hg.ImGuiCond_Once)
	hg.ImGuiText("dt = " + str(round(dts, 4)))
	hg.ImGuiText("car_mass = " + str(car_mass) + "Kg")
	hg.ImGuiText("speed = " + str(round(MetersPerSecondToKMH(hg.Len(car_vel)))) + " km/h")
	hg.ImGuiText("car position = Vec3(" + str(round(car_pos.x, 4)) + ", " + str(round(car_pos.y, 4)) + ", " + str(round(car_pos.z, 4)) + ")")
	was_clicked, debug_physic = hg.ImGuiCheckbox('Physic Debug', debug_physic)
	was_clicked, debug_car = hg.ImGuiCheckbox('Car Debug', debug_car)
	was_clicked, control_keyboard = hg.ImGuiCheckbox('Keyboard Control', control_keyboard)
	was_clicked, road_track = hg.ImGuiCheckbox('Debug Road Tracks', road_track)


	hg.ImGuiEnd()
	hg.ImGuiEndFrame(vid)

	return debug_physic, debug_car, control_keyboard, road_track

def DrawLine(pos_a, pos_b, line_color, vid, vtx_line_layout, line_shader):
	vtx = hg.Vertices(vtx_line_layout, 2)
	vtx.Begin(0).SetPos(pos_a).SetColor0(line_color).End()
	vtx.Begin(1).SetPos(pos_b).SetColor0(line_color).End()
	hg.DrawLines(vid, vtx, line_shader)
