# pipevm
A virtual machine controlled via stdin/stdout

Heavily inspired by discussion in https://github.com/tomhea/flip-jump/discussions/154

# Why?
Controlling a virtual machine that can have devices attached to it (such as a screen, keyboard, etc.) via stdin/stdout allows extending I/O capabilities of any program that can output bytes (or bits, see below) to graphic mode, accessing file system, sockets, etc.

# But why?
This all started in the discussion mentioned above, thinking about how an esolang only capable of outputing bytes could run PONG, for instance.
This project aims to allow that and more.

# Bits?
(TBD) pipevm also allows input and output as bits if bitDictionary flag is set and 2 int values are specified, representing respectively which byte is 0 and which byte is 1 (default 48 ('0') and 49 ('1'))

# Sample usage
The echoed string can be cut short at any point (better results if it's before `\xff\x80` or `\xff\x81`) to see partial examples

```
$ echo -ne "text\xff\x81\x05\x00\x0a\x00\x32\x00\x05\x00\x1e\x70\x80\x90\xff\x80\xff\xff\x00hi\xff\x81\00" | stdbuf -i0 -o0 -e0 python3 pipevm.py
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
