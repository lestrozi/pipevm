import os
import time
import sys
sys.path.append('..')   # ugh
from pathlib import Path
from bitutil import BitStream
from devices import Device

class Filesystem(Device):
    class Commands:
        LS = 0
        STAT = 1
        READ = 2    # no open/close required, at least for now
        WRITE = 3    # no open/close required, at least for now
        MKDIR = 4
        RM = 5

    def setRoot(self, root):
        self.root = root

        try:
            os.mkdir(root)
        except FileExistsError:
            pass

    def getNullTerminatedPath(self, start):
        zeroBytePos = None
        for i in range(start, len(self.inputBuffer), 8):
            if self.inputBuffer[i:i+8].uint == 0:
                zeroBytePos = i

        if zeroBytePos is None:
            return None, 0

        relative_path = self.inputBuffer[start:zeroBytePos].bytes.decode('utf-8')

        newPath = self.root + "/" + relative_path
        # raise exception if path traversal
        Path(newPath).resolve().relative_to(self.root).resolve()

        abs_path = str(Path(newPath).resolve())

        return abs_path, (zeroBytePos-start)

    def consumeInput(self):
        # wait for at least 1 byte
        if len(self.inputBuffer) < 8:
            return

        # TODO: allow non-byte-aligned commands
        c = self.inputBuffer.peek(8).uint
        if c == self.Commands.LS:
            start = 8
            abs_path, pathLen = self.getNullTerminatedPath(start)
            if abs_path is None:
                return

            self.inputBuffer.read(8)
            self.inputBuffer.read(pathLen + 8)

            rel_path = abs_path[len(self.root):]
            print(f"ls {abs_path}", file=sys.stderr)
            for f in os.listdir(abs_path):
                p = str(Path(abs_path + "/" + f))
                p = p[len(self.root):]
                self.output(BitStream((p.encode('utf-8') + bytes([0]))))
            self.output(BitStream(bytes([0])))
        elif c == self.Commands.STAT:
            start = 8
            abs_path, pathLen = self.getNullTerminatedPath(start)
            if abs_path is None:
                return

            self.inputBuffer.read(8)
            self.inputBuffer.read(pathLen + 8)

            # for this version, only return size and if is dir; otherwise
            # (even if it doesn't exist) return is file
            # this is pretty bad, but it's just a prototype
            s = os.stat(abs_path)
            is_dir = os.path.isdir(abs_path)

            print(f"stat {abs_path}: {int(is_dir)} {s.st_size}", file=sys.stderr)
            self.output(BitStream(uint=int(is_dir), length=8))
            self.output(BitStream(uint=s.st_size, length=32))
        elif c == self.Commands.READ:
            if len(self.inputBuffer) < 8+32:
                return

            start = 8+32
            abs_path, pathLen = self.getNullTerminatedPath(start)
            if abs_path is None:
                return

            self.inputBuffer.read(8)
            readBytesLen = self.inputBuffer.read(32).uint
            self.inputBuffer.read(pathLen + 8)

            print(f"reading {readBytesLen} bytes from {abs_path}", file=sys.stderr)
            with open(abs_path, 'rb') as f:
                result = f.read(readBytesLen)
                self.output(BitStream(result))

                # if eof, send a 0 byte in the end
                if len(result) < readBytesLen:
                    self.output(BitStream(int=0, length=8))
        elif c == self.Commands.WRITE:
            if len(self.inputBuffer) < 8+32:
                return

            start = 8+32
            abs_path, pathLen = self.getNullTerminatedPath(start)
            if abs_path is None:
                return

            writeBytesLen = self.inputBuffer[8:40].uint

            if len(self.inputBuffer) < 8+32+pathLen+8+8*writeBytesLen:
                return

            self.inputBuffer.read(8)
            self.inputBuffer.read(32)
            self.inputBuffer.read(pathLen + 8)
            b = self.inputBuffer.read(8*writeBytesLen)

            print(f"writing {writeBytesLen} bytes to {abs_path}", file=sys.stderr)
            with open(abs_path, 'wb') as f:
                f.write(b.bytes)

            # success (always)
            self.output(BitStream(int=0, length=8))
        elif c == self.Commands.MKDIR:
            if len(self.inputBuffer) < 8:
                return

            start = 8
            abs_path, pathLen = self.getNullTerminatedPath(start)
            if abs_path is None:
                return

            self.inputBuffer.read(8)
            self.inputBuffer.read(pathLen + 8)

            try:
                print(f"mkdir {abs_path}", file=sys.stderr)
                os.mkdir(abs_path)
            except:
                self.output(BitStream(int=1, length=8))

            # success
            self.output(BitStream(int=0, length=8))
        elif c == self.Commands.RM:
            if len(self.inputBuffer) < 8:
                return

            start = 8
            abs_path, pathLen = self.getNullTerminatedPath(start)
            if abs_path is None:
                return

            self.inputBuffer.read(8)
            self.inputBuffer.read(pathLen + 8)

            try:
                print(f"trying to remove file {abs_path}", file=sys.stderr)
                os.remove(abs_path)
                self.output(BitStream(int=0, length=8))
                return
            except:
                pass

            try:
                print(f"trying to remove dir {abs_path}", file=sys.stderr)
                os.rmdir(abs_path)
            except:
                self.output(BitStream(int=1, length=8))

            self.output(BitStream(int=0, length=8))
        else:
            raise Exception(f"Invalid command: {c}")
