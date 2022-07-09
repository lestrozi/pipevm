from pong import draw_rectangle, move_ball
import struct

class BfGen():
    def __init__(self, generators):
        self.labels = {}
        for i in range(len(generators)):
            self.labels[generators[i][0]] = i
            print(generators[i][1])

        print()

        self.curPos = len(generators) - 6   # FIXME

    def moveToPos(self, goalPos):
        d = self.curPos - goalPos
        self.curPos -= d

        if d >= 0:
            return "<" * d

        return ">" * -d

    def output(self, s):
        result = ""
        label = ""

        for c in s:
            if c in '[]<>{}+-.,':
                if label:
                    label = label.strip()
                    v = self.moveToPos(self.labels[label])
                    result += v
                    label = ""
                result += c
            else:
                label += c
        
        if label:
            label = label.strip()
            v = self.moveToPos(self.labels[label])
            result += v

        print(result)


generators = [
        ('00', ">"),                                                # 0
        ('01', "+>"),                                               # 1
        ('05', "+++++>"),                                           # 5
        ('paddle_size', ">+++++[<++++++>-]"),                       # 30
        ('paddle_right_x', ">++++++++[<++++++++>-]"),               # 64
        ('paddle_left_y', ">>+>+>+[>+[-<++++>]<<]>[-<+<+>>]"),      # 105
        ('paddle_right_y', ""),                                     # 105
        ('ball_x0', ""),                                            # 0
        ('ball_x1', ">+>+>+>+[>+[-<+++>]<<]>>"),                    # 160
        ('ball_y0', ">"),                                           # 0
        ('ball_y1', ">+++++++++[<+++++++++++++>-]"),                # 117
        ('ff', ">+>+>+>+[++>[-<++++>]<<]>[-<+>]"),                  # 255
        ('device', "++++[>++++<-]>[<++++++++>-]<+>"),               # 129
        ('f0', ">+>+>+>+[++>+[-<+++>]<<]>[-<+>]"),                  # 240
        ('ball_direction_x', ""),                                   # 0 (left)
        ('ball_direction_y', ""),                                   # 0 (top)
        ('mem0', ""),                                               # 0
        ('mem1', ""),                                               # 0
        ('mem2', ""),                                               # 0
        ('mem3', ""),                                               # 0
]

bfgen = BfGen(generators)

paddle_w, paddle_h = 5, 30
paddle_left_x = 5
#paddle_left_y = int(h/2)
paddle_right_x = 4 # mem index
#paddle_right_y = int(h/2)
paddle_rgb = (240, 240, 240)

ball_x, ball_y = 8, 10	# mem index
ball_w, ball_h = 5, 5
ball_rgb = (240, 240, 0)

bfgen.output("ff.device.")

# black screen  # struct.pack(">BHHHHBBB", command, x, y, w, h, r, g, b)
# paddle_right_x starts with [320 (width) - 256 (overflow)], but will later have 10 subtracted from it
bfgen.output("05.00.00.00.00.01.paddle_right_x.00.f0.00.00.00.")

# we don't need to save "320" anymore, decrease by 10 so it can be used as paddle_right_x
bfgen.output("paddle_right_x----------")

# draw left paddle
bfgen.output("05.00.05.00.paddle_left_y.00.05.00.paddle_size.f0.f0.f0.")

# draw right paddle
bfgen.output("05.01.paddle_right_x.00.paddle_right_y.00.05.00.paddle_size.f0.f0.f0.")

bfgen.output("05")

bfgen.output("[")   # main loop [

# delete ball
bfgen.output("05.ball_x0.ball_x1.ball_y0.ball_y1.00.05.00.05.00.00.00.")

# moves ball_x, handling over/underflow
bfgen.output("ball_direction_x[-mem0+mem1+ball_direction_x]mem1[-ball_direction_x+mem1]+ball_x1-----[-mem0+ball_x1]mem0[mem1-]mem2")
bfgen.curPos = bfgen.labels["mem1"]
bfgen.output("[ball_y0+ball_x0[-ball_y0-ball_x0]ball_y0[-ball_x0+ball_y0]ball_x1+ball_x0[mem1+++++++[-mem0++++++++mem1]+mem0+ball_x1-]ball_y0")
bfgen.curPos = bfgen.labels["ball_x1"]
bfgen.output("[mem0------ball_x1-ball_y0]mem1-mem2]")
bfgen.output("mem0[-ball_x1+mem0]")

bfgen.output("ball_direction_y[-mem0+ball_y1+ball_direction_y]mem0[-ball_direction_y+mem0]ball_y1-----")

# reverse direction of ball_y if ball_y1 == 2
bfgen.output("ball_y1[-mem0+mem2+ball_y1]mem1+")
bfgen.output("mem2--[mem1-mem2[-]]")
bfgen.output("mem1[-ball_direction_y++++++++++mem1]")
bfgen.output("mem0[-ball_y1+mem0]")

# reverse direction of ball_y if ball_y1 == 237
bfgen.output("ball_y1[-mem0+mem2+ball_y1]mem1+")
bfgen.output("mem2+++++++++++++++++++[mem1-mem2[-]]")
bfgen.output("mem1[-ball_direction_y----------mem1]")
bfgen.output("mem0[-ball_y1+mem0]")

bfgen.output("05.ball_x0.ball_x1.ball_y0.ball_y1.00.05.00.05.f0.f0.00.")

# return to initial position of the loop
bfgen.output("05")

bfgen.output("]")
