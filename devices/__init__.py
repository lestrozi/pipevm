from bitutil import BitStream

class Device:
    def __init__(self, vm, outputBuffer, isByteAligned=True):
        self.vm = vm
        self.inputBuffer = BitStream()
        self.outputBuffer = outputBuffer

    def input(self, b):
        self.inputBuffer.append(b)
        self.consumeInput()

    def consumeInput(self):
        raise Exception("NOT IMPLEMENTED")

    def output(self, b):
        self.outputBuffer.append(b)
