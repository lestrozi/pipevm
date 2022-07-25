# pipevm
PipeVM is a binary protocol - and a Python implementation - of a Virtual Machine that can be controlled via stdin/stdout.

It was heavily inspired by discussion in https://github.com/tomhea/flip-jump/discussions/154 about how to extend the capabilities of programming languages with limited I/O implementation (as most esolangs, for example, that can only read bytes from stdin and write bytes to stdout).

# Devices
This is a prototype implements 5 devices:
[a relative link](other_file.md)
  * [devices/text.py](devices/text.py) - ASCII console with auto-scroll
  * [devices/graphic.py](devices/graphic.py) - 320x240 24-bits RGB graphic screen
  * [devices/keyboard.py](devices/keyboard.py) - A keyboard that can wait for a char (blocking) or return which key is pressed (non-blocking)
  * [devices/pipeos.py](devices/pipeos.py) - Miscellaneous methods, like a pseudorandom number generator; this probably won't exist in the final version
  * [devices/filesystem.py](devices/filesystem.py) - Interface to a real filesystem (chrooted), supporting ls, stat, read, write, mkdir, rm

# Demo
To demonstrate how it can be used, there are two main demos in the tests/ folder:

## [tests/bfponggen.py](tests/bfponggen.py)
A (graphical) Pong implementation in brainfuck (the script is python because it's used to generate the brainfuck code)

![pong prototype in brainfuck](demos/pong.gif?raw=true "Pong prototype in Brainfuck")


## [tests/sh.bf](tests/sh.bf)
A basic UNIX shell implementation with ls, echo (including redirecting output to a file), mkdir, rm and cat

![UNIX Shell prototype in brainfuck](demos/shell.gif?raw=true "UNIX Shell prototype in Brainfuck")


## Running

To run the demos, you need to create a FIFO:

`$ ff="/tmp/ff"; [ ! -p "$ff" ] && mkfifo "$ff";`

And then execute the compiled (or interpreted) code like:

`$ <"$ff" ./pipevm.py | /tmp/your_program >"$ff"`

There are probably ways to make this work on Windows, but I haven't tried.
Keep in mind that your program must output raw bytes, not UTF-8 encoded strings (unless you pipe it through `iconv -f utf-8 -t latin1`, but I wouldn't recommend that).


# Sample usage
Other than the demos above, simply writing to pipevm stdin can be used to see how it works.

The echoed string can be cut short at any point (better results if it's before `\xff\x80` or `\xff\x81`) to see partial examples

```
$ echo -ne "text\xff\x81\x05\x00\x0a\x00\x32\x00\x05\x00\x1e\x70\x80\x90\xff\x80\xff\xff\x00hi\xff\x81\x00" | stdbuf -i0 -o0 -e0 python3 pipevm.py
            ^^^^ print "text" in text mode
                ^^^^^^^^ special char (switches to "command mode") followed by command 0x81, which switches device to device=1 (graphic screen)
                        ^^^^ operation 5 (draw rectangle)
                            ^^^^^^^^ 16 bits x (10)
                                    ^^^^^^^^ 16 bits y (50)
                                            ^^^^^^^^ 16 bits w (5)
                                                    ^^^^^^^^ 16 bits h (30)
                                                            ^^^^^^^^^^^^ 24 bits rgb (#708090)
                                                                        ^^^^^^^^ switches back to device=0 (text)
										^^^^^^^^ send 0xff to text device (puts it in "command mode")
										        ^^^^ send commmand 0x00 (clear screen)
										            ^^ write "hi"
										              ^^^^^^^^ switches to device=1 (graphic screen)
										                      ^^^ refresh
```
