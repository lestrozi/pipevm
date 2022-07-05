#!/usr/bin/python3

import sys
import struct

w, h = 320, 240

paddle_left_x = 10
paddle_right_x = w - paddle_left_x
paddle_w, paddle_h = 5, 30
paddle_rgb = (254, 254, 254)
ball_x, ball_y = w/2, h/2
ball_w, ball_h = 5, 5
ball_rgb = (254, 254, 0)

paddle_left_y = int(h/2)
paddle_right_y = int(h/2)

class Devices:
    TEXT = 0
    GRAPHIC = 1
    KEYBOARD = 2


def main():
    sys.stdout.buffer.raw.write(switch_device(Devices.GRAPHIC))

    # black screen
    sys.stdout.buffer.raw.write(draw_rectangle(0, 0, w, h, 0, 0, 0))
    # draw left paddle
    sys.stdout.buffer.raw.write(draw_rectangle(paddle_left_x, int(paddle_left_y - paddle_h/2), paddle_w, paddle_h, *paddle_rgb))
    # draw right paddle
    sys.stdout.buffer.raw.write(draw_rectangle(paddle_right_x, int(paddle_right_y - paddle_h/2), paddle_w, paddle_h, *paddle_rgb))
    # draw ball
    sys.stdout.buffer.raw.write(move_ball(0, 0))
    sys.stdout.flush()

    sys.stdout.buffer.raw.write(switch_device(Devices.KEYBOARD))
    moves = 0
    while moves < 20:
        sys.stdout.buffer.raw.write(get_key_pressed())
        sys.stdout.flush()

        v = sys.stdin.buffer.raw.read(1)
        if v == b'\x00':
            continue

        # as a hack to get a time.delay(), the ball only moves when there's a key press
        # also, make it follow the paddle movement
        sys.stdout.buffer.raw.write(switch_device(Devices.GRAPHIC))

        k = sys.stdin.buffer.raw.read(1)
        if k == b'w':
            sys.stdout.buffer.raw.write(move_left_paddle_up(5))
            sys.stdout.buffer.raw.write(move_ball(-5, -5))
        elif k == b's':
            sys.stdout.buffer.raw.write(move_left_paddle_down(5))
            sys.stdout.buffer.raw.write(move_ball(-5, 5))

        sys.stdout.flush()
        sys.stdout.buffer.raw.write(switch_device(Devices.KEYBOARD))

        moves += 1

def text(s):
    return s.encode('latin1')


def switch_device(deviceNum):
    SPECIAL_CHAR = 0xff
    DEVICE_SELECTOR = 0x80
    return struct.pack(">BB", SPECIAL_CHAR, (DEVICE_SELECTOR+deviceNum))
    

def draw_rectangle(x, y, w, h, r, g, b):
    # FIXME: if any parameter is 0xff, they need to be escaped by another 0xff
    command = 5
    return struct.pack(">BHHHHBBB", command, x, y, w, h, r, g, b)

def get_key_pressed():
    command = 1
    return struct.pack(">B", command)

def move_ball(amount_x, amount_y):
    global ball_x, ball_y

    cmd = b''
    # delete current ball
    cmd += draw_rectangle(int(ball_x - ball_w/2), int(ball_y - ball_h/2), ball_w, ball_h, 0, 0, 0)

    ball_x += amount_x
    ball_y += amount_y
    # draw new ball
    cmd += draw_rectangle(int(ball_x - ball_w/2), int(ball_y - ball_h/2), ball_w, ball_h, *ball_rgb)
    return cmd

def move_left_paddle_up(amount):
    global paddle_left_y

    # FIXME
    """
    if y < MIN_Y:
        return 
    """

    cmd = b''
    paddle_left_y = paddle_left_y - amount
    # delete bottom pixels
    cmd += draw_rectangle(paddle_left_x, int(paddle_left_y + paddle_h/2), paddle_w, amount, 0, 0, 0)
    # add top pixels
    cmd += draw_rectangle(paddle_left_x, int(paddle_left_y - paddle_h/2), paddle_w, amount, *paddle_rgb)
    return cmd

def move_left_paddle_down(amount):
    global paddle_left_y

    # FIXME
    """
    if y > MAX_Y
        return 
    """

    cmd = b''
    # delete top pixels
    cmd += draw_rectangle(paddle_left_x, int(paddle_left_y - paddle_h/2), paddle_w, amount, 0, 0, 0)
    # add bottom pixels
    cmd += draw_rectangle(paddle_left_x, int(paddle_left_y + paddle_h/2), paddle_w, amount, *paddle_rgb)
    paddle_left_y = paddle_left_y + amount
    return cmd


if __name__ == "__main__":
    main()
