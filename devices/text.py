from devices import Device

class Text(Device):
    SPECIAL_CHAR = 0xff

    class Commands:
        CLEAR_SCREEN = 0
        LOCATE = 1

    def consumeInput(self):
        # wait for at least 1 byte
        if len(self.inputBuffer) < 8:
            return

        c = self.inputBuffer.peek(8).uint
        if c == self.SPECIAL_CHAR:
            if len(self.inputBuffer) < 16:
                # wait for next token
                return

            c = self.inputBuffer[8:16].uint
            if c == self.Commands.CLEAR_SCREEN:
                c = self.inputBuffer.read(16)
                self.vm.clearText()
            elif c == self.Commands.LOCATE:
                raise Exception("Not implemented")
            else:
                raise Exception(f"Invalid command: {c}")
        elif c < 128:
            c = self.inputBuffer.read(8).uint
            self.vm.putc(chr(c))
        else:
            raise Exception(f"Non-ASCII char to print: {c}")
