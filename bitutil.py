import bitstring

# work-around to make bitstring.BitStream actually lose the bits read
# instead of just advancing the reading pointer
class BitStream(bitstring.BitStream):
    def peek(self, fmt):
        # horrible, but the original peek() is defined
        # using read() and don't  expect it to delete bits from
        # the beginning as my override does
        thisRead = self.read
        self.read = super().read
        v = super().peek(fmt)
        self.read = thisRead
        return v

    def read(self, n):
        c = super().read(n)
        del self[0:n]
        self.pos = 0
        return c
