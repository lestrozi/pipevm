import sys
sys.path.append('..')   # ugh
from bitutil import BitStream
from devices import Device

class Keyboard(Device):
    class Commands:
        WAIT_CHAR = 0
        GET_KEYPRESSED = 1

    def consumeInput(self):
        # wait for at least 1 byte
        if len(self.inputBuffer) < 8:
            return

        # TODO: allow non-byte-aligned commands
        c = self.inputBuffer.peek(8).uint
        if c == self.Commands.WAIT_CHAR:
            raise Exception("Not implemented")
        elif c == self.Commands.GET_KEYPRESSED:
            print("Get keypressed", file=sys.stderr)
            c = self.inputBuffer.read(8).uint

            # TODO: improve method to allow read special keys
            kp = self.vm.getKeyPressed()
            if kp == None:
                # for non-byte-aligned, just 1 or 2 bits might suffice
                # even for byte-aligned, other encodings are certainly better,
                # but this is enough for a prototype
                self.output(BitStream('0x00'))
            else:
                self.output(BitStream('0x01'))
                self.output(BitStream(kp.encode('latin-1')))
        else:
            raise Exception(f"Invalid command: {c}")
