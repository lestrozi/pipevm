from bitutil import BitStream

class Device:
    def __init__(self, vm, isByteAligned=True):
        self.vm = vm
        self.inputBuffer = BitStream()

    def input(self, b):
        self.inputBuffer.append(b)
        self.consumeInput()

    def consumeInput(self):
        raise Exception("NOT IMPLEMENTED")

    def output(self):
        raise Exception("NOT IMPLEMENTED")
