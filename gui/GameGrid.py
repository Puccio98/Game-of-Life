from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QSizePolicy, QFrame
from PyQt5.QtGui import QColor, QPen, QBrush
from PyQt5.QtCore import Qt


class GameGrid(QGraphicsView):
    def __init__(self, model, width=1400, height=800, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.model.observeBoard(self.renderBoard)
        self.model.observeColor(self.renderBoard)
        self.model.observeGridSize(self.changeSizes)

        self.width = width
        self.height = height
        self.cellSize = self.model.getCellSize()

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, self.width, self.height)
        self.scene.setBackgroundBrush(QBrush(QColor("black")))

        # self.setFixedSize(self.width, self.height)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setScene(self.scene)
        self.setFrameStyle(QFrame.NoFrame)

        self.renderBoard()

    def scrollContentsBy(self, dx, dy):
        pass

    def eventHandler(self, event):
        i = int(event.pos().x() / self.cellSize)
        j = int(event.pos().y() / self.cellSize)
        if(event.buttons() == Qt.LeftButton):
            self.model.addCell(i, j)
        elif(event.buttons() == Qt.RightButton):
            self.model.removeCell(i, j)

    def mousePressEvent(self, event):
        self.eventHandler(event)
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.eventHandler(event)
        return super().mouseMoveEvent(event)

    def renderBoard(self):
        currentBoard = self.model.getBoard()
        self.scene.clear()

        for indexes, cell in currentBoard.items():
            i = indexes[0]
            j = indexes[1]
            pos = self.mapToScene(i * self.cellSize, j * self.cellSize)
            color = self.model.getColor(cell.getState())
            self.scene.addRect(pos.x(), pos.y(), self.cellSize,
                               self.cellSize, QPen(color), QBrush(color))

    def changeSizes(self):
        self.cellSize = self.model.getCellSize()
        self.renderBoard()
