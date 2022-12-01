import time

import keyboard
import pyautogui
import pyscreenshot
import pytesseract as tess
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from colorama import Fore

opacity = 0.6


class Point(QGraphicsItem):
    def __init__(self, x, y):
        super(Point, self).__init__()
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.rectF = QRectF(0, 0, 30, 30)
        self.x = x
        self.y = y
        self._brush = QBrush(Qt.black)

    def setBrush(self, brush):
        self._brush = brush
        self.update()

    def boundingRect(self):
        return self.rectF

    def paint(self, painter=None, style=None, widget=None, ):
        painter.fillRect(self.rectF, self._brush)

    def hoverMoveEvent(self, event):
        point = event.pos().toPoint()
        print(point)
        QGraphicsItem.hoverMoveEvent(self, event)


class Viewer(QGraphicsView):
    photoClicked = pyqtSignal(QPoint)
    rectChanged = pyqtSignal(QRect)

    def __init__(self, parent):
        super(Viewer, self).__init__(parent)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.setMouseTracking(True)
        self.origin = QPoint()
        self.changeRubberBand = False

        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWindowOpacity(opacity)
        self.setFrameShape(QFrame.NoFrame)
        self.area = float()
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def fitInView(self, scale=True):
        rect = QRectF(self.area)
        if not rect.isNull():
            self.setSceneRect(rect)

            unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())
            viewrect = self.viewport().rect()
            scenerect = self.transform().mapRect(rect)
            factor = min(viewrect.width() / scenerect.width(),
                         viewrect.height() / scenerect.height())
            self.scale(factor, factor)
            self._zoom = 0

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            global cmx1, cmy1
            self.origin = event.pos()
            cmx1, cmy1 = pyautogui.position()
            print(cmx1, cmy1)
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rectChanged.emit(self.rubberBand.geometry())
            self.rubberBand.show()
            self.changeRubberBand = True
            return
            # QGraphicsView.mousePressEvent(self,event)
        elif event.button() == Qt.MidButton:
            self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
            self.original_event = event
            handmade_event = QMouseEvent(QEvent.MouseButtonPress, QPointF(event.pos()), Qt.LeftButton, event.buttons(),
                                         Qt.KeyboardModifiers())
            QGraphicsView.mousePressEvent(self, handmade_event)

        super(Viewer, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.changeRubberBand = False
            global cmx2, cmy2
            cmx2, cmy2 = pyautogui.position()
            print(cmx2, cmy2)
            QGraphicsView.mouseReleaseEvent(self, event)
            # sys.exit()
            # run autotyper function
            window.hide()
            autotyper()
        elif event.button() == Qt.MidButton:
            self.viewport().setCursor(Qt.OpenHandCursor)
            handmade_event = QMouseEvent(QEvent.MouseButtonRelease, QPointF(event.pos()), Qt.LeftButton,
                                         event.buttons(), Qt.KeyboardModifiers())
            QGraphicsView.mouseReleaseEvent(self, handmade_event)
        super(Viewer, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.changeRubberBand:
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())
            self.rectChanged.emit(self.rubberBand.geometry())
            QGraphicsView.mouseMoveEvent(self, event)
        super(Viewer, self).mouseMoveEvent(event)


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.viewer = Viewer(self)
        self.setWindowOpacity(opacity)

        VBlayout = QVBoxLayout(self)
        VBlayout.addWidget(self.viewer)


def autotyper():
    tess.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    nonbreak = True
    abc = "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuopasdfghjklizxcvbnm1234567890.,()'`/\-+<>:;!@#$%^&*\[]"
    while 1:
        # print(Fore.BLUE + "Press 1 when your cursor is on top left corner of the area you want to scan")
        # keyboard.wait("1")
        # cmx1, cmy1 = pyautogui.position()
        # print(Fore.BLUE + "Press 2 when your cursor is on bottom right corner of the area you want to scan")
        # keyboard.wait("2")
        # cmx2, cmy2 = pyautogui.position()
        print(
            Fore.GREEN + "Click enter when your cursor is in the position you want for it to type, it will automatically click and start to type everything that is in the area you selected")
        keyboard.wait("enter")
        pyautogui.click()
        print(Fore.RED + "hold p to stop")
        word = ""
        while nonbreak:
            img = pyscreenshot.grab(bbox=(cmx1, cmy1, cmx2, cmy2))
            text = tess.image_to_string(img)
            if text == "":
                break
            for a in range(0, len(text)):
                if keyboard.is_pressed('p'):
                    print(Fore.RED + 'STOPPING THE AUTOTYPER')
                    nonbreak = False
                    break

                if text[a] in abc:
                    word = word + text[a]
                else:
                    pyautogui.write(word)
                    word = ""
                    pyautogui.press('space')
        time.sleep(0.01)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = Window()
    geometry = app.desktop().availableGeometry()
    geometry.setHeight(geometry.height())
    window.setGeometry(geometry)
    window.show()
    sys.exit(app.exec_())
