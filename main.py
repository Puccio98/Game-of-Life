import sys
from PyQt5.QtWidgets import QSizePolicy, QMessageBox, QAction, QSlider, QFileDialog, QFrame, QGraphicsView, QGraphicsScene, QToolButton, QApplication, QMenu, QMenuBar, QWidget, QVBoxLayout, QLineEdit, QColorDialog, QHBoxLayout, QLabel, QPushButton
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

        self._help = QAction("&Help")
        self._help.triggered.connect(self.helpDialog)
        self._menu_bar.addAction(self._help)

        self.setMenuBar(self._menu_bar)

    def saveAction(self):
        file = QFileDialog.getSaveFileName(caption="Save Game", filter="Game of Life (*.gol)")
        self.model.saveGame(file[0])

    def loadAction(self):
        file = QFileDialog.getOpenFileName(caption="Load Game", filter="Game of Life (*.gol)")
        self.model.loadGame(file[0])

    def quitAction(self):
        QApplication.exit()

    def helpDialog(self):
        HelpDialog()


class HelpDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Help")
        # self.setStyleSheet("h2{text-align:center}")
        self.setMinimumSize(100, 200)

        self.setText("<h2>Conway's Game of Life</h2>")
        self.setInformativeText("<a href=\"https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life\">Here</a> you can find how the game works."
                                + "<h3>Commands:</h3>"
                                + "<li> <b>Left Click:</b> add cells"
                                + "<li> <b>Right Click:</b> remove cells")

        self.exec_()


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

        self.cellSizeInput = QLineEdit(str(self.model.getCellSize()))
        self.cellSizeInput.setMaxLength(3)
        self.cellSizeInput.setMinimumSize(50, 30)
        self.cellSizeInput.setMaximumSize(50, 30)
        self.cellSizeInput.setValidator(QIntValidator(5, 100))
        self.cellSizeInput.returnPressed.connect(self.enterNewCellSize)

        self.addWidget(QLabel("Cell Size:"), alignment=Qt.AlignLeft)
        self.addWidget(self.cellSizeInput, alignment=Qt.AlignLeft)
        self.addStretch()

        color_controllers_names = ["Alive", "Dead", "Born"]
        for n in color_controllers_names:
            self.addWidget(QLabel(n + ":"), alignment=Qt.AlignRight)
            self.addWidget(ColorButton(name=n, model=self.model), alignment=Qt.AlignLeft)

    def enterNewCellSize(self):
        self.model.setCellSize(int(self.cellSizeInput.text()))


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


class SimulationPanel(QHBoxLayout):
    def __init__(self, model, **kwargs):
        super().__init__(**kwargs)

        self.model = model
        self.model.observeBoard(self.alignArrowStatus)

        self._left = QPushButton(QIcon("./Icons/iconmonstr-arrow-left.svg"), "")
        self._left.clicked.connect(self.clickLeft)
        self._left.setEnabled(False)
        self._left.setMinimumSize(40, 30)

        self._right = QPushButton(QIcon("./Icons/iconmonstr-arrow-12.svg"), "")
        self._right.clicked.connect(self.clickRight)
        self._right.setEnabled(False)
        self._right.setMinimumSize(40, 30)

        self._pause = QPushButton(QIcon("./Icons/iconmonstr-media-control-49.svg"), "")
        self._pause.clicked.connect(self.clickPause)
        self._pause.setEnabled(False)
        self._pause.setMinimumSize(40, 30)

        self._play = QPushButton(QIcon("./Icons/iconmonstr-media-control-48.svg"), "")
        self._play.clicked.connect(self.clickPlay)
        self._play.setMinimumSize(40, 30)

        self._reset = QPushButton("Reset")
        self._reset.clicked.connect(self.clickReset)
        self._reset.setMinimumSize(40, 30)

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
        self.addStretch()
        self.addWidget(self._reset)

    def clickRight(self):
        self.model.goNext()

    def clickLeft(self):
        self.model.goBack()

    def clickPause(self):
        self.model.pause()
        self._pause.setEnabled(False)
        self._play.setEnabled(True)

    def clickPlay(self):
        self.model.play()
        self._play.setEnabled(False)
        self._pause.setEnabled(True)

    def clickReset(self):
        self.clickPause()
        self.model.reset()

    def sliderModified(self, value):
        self.model.setSpeed(value)

    def alignArrowStatus(self):
        self._left.setEnabled(self.model.getLeftEnabled())
        self._right.setEnabled(self.model.getRightEnabled())


# The main application.
class App(QApplication):

    def __init__(self, args):

        super().__init__(args)
        self.setStyleSheet("*{font-size: 20px;} \n QPushButton:enabled{background-color: #d3d3d3;} \n QPushButton:disabled{background-color: white;}")

        self._model = CheckboardModel(cellSize=15, maxCols=170, maxRows=290)

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

    def quit(self):
        self.exit()


def Root(QWidget):
    def __init__(self, **kwargs):
        pass


# Instantiate and run the application.
app = App(sys.argv)
