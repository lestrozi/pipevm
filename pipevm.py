from bitutil import BitStream
from vm import Vm
from devices import text, graphic, keyboard
import sys

class PipeCmd:
    SPECIAL_CHAR = 0xff
    DEVICE_SELECTOR_CHAR = 0x80

    def __init__(self, vm):
        # TODO: CLI arguments:
        self.byteAligned = True
        self.bitDictionary = None #[48, 49]    # bytes that represent bit-0 and bit-1 respectively
                                    # is ignored if byteAligned = True


        self.vm = vm
        self.devices = [
                text.Text(vm, self.byteAligned),
                graphic.Graphic(vm, self.byteAligned),
                keyboard.Keyboard(vm, self.byteAligned),
        ]
        self.device = self.devices[0]
        self.inputBuffer = BitStream()

        fd = sys.stdin.fileno()

        while True:
            b = sys.stdin.buffer.raw.read(1)
            if b == b'':
                print("EOF")
                quit()

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
                    print(f"Selecting device {deviceNum}")
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
