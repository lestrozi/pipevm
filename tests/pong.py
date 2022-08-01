#!/usr/bin/env python3

import sys
import struct

w, h = 320, 240

paddle_left_x = 10
paddle_right_x = w - paddle_left_x
paddle_w, paddle_h = 5, 30
paddle_rgb = (254, 254, 254)
paddle_movement = 10
ball_x, ball_y = int(w/2), int(h/2)
ball_w, ball_h = 5, 5
ball_rgb = (254, 254, 0)
ball_movement = 5
ball_direction_x, ball_direction_y = -1, -1
min_x, max_x = 10, w - 10
min_y, max_y = 10, h - 10

paddle_left_y = int(h/2)
paddle_right_y = int(h/2)

class Devices:
    TEXT = 0
    GRAPHIC = 1
    KEYBOARD = 2
    OS = 3


def main():
    global ball_x, ball_y, ball_direction_x, ball_direction_y

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

    moves = 0
    sys.stdout.buffer.raw.write(switch_device(Devices.GRAPHIC))
    while moves < 100:
        # device = GRAPHIC

        if check_ball_should_restart():
            # delete ball
            sys.stdout.buffer.raw.write(draw_ball(ball_x, ball_y, (0, 0, 0)))
            ball_x, ball_y = int(w/2), int(h/2)

            sys.stdout.buffer.raw.write(switch_device(Devices.OS))
            sys.stdout.buffer.raw.write(get_random(1))
            sys.stdout.flush()
            c = sys.stdin.buffer.raw.read(1)
            ball_direction_x *= -(2 * (c[0] & 0x01) - 1)
            ball_direction_y *= -((c[0] & 0x02) - 1)
            sys.stdout.buffer.raw.write(switch_device(Devices.GRAPHIC))

        # computer movement
        if ball_direction_x > 0 and paddle_right_y > ball_y:
            sys.stdout.buffer.raw.write(move_right_paddle_up())
        elif ball_direction_x > 0 and paddle_right_y < ball_y:
            sys.stdout.buffer.raw.write(move_right_paddle_down())

        sys.stdout.buffer.raw.write(move_ball(ball_movement*ball_direction_x, ball_movement*ball_direction_y))
        sys.stdout.buffer.raw.write(move_ball(ball_movement*ball_direction_x, ball_movement*ball_direction_y))

        sys.stdout.buffer.raw.write(switch_device(Devices.OS))
        sys.stdout.buffer.raw.write(delay_ms(10))
        sys.stdout.flush()
        # wait delay
        sys.stdin.buffer.raw.read(1)

        sys.stdout.buffer.raw.write(switch_device(Devices.KEYBOARD))
        sys.stdout.buffer.raw.write(get_key_pressed())
        sys.stdout.flush()

        v = sys.stdin.buffer.raw.read(1)
        if v == b'\x00':
            sys.stdout.buffer.raw.write(switch_device(Devices.GRAPHIC))
            continue

        k = sys.stdin.buffer.raw.read(1)

        sys.stdout.buffer.raw.write(switch_device(Devices.GRAPHIC))
        if k == b'w':
            sys.stdout.buffer.raw.write(move_left_paddle_up())
        elif k == b's':
            sys.stdout.buffer.raw.write(move_left_paddle_down())

        sys.stdout.flush()

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

def delay_ms(n):
    command = 0
    return struct.pack(">BH", command, n)

def get_random(n):
    command = 1
    return struct.pack(">BB", command, n)

def draw_ball(x, y, rgb):
    return draw_rectangle(int(x - ball_w/2), int(y - ball_h/2), ball_w, ball_h, *rgb)

def move_ball(amount_x, amount_y):
    global ball_x, ball_y

    cmd = b''
    # delete current ball
    cmd += draw_ball(ball_x, ball_y, (0, 0, 0))

    ball_x += amount_x
    ball_y += amount_y
    # draw new ball
    cmd += draw_ball(ball_x, ball_y, ball_rgb)
    return cmd

def move_paddle(paddle_x, paddle_y, direction_up):
    d = 1 if direction_up else -1;

    # delete top pixels
    cmd = draw_rectangle(paddle_x, int(paddle_y + d*paddle_h/2), paddle_w, paddle_movement, 0, 0, 0)
    # add top pixels
    cmd += draw_rectangle(paddle_x, int(paddle_y - d*paddle_h/2), paddle_w, paddle_movement, *paddle_rgb)

    return cmd

def move_left_paddle_up():
    global paddle_left_y

    if paddle_left_y - paddle_h/2 <= min_y:
        return b''

    paddle_left_y = paddle_left_y - paddle_movement
    return move_paddle(paddle_left_x, paddle_left_y, True)

def move_left_paddle_down():
    global paddle_left_y

    if paddle_left_y + paddle_h/2 >= max_y:
        return b''

    cmd = move_paddle(paddle_left_x, paddle_left_y, False)
    paddle_left_y = paddle_left_y + paddle_movement
    return cmd

def move_right_paddle_up():
    global paddle_right_y

    if paddle_right_y - paddle_h/2 <= min_y:
        return b''

    paddle_right_y = paddle_right_y - paddle_movement
    return move_paddle(paddle_right_x, paddle_right_y, True)

def move_right_paddle_down():
    global paddle_right_y

    if paddle_right_y + paddle_h/2 >= max_y:
        return b''

    cmd = move_paddle(paddle_right_x, paddle_right_y, False)
    paddle_right_y = paddle_right_y + paddle_movement
    return cmd

def check_ball_should_restart():
    global ball_direction_x, ball_direction_y

    if ball_x <= paddle_left_x:
        if ball_y > paddle_left_y - paddle_h/2 and ball_y < paddle_left_y + paddle_h/2:
            ball_direction_x *= -1
        else:
            return True

    if ball_x >= paddle_right_x:
        if ball_y > paddle_right_y - paddle_h/2 and ball_y < paddle_right_y + paddle_h/2:
            ball_direction_x *= -1
        else:
            return True

    if ball_y <= min_y or ball_y >= max_y:
        ball_direction_y *= -1

    return False

if __name__ == "__main__":
    main()
