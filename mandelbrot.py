import numpy as np
import cv2
import argparse


parser = argparse.ArgumentParser()
parser.add_argument(
    '--N', type=int,
    default=300,
    help='Number of iterations'
)
args = parser.parse_args()


W = 1500
H = 1000

min_x = -2
max_x = 1
min_y = -1
max_y = 1


def create_grid(min_x, max_x, min_y, max_y, W, H):
    xs = np.expand_dims(np.linspace(min_x, max_x, W), axis=0)
    ys = 1j * np.expand_dims(np.linspace(min_y, max_y, H), axis=1)
    return xs + ys


def get_image(ans):
    ans[ans > 0] += np.max(ans) * 0.1
    ans /= np.max(ans)
    return np.repeat(np.expand_dims(ans, 2), 3, axis=2)


def escape(grid, args):
    ans = np.zeros_like(grid, dtype=np.float64)
    z = np.zeros_like(grid)
    valid = np.logical_and(np.abs(z.real) < 2, np.abs(z.imag) < 2)

    for k in range(1, args.N + 1, 1):
        z[valid] = z[valid]**2 + grid[valid]
        new_valid = np.logical_and(np.abs(z.real) < 2, np.abs(z.imag) < 2)
        ans[np.logical_and(valid, np.logical_not(new_valid))] = k
        valid = new_valid

    return get_image(ans)


grid = create_grid(min_x, max_x, min_y, max_y, W, H)
image = escape(grid, args)


drawing = False
ix = iy = 0
def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing
    global min_x, max_x, min_y, max_y
    global image

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
    elif event == cv2.EVENT_LBUTTONUP:
        if x < ix:
            ix, x = x, ix

        ydiff = int((x - ix) * H/W)
        if y < iy:
            ydiff *= -1
        y = iy + ydiff

        if y < iy:
            iy, y = y, iy

        max_x, min_x = x / W * (max_x - min_x) + min_x, ix / W * (max_x - min_x) + min_x
        max_y, min_y = y / H * (max_y - min_y) + min_y, iy / H * (max_y - min_y) + min_y
        grid = create_grid(min_x, max_x, min_y, max_y, W, H)
        image = escape(grid, args)


cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_rectangle)


while True:
    cv2.imshow('image', image)
    k = cv2.waitKey(1) & 0xFF
    if k == ord('b'):
        pass # TODO 'backup'/zoom out
