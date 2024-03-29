# pongff="/tmp/pongff"; [ ! -p "$pongff" ] && mkfifo "$pongff";
# rm -f /tmp/p; python3 bfponggen.py >/tmp/p.bf && python2.7 ~/bfc.py /tmp/p.bf && <"$pongff" ../pipevm.py | /tmp/p >"$pongff"

import struct

class BfGen():
    def __init__(self, generators):
        self.labels = {}
        for i in range(len(generators)):
            self.labels[generators[i][0]] = i
            print(generators[i][1])

        print()

        self.curPos = len(generators) - 9   # FIXME

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
        ('paddle_right_y', ">>+>+>+[+>++[-<+++>]<<]>-[-<+<+>>]"),   # 103
        ('paddle_left_y', ""),                                      # 103
        ('ball_x0', ""),                                            # 0
        ('ball_x1', ">+>+>+++[+>+[-<++++>]<<]>>"),                  # 158
        ('ball_y0', ">"),                                           # 0
        ('ball_y1', ">+++++++++[<+++++++++++++>-]"),                # 117
        ('ff', ">+>+>+>+[++>[-<++++>]<<]>[-<+>]"),                  # 255
        ('device', "++++[>++++<-]>[<++++++++>-]<+>"),               # 129
        ('f0', ">+>+>+>+[++>+[-<+++>]<<]>[-<+>]"),                  # 240
        ('ball_direction_x', ""),                                   # 0 (left)
        ('ball_direction_y', ">"),                                  # 0 (top)
        ('mem0', ""),                                               # 0
        ('mem1', ""),                                               # 0
        ('mem2', ""),                                               # 0
        ('mem3', ""),                                               # 0
        ('mem4', ""),                                               # 0
        ('mem5', ""),                                               # 0
        ('mem6', ""),                                               # 0
        ('mem7', ""),                                               # 0
]

bfgen = BfGen(generators)

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
bfgen.output("ball_direction_x[-mem0+mem1+ball_direction_x]mem1[-ball_direction_x+mem1]+ball_x1-----[-mem0+ball_x1]mem0+++[mem1-]>")
bfgen.output("[ball_y0+ball_x0[-ball_y0-ball_x0]ball_y0[-ball_x0+ball_y0]ball_x1+ball_x0[mem0+++++ball_x1-]>")
bfgen.output("[mem0-----ball_x1-ball_y0]mem1-mem2]")
bfgen.output("mem0---[-ball_x1+mem0]")

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

# check ball boundaries
# mem0 = ball_x0-ball_x1, using ball_y0 as a buffer
print("start boundaries check")
bfgen.output("ball_x0[-ball_y0+mem1+ball_x0]ball_y0[-ball_x0+ball_y0]")
bfgen.output("ball_x1[-ball_y0+mem5+ball_x1]ball_y0[-ball_x1+ball_y0]")
bfgen.output("mem1+mem5[-mem6+mem7+mem5]mem6[-mem3+mem6]")
print("check left boundary")
# if mem0 == 13, reached left boundary
bfgen.output("mem4+mem3-------------[mem4-]>")

# algorithm (done in debugger, not converted here) to
# bounce the ball if it hits the paddle or to reset
# ball_x and ball_y to the center otherwise
print("""
[
  -
  copy ball_y to mem3 and paddle_left_y to mem4
  <<<<<<<<<<[-<+>>>>>>>>>>+<<<<<<<<<]<[->+<]
  <<<[->>>+>>>>>>>>>>>+<<<<<<<<<<<<<<]>>>[-<<<+>>>]
  >>>>>>>>>>
  if mem3 ge mem4
  [->-[>]<<]<  (mem3 ends up = mem4 minus men3)
  [
    then if mem3 ge 31
    >>>>+++++[<++++++>-]<+
    <[->-[>]<<]<
    [then just clean up ->]<
    [else set mem0=1 ><<+>-]>
  ]
  >>[-]<<<[-]+<
  if mem0 eq 1 (ball hit left paddle)
  [
    then change direction of the ball
    <<++++++++++>>-
    >-]>

  [< else reset ball_y
    >>[-]>>[-]<<<<
    <<<<<<[-]<<[-]
    +>+++[++>++[-<++++++>]<<]>      117
    [->+>+<<]
    <++++++++++[->++++<]>+>[-<+>]   158

    request a random char (ff 03 01 01 ff 01)
    >>.>++.>>[-]+..<<<.>--.
    >>->[-]>+>[-]>+>[-]>+>>
    read random char (mem6) and set mem1 and mem2 to (mem6 % 4) (in binary)
    ,[
      -
      <<<<
      [-[<[-<->]<[->+<]+>>-->]>>[-]]<[<]>[-]<<++
      >>+>>
    ]<<-<<-<<->>
    set the ball (x and y) directions based on mem1 and mem2
    [-<<<++++++++++>>>]<[-<<<++++++++++>>>]
    >
  ]
  >>>
]
<<[-]<<[-]<
""")

