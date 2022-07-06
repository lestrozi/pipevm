import os
import time
import sys
sys.path.append('..')   # ugh
from bitutil import BitStream
from devices import Device

class Os(Device):
    class Commands:
        DELAY_MS = 0
        RANDOM = 1

    def consumeInput(self):
        # wait for at least 1 byte
        if len(self.inputBuffer) < 8:
            return

        # TODO: allow non-byte-aligned commands
        c = self.inputBuffer.peek(8).uint
        if c == self.Commands.DELAY_MS:
            if len(self.inputBuffer) < 24:
                return

            self.inputBuffer.read(8).uint
            n = self.inputBuffer.read(16).uint

            time.sleep(n/1000)

            self.output(BitStream('0x00'))
        elif c == self.Commands.RANDOM:
            if len(self.inputBuffer) < 16:
                return

            self.inputBuffer.read(8).uint
            n = self.inputBuffer.read(8).uint

            # generate n pseudorandom number
            r = os.urandom(n)
            self.output(BitStream(r))
        else:
            raise Exception(f"Invalid command: {c}")
