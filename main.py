import sys
from PyQt5.QtWidgets import QAction, QSlider, QFileDialog, QFrame, QGraphicsView, QGraphicsScene, QToolButton, QApplication, QMenu, QMenuBar, QWidget, QVBoxLayout, QLineEdit, QColorDialog, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QColor, QPen, QBrush, QIcon, QIntValidator
from PyQt5.QtCore import Qt
from model import CheckboardModel


class Toolbar(QHBoxLayout):
    def __init__(self, model, ** kwargs):
        super().__init__(**kwargs)
        self.model = model
        self._menu_bar = QMenuBar()

        self._file = QMenu("&File")
        self._menu_bar.addMenu(self._file)

        self._save = QAction(QIcon("./Icons/iconmonstr-save-1.svg"), "Save Game")
        self._save.triggered.connect(self.saveAction)
        self._file.addAction(self._save)

        self._load = QAction(QIcon("./Icons/iconmonstr-folder-21.svg"), "Load")
        self._load.triggered.connect(self.loadAction)
        self._file.addAction(self._load)

        self._file.addSeparator()

        self._quit = QAction("Quit")
        self._quit.triggered.connect(self.quitAction)
        self._file.addAction(self._quit)

        self._help = QMenu("&Help")
        # self._help.setIcon(QIcon("./Icons/iconmonstr-help-2.svg"))
        self._menu_bar.addMenu(self._help)

        self.setMenuBar(self._menu_bar)

    def saveAction(self):
        file = QFileDialog.getSaveFileName(caption="Save Game", filter="Game of Life (*.gol)")
        self.model.saveGame(file[0])

    def loadAction(self):
        file = QFileDialog.getOpenFileName(caption="Load Game", filter="Game of Life (*.gol)")
        self.model.loadGame(file[0])

    def quitAction(self):
        print("quit")


class ColorButton(QToolButton):
    def __init__(self, name, model, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.name = name

        self.allignColor()
        self.clicked.connect(self.handle_click)
        self.model.observeColor(self.allignColor)

    def handle_click(self):
        new_color = QColorDialog.getColor()
        self.model.setColor(self.name, new_color)

    def allignColor(self):
        color = self.model.getColor(self.name)
        self.setStyleSheet("background-color: " + color.name())


class ConfigPanel(QHBoxLayout):
    def __init__(self, model, **kwargs):
        super().__init__(**kwargs)
        self.model = model

        self.gridSizeInput = QLineEdit(str(self.model.getN()))
        self.gridSizeInput.setMaxLength(3)
        self.gridSizeInput.setMinimumSize(50, 30)
        self.gridSizeInput.setMaximumSize(50, 30)
        self.gridSizeInput.setValidator(QIntValidator(1, 300))  # Add feedback if too large number
        self.gridSizeInput.returnPressed.connect(self.enterNewGridSize)

        self.addWidget(QLabel("Grid Size:"), alignment=Qt.AlignLeft)
        self.addWidget(self.gridSizeInput, alignment=Qt.AlignLeft)
        self.addStretch()

        color_controllers_names = ["Alive", "Dead", "Born"]
        for n in color_controllers_names:
            self.addWidget(QLabel(n + ":"), alignment=Qt.AlignRight)
            self.addWidget(ColorButton(name=n, model=self.model), alignment=Qt.AlignLeft)

    def enterNewGridSize(self):
        self.model.setN(int(self.gridSizeInput.text()))


class GameGrid(QGraphicsView):
    def __init__(self, model, width=800, height=800, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.model.observeBoard(self.renderBoard)
        self.model.observeColor(self.renderBoard)
        self.model.observeGridSize(self.changeSizes)

        self.width = width
        self.height = height
        self.cellSize = int(self.height / self.model.getN())

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, self.width, self.height)
        self.scene.setBackgroundBrush(QBrush(QColor("black")))

        self.setFixedSize(self.width, self.height)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setScene(self.scene)
        self.setFrameStyle(QFrame.NoFrame)

        self.renderBoard()

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
            color = self.model.getColor(cell.getState())
            self.scene.addRect(i * self.cellSize, j * self.cellSize, self.cellSize,
                               self.cellSize, QPen(color), QBrush(color))

    def changeSizes(self):
        self.cellSize = int(self.height / self.model.getN())
        self.renderBoard()


class SimulationPanel(QHBoxLayout):
    def __init__(self, model, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.model.observeBoard(self.alignButtonStatus)

        self._left = QPushButton(QIcon("./Icons/iconmonstr-arrow-left.svg"), "")
        self._left.clicked.connect(self.clickLeft)
        self._left.setEnabled(False)

        self._right = QPushButton(QIcon("./Icons/iconmonstr-arrow-12.svg"), "")
        self._right.clicked.connect(self.clickRight)
        self._left.setEnabled(False)

        self._pause = QPushButton(QIcon("./Icons/iconmonstr-media-control-49.svg"), "")
        self._pause.clicked.connect(self.clickPause)

        self._play = QPushButton(QIcon("./Icons/iconmonstr-media-control-48.svg"), "")
        self._play.clicked.connect(self.clickPlay)

        self._speed = QSlider(Qt.Horizontal)
        self._speed.setMaximumSize(300, 50)
        self._speed.setMinimum(1)
        self._speed.setMaximum(29)
        self._speed.setValue(self.model.getSpeed())
        self._speed.valueChanged[int].connect(self.sliderModified)

        self.addWidget(self._left)
        self.addWidget(self._right)
        self.addWidget(self._pause)
        self.addWidget(self._play)
        self.addStretch()
        self.addWidget(QLabel("Speed:"))
        self.addWidget(self._speed)

    def clickRight(self):
        self.model.goNext()

    def clickLeft(self):
        self.model.goBack()

    def clickPause(self):
        self.model.pause()

    def clickPlay(self):
        self.model.play()

    def sliderModified(self, value):
        self.model.setSpeed(value)

    def alignButtonStatus(self):
        self._left.setEnabled(self.model.getLeftEnabled())
        self._right.setEnabled(self.model.getRightEnabled())


# The main application.
class App(QApplication):

    def __init__(self, args):

        super().__init__(args)
        self.setStyleSheet('*{font-size: 20px;}')
        self._model = CheckboardModel(N=50)

        self._root = QWidget()
        self._layout = QVBoxLayout()

        self._toolbar = QWidget()
        self._toolbar.setLayout(Toolbar(self._model))

        self._config = QWidget()
        self._config.setLayout(ConfigPanel(self._model))

        self._game_grid = GameGrid(self._model)

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
