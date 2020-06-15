# raycasting.py

import os, time, math, curses

SCREEN_WIDTH, SCREEN_HEIGHT = os.get_terminal_size()# 120, 40
FOV = 60
player_x, player_y, player_angle = 2, 2, 90
MOVEMENT, ROTATION = 0.3, 5.0
PRECISION = 64
INCREMENT_ANGLE = FOV / SCREEN_WIDTH

COLOR = "\033[48;5;{}m{}\033[0m"

screen = []
for _ in range(SCREEN_HEIGHT):
	row = []
	for _ in range(SCREEN_WIDTH):
		row.append("")
	screen.append(row)

map_ = [
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[1,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1],
[1,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1],
[1,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1],
[1,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1],
[1,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1],
[1,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1],
[1,0,0,0,0,1,1,1,1,0,0,0,0,0,0,1],
[1,0,0,0,0,1,0,0,1,1,0,0,0,0,0,1],
[1,0,0,0,0,1,1,0,1,1,0,0,0,0,0,1],
[1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1],
[1,0,0,0,0,0,1,1,1,1,0,0,0,0,0,1],
[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
[1,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1],
[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

radian_conversion = lambda degree: degree * math.pi / 180


""" github.com/encukou/bresenham/blob/master/bresenham.py """
def draw_line(x0, y0, x1, y1, char = "*"):
	global screen
	def bresenham(x0, y0, x1, y1):
		dx, dy = x1 - x0, y1 - y0
		xsign = 1 if dx > 0 else -1
		ysign = 1 if dy > 0 else -1
		dx, dy = abs(dx), abs(dy)
		if dx > dy: xx, xy, yx, yy = xsign, 0, 0, ysign
		else:
			dx, dy = dy, dx
			xx, xy, yx, yy = 0, ysign, xsign, 0
		D, y = 2 * dy - dx, 0
		for x in range(dx + 1):
			yield x0 + x * xx + y * yx, y0 + x * xy + y * yy
			if D >= 0:
				y += 1
				D -= 2 * dx
			D += 2 * dy
	for x, y in list(bresenham(x0, y0, x1, y1)):
		try:
			screen[y - 1][x - 1] = char
		except IndexError:
			return

def get_char(stdscr):
    stdscr.nodelay(True)
    stdscr.refresh()
    char_num = stdscr.getch()
    if char_num != -1:
        return chr(char_num)

def print_screen():
	for row in screen:
		for char in row:
			print(char, end = "")
		print()

def manage_input(inp):
	global player_x, player_y, player_angle
	if inp == "w":
		player_cos = math.cos(radian_conversion(player_angle)) * MOVEMENT
		player_sin = math.sin(radian_conversion(player_angle)) * MOVEMENT
		new_x, new_y = player_x + player_cos, player_y + player_sin

		if map_[int(new_y)][int(new_x)] == 0:  # collision test
			player_x, player_y = new_x, new_y

	elif inp == "a": player_angle -= ROTATION

	elif inp == "s":
		player_cos = math.cos(radian_conversion(player_angle)) * MOVEMENT
		player_sin = math.sin(radian_conversion(player_angle)) * MOVEMENT
		new_x, new_y = player_x - player_cos, player_y - player_sin

		if map_[int(new_y)][int(new_x)] == 0:
			player_x, player_y = new_x, new_y

	elif inp == "d": player_angle += ROTATION

def raycasting():
	ray_angle = player_angle - (FOV / 2)

	for ray_count in range(SCREEN_WIDTH):
		ray = {"x": player_x, "y": player_y}
		ray_cos = math.cos(radian_conversion(ray_angle)) / PRECISION
		ray_sin = math.sin(radian_conversion(ray_angle)) / PRECISION 

		wall = 0
		while wall == 0:
			ray["x"] += ray_cos
			ray["y"] += ray_sin
			wall = map_[int(ray["y"])][int(ray["x"])]

		distance = math.sqrt(pow(player_x - ray["x"], 2)) + pow(player_y - ray["y"], 2)
		distance *= math.cos(radian_conversion(ray_angle - player_angle))

		wall_height = (SCREEN_HEIGHT / 2) // distance

		"""
		m = int(SCREEN_HEIGHT / 2 - wall_height)
		open("log_file.txt", "a").write(str(m) + "\n")
		wall_color_amt = int(SCREEN_HEIGHT / 2 - wall_height)
		if wall_color_amt in range(16, 17):
			ceiling_color = 40
		elif wall_color_amt in range(18, 19):
			ceiling_color = 41
		elif wall_color_amt == 20:
			ceiling_color = 42
		else:
			ceiling_color = 43
		"""

		draw_line(ray_count, 0, ray_count, int(SCREEN_HEIGHT / 2 - wall_height), COLOR.format(210, " "))
		draw_line(ray_count, int(SCREEN_HEIGHT / 2 - wall_height), ray_count, int(SCREEN_HEIGHT / 2 + wall_height), COLOR.format(40, " "))
		draw_line(ray_count, int(SCREEN_HEIGHT / 2 + wall_height), ray_count, SCREEN_HEIGHT, COLOR.format(45, " "))

		ray_angle += INCREMENT_ANGLE


def main():
	while True:
		print_screen()
		manage_input(curses.wrapper(get_char))
		raycasting()
		time.sleep(0.1)
		os.system("printf '\033c'")

if __name__ == "__main__":
	main()