bfgen.curPos = bfgen.labels["mem0"]

# now repeat the check for mem0 = 47 (+256=303) (reached right boundary)
bfgen.output("mem7[-mem0+mem7]")
bfgen.output("mem1+mem0-----------------------------------------------[mem1-]>")
bfgen.output("[ball_direction_x----------mem1-mem2]mem0[-]")
bfgen.output("mem1[-]mem2[-]mem3[-]")
print("end boundaries check")

# draw new ball
bfgen.output("05.ball_x0.ball_x1.ball_y0.ball_y1.00.05.00.05.f0.f0.00.")

print("move right paddle (computer)")
# move paddle_right_x
bfgen.output("mem0+ball_direction_x[")  # if ball_direction_x != 0

bfgen.output("05.01.paddle_right_x.00.paddle_right_y.00.05.00.paddle_size.00.00.00.")

# use ball_y0 as buffer to copy ball_y1 to mem2 and paddle_right_y to mem3
bfgen.output("ball_y1[-ball_y0+mem2+ball_y1]ball_y0[-ball_y1+ball_y0]")
bfgen.output("paddle_right_y[-ball_y0+mem3+paddle_right_y]ball_y0[-paddle_right_y+ball_y0]")
# compare mem2 and mem3
bfgen.output("mem5+mem3+++++++++++++++mem2[-mem3-[mem4]mem2]mem5")
bfgen.curPos = bfgen.labels["mem4"]
bfgen.output("[-")
# mem2 >= mem3
bfgen.output("paddle_right_x-----mem3")  # must be 1 position before paddle_right_y
bfgen.curPos = bfgen.labels["mem4"]

bfgen.output("]mem5")

# mem2 < mem3
bfgen.output("[-")
bfgen.output("paddle_right_y+++++mem5")

bfgen.output("]mem3[-]mem2[-]")

bfgen.output("05.01.paddle_right_x.00.paddle_right_y.00.05.00.paddle_size.f0.f0.f0.")
bfgen.output("mem0-ball_direction_x[mem1+ball_direction_x-]")
bfgen.output("]mem1[ball_direction_x+mem1-]mem0[-]")

print("move left paddle (user input)")
bfgen.output("ff.device+.-01.")  # ff 02 01 (ff device command)
bfgen.output("mem0,")  # read char
bfgen.output("mem0[,mem2+mem3+mem4+++[mem5[-mem4++++++mem5]mem3]") # if mem0 != 0, read another char and generate 115 ('s')
bfgen.curPos = bfgen.labels["mem1"]
bfgen.output("mem2[-mem0-mem2]mem1+mem0")
bfgen.output("[----[>-]mem1[mem3+++++mem5+mem1-mem2]mem1[-]]")
bfgen.output("mem2[mem5+++++>+<mem2->]mem0[-]]")

bfgen.output("ff.device.")

bfgen.output("mem5[05.00.05.00.paddle_left_y.00.05.00.paddle_size.00.00.00.mem5[-]]") # delete left paddle
bfgen.output("mem3[-paddle_left_y-mem2+mem3]")   # paddle_left_y += mem3, set mem2
bfgen.output("mem4[-paddle_left_y+mem2+mem4]")   # paddle_left_y -= mem4, set mem2
bfgen.output("mem2[05.00.05.00.paddle_left_y.00.05.00.paddle_size.f0.f0.f0.mem2[-]]") # redraw left paddle

# draw right paddle
bfgen.output("05.01.paddle_right_x.00.paddle_right_y.00.05.00.paddle_size.f0.f0.f0.")

# return to initial position of the loop
bfgen.output("05")

bfgen.output("]")
