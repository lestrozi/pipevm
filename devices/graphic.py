import sys
from devices import Device

class Graphic(Device):
    class Commands:
        REFRESH = 0
        READ_PIXEL = 1
        WRITE_PIXEL = 2
        READ_RECT = 3
        WRITE_RECT = 4
        FILL_RECT = 5

    def consumeInput(self):
        # wait for at least 1 byte
        if len(self.inputBuffer) < 8:
            return

        # TODO: allow non-byte-aligned commands
        c = self.inputBuffer.peek(8).uint
        if c == self.Commands.REFRESH:
            self.vm.refreshGraphic()
        elif c == self.Commands.READ_PIXEL:
            raise Exception("Not implemented")
        elif c == self.Commands.WRITE_PIXEL:
            raise Exception("Not implemented")
        elif c == self.Commands.READ_RECT:
            raise Exception("Not implemented")
        elif c == self.Commands.WRITE_RECT:
            raise Exception("Not implemented")
        elif c == self.Commands.FILL_RECT:
            # x (16b), y (16b), w (16b), h (16b), color (24b)
            if len(self.inputBuffer) < 96:
                return

            c = self.inputBuffer.read(8).uint
            x = self.inputBuffer.read(16).uint
            y = self.inputBuffer.read(16).uint
            w = self.inputBuffer.read(16).uint
            h = self.inputBuffer.read(16).uint
            r = self.inputBuffer.read(8).hex
            g = self.inputBuffer.read(8).hex
            b = self.inputBuffer.read(8).hex
            rgb = f"#{r}{g}{b}"

            # TODO if debug
            print(x, y, w, h, r, g, b, rgb, file=sys.stderr)
            self.vm.drawRect(x, y, w, h, rgb)
        else:
            raise Exception(f"Invalid command: {c}")
