import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt

class MouseTracker(QWidget):
    distance_from_center = 0
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setMouseTracking(True)
        self.x = -1
        self.y = -1

    def initUI(self):
        self.setGeometry(200, 200, 1000, 500)
        self.setWindowTitle('Mouse Tracker')
        self.label = QLabel(self)
        self.label.resize(500, 40)
        self.show()

    def paintEvent(self, e):

        if not (self.x == -1 or self.y == -1):
            q = QPainter()  #Painting the line

            q.begin(self)

            q.drawLine(self.x, self.y, 250, 500)
            q.end()

    def mouseMoveEvent(self, event):
        distance_from_center = round(((event.y() - 250)**2 + (event.x() - 500)**2)**0.5)
        self.label.setText('Coordinates: ( %d : %d )' % (event.x(), event.y()) + "Distance from center: " + str(distance_from_center))

        self.x = event.x()
        self.y = event.y()

        self.update()

    def drawPoints(self, qp, x, y):
        qp.setPen(Qt.red)
        qp.drawPoint(x, y)

app = QApplication(sys.argv)
ex = MouseTracker()
sys.exit(app.exec_())