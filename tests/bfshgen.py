"""
* invalid commands have undefined behavior
* errors aren't handled (e.g. trying to delete a non-existing file)

echo [word]             print word
echo [word] >[path]     print word to file
ls [path]               list files/dirs
mkdir [path]            mkdir path
rm [path]               remove file or empty dir
cat [path]              cat file
#anything               comment (TODO)

in reality, only the first letter is checked, so
"mkdir FOO" is equivalent to "monkeyFOO" for example
"""

import struct

class BfGen():
    def __init__(self, generators):
        self.labels = {}
        for i in range(len(generators)):
            self.labels[generators[i][0]] = i
            print(generators[i][1])

        print()

        self.curPos = len(generators) - 1

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
        ('00', ""),                                                	# 0
        ('ff', ">+>+>+>+[++>[-<++++>]<<]>>"),                       # 255
        ('device', ">+>+[+>++[-<+++++++>]<<]>[-<+>]"),              # 128
        ('01', "+>"),                           					# 01
        ('0A', "++++++++++>"),                           			# 10
        ('space', ">>++++++++[<++++<++++>>-]"),                     # 32
        ('$', "<++++"),                                         	# 36
]

bfgen = BfGen(generators)

print("""
>+sentinel
>invalid command
>rm
>mkdir
>ls
>echo
>cat

+[
    print prompt
    <<<<<<<[<]
    >.>.
    >>.>>.<.

    return to where we were before printing prompt
    [>]>>>>>
    read chars until char 10 (enter) is pressed
    [[<]<<<<<[<]>.>++.--<<.>[>]>>>>>[>],[<]<<<<<[<]>.>.[>]>>>>>[>]<.----------]

    <[<]++++++++[>+++++++++++<-]>
    [->-<]
    >[--[-------[-[-----[<]<]<]<]<]<+
    <-[+<-]

    invalid >[-<<[->+>+<<]>[-<+>>+<]>---.+++++++++++++..[-]++++++++++.[-]]
    rm      >[- switch to filesystem device & request rm and path <<<<<[<]>.>++++.---->++++.----[>]>>>>>>>>>>[++++++++++.>].
                return cleaning <[[-]<]
                switch back to text device <<<<<<<<[<]>.>.[>]
                return to position >>
                read result and ignore ,[-]
             ]
    mkdir   >[- switch to filesystem device & request mkdir and path <<<<<[<]>.>++++.---->+++.---[>]>>>>>>>>>>>>>[++++++++++.>].
                return cleaning <[[-]<]
                switch back to text device <<<<<<<<[<]>.>.[>]
                return to position >>>
                read result and ignore ,[-]
             ]
    ls      >[- switch to filesystem device & request ls and path <<<<<[<]>.>++++.----<<.>[>]>>>>>>>>>>[++++++++++.>].
               zero path <[[-]<]
               switch back to text device <<<<<<<<[<]>.>.[>]
               sentinel+>>>>
               read zero terminated paths returned ,[
                 [>,]<[<]>
                 read next path
                 >[>]>>>,
               ]
               return to sentinel -[+<-]+>

               stat and print paths
               >>>[
                   <<<
                   switch to filesystem device & request stat
                   generate 255-.
                   generate 132-[-->-<]>+++.>+.->[.>].<[<]
                   switch back to text device -.+<----.[-]<
                   read first byte of stat (isDir) ,[--->]>>>[<]<++++++++++[->+<<+++++++>]
                   print isDir <.[-]>
                   generate and print space ++++[-<++++++++>]<.>
                   read and ignore higher bytes of size ,,,
                   read lowest byte of size and treat it as a single decimal digit ,>[-<+++++>]<--print it.[-]
                   print space <.[-]>>>
                   [.>]> newline++++++++++.[-]>>
               ]
               return to sentinel zeroing cells -[[-]<-]+
               return to initial position
               ->>>>
            ]
    echo    >[>>>[>]>sentinel+++++[-<++++>]<++[<]>>>>[>----------------------]>
              [
                found another space assume it's followed by a lessthan symbol [-]
                >[>]<zero the sentinel[-]
                switch to filesystem device & request write
                generate 255>-.
                generate 132-[-->-<]>+++.<+++.--->[-]
                <<shift filename right <[[->+<]<]
                count and send writeLength<< [[->>+<<]>[-<+>]<+<]...>----.>>[>]>
                print filename [++++++++++.>].
                <[[-]<]<[<]<[-]
                >>[>]>
              ]
              <[-]<[<]>>>>>[++++++++++++++++++++++++++++++++.>]<[[-]<]
              return to known position -[+<-]
            ]
    cat     >[- switch to filesystem device & request read and path <<<<<<<[<]>.>++++.---->+.---........++[>]>>>>>>>>>>>[++++++++++.>].
                return cleaning <[[-]<]
                switch back to text device <<<<<<<<[<]>.>.[>]
                return to position >>>>>>
                while result print ,[.,] print newline ++++++++++.[-]
             ]
    >[-]

    reset sentinel <<<<<<<+>>>>>>
    +
]
""")
