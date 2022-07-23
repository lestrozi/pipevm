import sys
import threading
import time
import tkinter as tk 

class Vm(threading.Thread):
    class Mode:
        TEXT = 0
        GRAPHIC = 1

    def __init__(self):
        self.mode = self.Mode.TEXT
        self.isReady = False
        self.keyPressed = None
        self.inBuf = None

        threading.Thread.__init__(self)
        self.start()

    def clearText(self):
        self.text.delete('1.0', tk.END)

    def putc(self, b):
        self.setMode(self.Mode.TEXT)

        self.text.insert('end', '%s' % b)

    def drawRect(self, x, y, w, h, color):
        self.setMode(self.Mode.GRAPHIC)

        self.canvas.create_rectangle(x, y, x+w, y+h, fill=color, width=0)

    def refreshGraphic(self):
        self.setMode(self.Mode.GRAPHIC)

        self.canvas.update()

    def waitChar(self):
        # only initialize inBuf after the first waitChar call
        # (ie ignore previous keypresses)
        if self.inBuf is None:
            self.inBuf = []

        k = ''
        while k == '':
            while not self.inBuf:
                time.sleep(0.01)

            k, self.inBuf = self.inBuf[0], self.inBuf[1:]

            if k == '':
                print(f"Got empty key", file=sys.stderr)


        # handle newline as char 10
        if k == '\x0D':
            k = '\x0A'

        print(f"Key pressed: {ord(k)}", file=sys.stderr)
        return k


    def onKeyPress(self, event):
        # only save keypresses to inBuf after it's initialized
        # FIXME: add mutex
        if self.inBuf is not None:
            self.inBuf.append(event.char)

        # TODO: add support for multiple keypress?
        self.keyPressed = event.char

    def onKeyRelease(self, event):
        # TODO: add support for multiple keypress?
        self.keyPressed = None

    def getKeyPressed(self):
        return self.keyPressed

    def setMode(self, mode):
        if mode == self.mode:
            return

        if mode == self.Mode.TEXT:
            self.canvas.pack_forget()
            self.text.pack()
            self.root.geometry(f"{self.text_width_height[0]}x{self.text_width_height[1]}")
        elif mode == self.Mode.GRAPHIC:
            self.text.pack_forget()
            self.canvas.pack()
            self.root.geometry(f"{self.canvas_height_width[0]}x{self.canvas_height_width[1]}")

        self.mode = mode

    def run(self):
        self.root = tk.Tk()

        self.text_rows_columns = (25, 80)
        self.canvas_height_width = (320, 240)

        self.text = tk.Text(self.root, background='black', foreground='white', font=('Courier', 16), height=self.text_rows_columns[0], width=self.text_rows_columns[1])
        self.text.pack()
        self.text.update()
        self.text_width_height = (self.text.winfo_width(), self.text.winfo_height())

        self.canvas = tk.Canvas(self.root, width=self.canvas_height_width[0], height=self.canvas_height_width[1])
        self.canvas.pack()
        #self.canvas.scale(tk.ALL, 0, 0, 10.0, 10.0)

        self.root.bind('<KeyPress>', self.onKeyPress)
        self.root.bind('<KeyRelease>', self.onKeyRelease)

        self.setMode(self.mode)
        self.isReady = True
        self.root.mainloop()

    def waitReady(self):
        while not self.isReady:
            continue
