#!/usr/bin/env python3
from datetime import time

from PyQt4 import QtGui
from PyQt4.QtGui import QColor, QBrush, QPen, QFont, QPainter
from PyQt4.QtCore import Qt, QTimer, QRectF, QTime

from libsyntyche import common


class MainWindow(QtGui.QWidget):
    def __init__(self, hours, minutes, seconds, fps):
        super().__init__()
        self.setWindowTitle('panictimer')

        if not hours and not minutes and not seconds:
            hours = 1

        self.time = QTime(0,0)
        self.totalseconds = 0
        self.panictime = hours * 3600 + minutes * 60 + seconds
        self.panic = False

        self.scale = 0.8
        self.mode = 0
        self.fps = fps

        self.timer = QTimer(self)
        self.timer.setInterval(1000/self.fps)
        self.timer.timeout.connect(self.update_time)
        self.timer.start()
#        common.set_hotkey('Escape', self, self.terminal.toggle)
        self.show()

    def update_time(self):
        self.time = self.time.addMSecs(1000/self.fps)
        self.totalseconds += 1/self.fps
        if self.totalseconds >= self.panictime and not self.panic:
            self.panic = True
        self.update()

    def paintEvent(self, event):
        bgcol = QColor('#111')
        if self.panic:
            fgcol = QColor('#e11')
        else:
            fgcol = QColor('#ddd')
        # Size and shit
        w, h = self.width(), self.height()
        minsize = min(w,h)*self.scale
        arcwidth = minsize*0.1
        minsize *= 0.86
        marginx = (w-minsize)/2
        marginy = (h-minsize)/2
        # Start drawing shit
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        painter.setPen(QPen(fgcol, arcwidth, cap=Qt.FlatCap))
        #font = QFont('sv basic manual')
        font = QFont('bank gothic')
        font.setPointSize(get_font_size(font, minsize-2*arcwidth))
        smallfont = QFont(font)
        smallfont.setPointSizeF(font.pointSize()/2)
        painter.fillRect(QRectF(0,0,w,h), bgcol)
        # Timer dial thingy
        painter.setOpacity(0.05)
        painter.drawArc(marginx,marginy, minsize,minsize, 0, 5760)
        painter.setOpacity(1)
        arclength = min(1, self.totalseconds/self.panictime) * 5760
        painter.drawArc(marginx,marginy, minsize,minsize, 90*16, -arclength)
        # Timer text
        painter.setFont(font)
        textoptions = QtGui.QTextOption(Qt.AlignCenter)
        painter.drawText(QRectF(marginx, marginy, minsize, minsize),
                         self.get_text(0), textoptions)
        painter.setFont(smallfont)
        painter.setOpacity(0.5)
        painter.drawText(QRectF(marginx, marginy+minsize*0.4, minsize, minsize/2),
                         self.get_text(1), textoptions)
        #painter.setOpacity(0.15)
        #painter.drawText(QRectF(marginx, marginy+minsize*0.05, minsize, minsize/2),
        #                 self.get_text(2), textoptions)
        painter.end()

    def get_text(self, item):
        if item == 2:
            h, rest = divmod(self.panictime, 3600)
            m, s = divmod(rest, 60)
            return 'target:\n{:0>2}:{:0>2}:{:0>2}'.format(h,m,s)
        texts = [
            self.time.toString('HH:mm:ss'),
            '{:.2%}'.format(self.totalseconds/self.panictime)
        ]
        if self.mode == 0:
            return texts[item]
        elif self.mode == 1:
            return texts[::-1][item]
        elif self.mode == 2:
            return [texts[0], ''][item]
        elif self.mode == 3:
            return [texts[1], ''][item]


    def change_view_mode(self):
        self.mode += 1
        if self.mode > 3:
            self.mode = 0

    def wheelEvent(self, event):
        if event.delta() > 0:
            self.scale += 0.05
        else:
            self.scale = max(0.05, self.scale-0.05)
        event.accept()
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.change_view_mode()
            event.accept()
            self.update()
        else:
            event.ignore()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_0:
            self.scale = 1
            event.accept()
            self.update()
        else:
            event.ignore()


def get_font_size(font, fillwidth, text='00:00:00'):
    """
    Return the correct point size for the string to fill the whole width.
    """
    fm = QtGui.QFontMetricsF(font)
    h = fm.height()
    newh = h/fm.width(text)*fillwidth
    return font.pointSize()/h*newh



def main():
    import argparse, sys
    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--hours', type=int, default=0)
    parser.add_argument('-m', '--minutes', type=int, default=0)
    parser.add_argument('-s', '--seconds', type=int, default=0)
    parser.add_argument('-f', '--fps', type=int, default=1)
    args = parser.parse_args()

    app = QtGui.QApplication([])
    window = MainWindow(args.hours, args.minutes, args.seconds, args.fps)
    app.setActiveWindow(window)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
