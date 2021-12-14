from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QSizePolicy, QFrame
from PyQt5.QtGui import QColor, QPen, QBrush
from PyQt5.QtCore import Qt


# 3) GameGrid()
class GameGrid(QGraphicsView):
    """
    GameGrid: presents the user the game rendering (the View) and the add/remove cell functionalities

    Parameters:
    model  (CheckboardModel): the model, in order to make use of primitives to modify Cell Size and Game Colors
    width  (int): maximum width of the QGraphicsScene
    height (int): maximum height of the QGraphicsScene

    """

    def __init__(self, model, width=1400, height=800, **kwargs):
        """ Creates the QGraphicsScene (the View) and connects it to the model """

        super().__init__(**kwargs)
        self.model = model

        # We've to observe when the model changes in order to keep the View updated
        self.model.observeBoard(self.renderBoard)  # to observe the cells which are added/removed
        self.model.observeColor(self.renderBoard)  # to observe game colors changings
        self.model.observeCellSize(self.changeSizes)  # to observe the cell size selected

        self.width = width
        self.height = height
        self.cellSize = self.model.getCellSize()

        # Create the View
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, self.width, self.height)
        self.scene.setBackgroundBrush(QBrush(QColor("black")))

        # Some settings on the QGraphicsScene in order to keep the app simple
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setScene(self.scene)
        self.setFrameStyle(QFrame.NoFrame)

        self.renderBoard()

    def mousePressEvent(self, event):
        """ When a mouse key is pressed on the View we call the event handler """
        self.eventHandler(event)
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """ When a mouse key is pressed and moved on the View we call the event handler """
        self.eventHandler(event)
        return super().mouseMoveEvent(event)

    def eventHandler(self, event):
        """ When an interaction with the view is performed we gather where the click happened,
        and we have the following effect to the model:
        left-click  -> add a cell
        right-click -> remove a cell
        """
        i = int(event.pos().x() / self.cellSize)
        j = int(event.pos().y() / self.cellSize)
        if(event.buttons() == Qt.LeftButton):
            self.model.addCell(i, j)
        elif(event.buttons() == Qt.RightButton):
            self.model.removeCell(i, j)

    def renderBoard(self):
        """We get from the model the board to be rendered as a dict:
        if (i, j) is a key, currentBoard[(i, j)] holds the cell and its status,
        otherwise the position (i, j) is empty.
        We get the colors from the Model, based on the state of the cell, as we need those for the rendering.
        """
        currentBoard = self.model.getBoard()
        self.scene.clear()

        for indexes, cell in currentBoard.items():
            i = indexes[0]
            j = indexes[1]
            pos = self.mapToScene(i * self.cellSize, j * self.cellSize)
            color = self.model.getColor(cell.getState())  # get color from the model, based on cell state
            self.scene.addRect(pos.x(), pos.y(), self.cellSize,
                               self.cellSize, QPen(color), QBrush(color))  # each cell is represented as square

    def changeSizes(self):
        """ When the cell size is modified this method is called, we get the new cellSize value
        and we re-render the board."""
        self.cellSize = self.model.getCellSize()
        self.renderBoard()

    def scrollContentsBy(self, dx, dy):
        """ "puppet" class to avoid scrolling in the View """
        pass
