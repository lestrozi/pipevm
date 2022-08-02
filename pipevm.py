#!/usr/bin/env python3

from bitutil import BitStream
from devices import text, graphic, keyboard, pipeos, filesystem
from vm import Vm
import fcntl
import os
import sys

import time

class PipeCmd:
    SPECIAL_CHAR = 0xff
    DEVICE_SELECTOR_CHAR = 0x80

    def __init__(self, vm):
        # TODO: CLI arguments:
        self.byteAligned = True
        self.bitDictionary = None #[48, 49]    # bytes that represent bit-0 and bit-1 respectively
                                    # is ignored if byteAligned = True
        self.filesystemRoot = "/tmp/pipevm/"


        # for now, let all devices share the same outputBuffer
        self.outputBuffer = BitStream()

        self.vm = vm
        filesystemDevice = filesystem.Filesystem(vm, self.outputBuffer, self.byteAligned)
        filesystemDevice.setRoot(self.filesystemRoot)
        self.devices = [
                text.Text(vm, self.outputBuffer, self.byteAligned),
                graphic.Graphic(vm, self.outputBuffer, self.byteAligned),
                keyboard.Keyboard(vm, self.outputBuffer, self.byteAligned),
                pipeos.Os(vm, self.outputBuffer, self.byteAligned),
                filesystemDevice,
        ]
        self.device = self.devices[0]
        self.inputBuffer = BitStream()

        fd = sys.stdin.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        while True:
            # FIXME: improve stdin/out handling loop

            # handle output (devices -> stdout)
            while len(self.outputBuffer) >= 8:
                c = self.outputBuffer.read(8)
                sys.stdout.buffer.raw.write(c.bytes)
                sys.stdout.buffer.raw.flush()

            # handle input (stdin -> devices)
            b = sys.stdin.buffer.raw.read(1)
            if b == b'' or b is None:
                continue
                print("EOF", file=sys.stderr)
                #quit()

            # FIXME
            time.sleep(0.001)

            # if bitDictionary is set, read input bytes as representing an individual bit
            if self.bitDictionary:
                if ord(b) == self.bitDictionary[0]:
                    self.inputBuffer.append(BitStream(bin='0b0'))
                elif ord(b) == self.bitDictionary[1]:
                    self.inputBuffer.append(BitStream(bin='0b1'))
                else:
                    raise Exception(f"Invalid input byte representation of a bit: {ord(b)}")
            else:
                self.inputBuffer.append(BitStream(bytes=b, length=8))

            # wait for at least 1 byte
            if len(self.inputBuffer) < 8:
                continue

            c = self.inputBuffer.peek(8).uint
            if c == self.SPECIAL_CHAR:
                if len(self.inputBuffer) < 16:
                    # wait for next token
                    continue

                c = self.inputBuffer.read(8).uint
                c = self.inputBuffer.read(8).uint
                if c == self.SPECIAL_CHAR:
                    self.device.input(BitStream(uint=c, length=8))
                elif (c >= self.DEVICE_SELECTOR_CHAR
                        and c <= (self.DEVICE_SELECTOR_CHAR + len(self.devices))):
                    deviceNum = c - self.DEVICE_SELECTOR_CHAR
                    print(f"Selecting device {deviceNum}", file=sys.stderr)
                    self.setDevice(deviceNum)
                else:
                    raise Exception(f"Invalid command: {c}")
            else:
                bs = self.inputBuffer.read(8)
                self.device.input(bs)


    def setDevice(self, deviceNum):
        try:
            self.device = self.devices[deviceNum]
        except IndexError:
            raise Exception(f"Invalid device: {deviceNum}")


    def putc(self, c):
        sys.stdout.input(c)
        sys.stdout.flush()


if __name__ == "__main__":
    vm = Vm()
    vm.waitReady()

    PipeCmd(vm)
