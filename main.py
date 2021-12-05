import sys
from PyQt5.QtWidgets import QSlider, QFrame, QGraphicsView, QGraphicsScene, QToolButton, QApplication, QMenu, QMenuBar, QWidget, QVBoxLayout, QLineEdit, QColorDialog, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QColor, QPen, QBrush, QIcon
from PyQt5.QtCore import Qt
from model import Checkboard

default_colors = {
    "Alive": QColor("white"),
    "Dead": QColor("red"),
    "Born": QColor("blue")
}


class Toolbar(QHBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._menu_bar = QMenuBar()
        self._load = QMenu("Load")
        self._save = QMenu("Save Execution")
        self._reset = QMenu("Reset")
        self._quit = QMenu("Quit")
        self._help = QMenu("Help")
        self._menu_bar.addMenu(self._load)
        self._menu_bar.addMenu(self._save)
        self._menu_bar.addMenu(self._reset)
        self._menu_bar.addMenu(self._quit)
        self._menu_bar.addMenu(self._help)

        self.setMenuBar(self._menu_bar)


class GridSizeInput(QLineEdit):
    def __init__(self, name, val=30, **kwargs):
        super().__init__(**kwargs)
        self._val = val
        self._name = name

        self.setMaxLength(4)
        self.setText(str(self._val))
        self.setMinimumSize(60, 30)
        self.setMaximumSize(60, 30)

        self.setEnabled(False)


class ColorButton(QToolButton):
    def __init__(self, name, color, **kwargs):
        super().__init__(**kwargs)
        self.set_color(color)
        self._name = name

        self.setStyleSheet("background-color: " + self._color)

        self.clicked.connect(self.handle_click)

    def handle_click(self):
        print('Clicked ', self._name)
        new_color = QColorDialog.getColor()
        self.set_color(new_color)

    def set_color(self, new_color):
        if new_color.isValid():
            self._color = new_color.name()
            self.setStyleSheet("background-color: " + self._color)


class ConfigPanel(QHBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.addWidget(QLabel("Grid Size:"), alignment=Qt.AlignLeft)
        self._grid_size_controllers = []
        self.addWidget(GridSizeInput("Rows"), alignment=Qt.AlignLeft)
        self.addWidget(GridSizeInput("Cols"), alignment=Qt.AlignLeft)
        self.addStretch()

        self._color_controllers = []
        color_controllers_names = ["Alive", "Dead", "Born"]
        for n in color_controllers_names:
            self.addWidget(QLabel(n + ":"), alignment=Qt.AlignRight)
            self.addWidget(ColorButton(name=n, color=default_colors[n]), alignment=Qt.AlignLeft)


class GameGrid(QGraphicsView):
    def __init__(self, checkboard, rows=60, cols=60, width=600, height=600, **kwargs):
        super().__init__(**kwargs)
        self.checkboardModel = checkboard
        self.checkboardModel.observe(self.renderBoard)

        self.width = width
        self.height = height
        self.cellSizeX = int(self.height / rows)
        self.cellSizeY = int(self.width / cols)

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, self.width, self.height)

        self.setBackgroundBrush(QBrush(QColor("black")))
        self.setFixedSize(self.width, self.height)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setScene(self.scene)
        self.setFrameStyle(QFrame.NoFrame)

    def eventHandler(self, event):
        i = int(event.pos().x() / self.cellSizeX)
        j = int(event.pos().y() / self.cellSizeY)
        if(event.buttons() == Qt.LeftButton):
            self.checkboardModel.addCell(i, j)
        elif(event.buttons() == Qt.RightButton):
            self.checkboardModel.removeCell(i, j)

    def mousePressEvent(self, event):
        self.eventHandler(event)
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.eventHandler(event)
        return super().mouseMoveEvent(event)

    def renderBoard(self):
        currentBoard = self.checkboardModel.getBoard()
        self.scene.clear()

        for indexes, cell in currentBoard.items():
            i = indexes[0]
            j = indexes[1]
            color = default_colors[cell.getState()]
            self.scene.addRect(i * self.cellSizeX, j * self.cellSizeY, self.cellSizeX,
                               self.cellSizeY, QPen(color), QBrush(color))


class SimulationPanel(QHBoxLayout):
    def __init__(self, checkboard, **kwargs):
        super().__init__(**kwargs)
        self.checkboard = checkboard
        self._left = QPushButton(QIcon("./Icons/iconmonstr-arrow-left.svg"), "")
        self._left.clicked.connect(self.clickLeft)

        self._right = QPushButton(QIcon("./Icons/iconmonstr-arrow-12.svg"), "")
        self._right.clicked.connect(self.clickRight)

        self._pause = QPushButton(QIcon("./Icons/iconmonstr-media-control-49.svg"), "")
        self._play = QPushButton(QIcon("./Icons/iconmonstr-media-control-48.svg"), "")
        self._speed = QSlider(Qt.Horizontal)
        self._speed.setMaximumSize(300, 50)

        self.addWidget(self._left)
        self.addWidget(self._right)
        self.addWidget(self._pause)
        self.addWidget(self._play)
        self.addStretch()
        self.addWidget(QLabel("Speed:"))
        self.addWidget(self._speed)

    def clickRight(self):
        self.checkboard.next()

    def clickLeft(self):
        self.checkboard.goBack()


# The main application.
class App(QApplication):

    def __init__(self, args):

        super().__init__(args)
        # self.setStyleSheet('*{font-size: 20px; color: white; background-color: #292929;}')
        self.setStyleSheet('*{font-size: 20px;}')
        rows = 30
        cols = 30
        self._model = Checkboard(rows, cols)

        self._root = QWidget()
        self._layout = QVBoxLayout()

        self._toolbar = QWidget()
        self._toolbar.setLayout(Toolbar())

        self._config = QWidget()
        self._config.setLayout(ConfigPanel())

        self._game_grid = GameGrid(self._model, rows, cols)

        self._simulation_panel = QWidget()
        self._simulation_panel.setLayout(SimulationPanel(self._model))

        self._layout.addWidget(self._toolbar)
        self._layout.addWidget(self._config)
        self._layout.addStretch()
        self._layout.addWidget(self._game_grid)
        self._layout.setAlignment(self._game_grid, Qt.AlignCenter)
        self._layout.addWidget(self._simulation_panel)

        self._root.setLayout(self._layout)
        self._root.show()
        self.exec_()


# Instantiate and run the application.
app = App(sys.argv)
