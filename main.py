import sys
from PyQt5.QtWidgets import QToolButton, QSizePolicy, QApplication, QMenu, QMenuBar, QWidget, QGridLayout, QVBoxLayout, QLineEdit, QColorDialog, QHBoxLayout, QBoxLayout, QLabel, QPushButton, QToolBar
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

default_colors = {
    "Alive": QColor("white"),
    "Dead": QColor("red"),
    "Born": QColor("blue")
}


class GameGrid(QGridLayout):
    def __init__(self, rows=30, cols=30, **kwargs):
        super().__init__(**kwargs)
        self.setHorizontalSpacing(0)
        self.setVerticalSpacing(0)

        for i in range(rows):
            for j in range(cols):
                self.addWidget(GameCell(i, j), i, j)


class GameCell(QToolButton):
    def __init__(self, i, j, **kwargs):
        super().__init__(**kwargs)
        self._i = i
        self._j = j

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(10, 10)
        self.setMaximumSize(60, 60)

        self.setStyleSheet("background-color: grey;")

        self.clicked.connect(self.handleClick)

    def handleClick(self):
        print(self._i, self._j)


class SimulationPanel(QGridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class GridSizeInput(QLineEdit):
    def __init__(self, name, val=30, **kwargs):
        super().__init__(**kwargs)
        self._val = val
        self._name = name

        self.setMaxLength(4)
        self.setText(str(self._val))
        self.setMinimumSize(60, 30)
        self.setMaximumSize(60, 30)


class ColorButton(QToolButton):
    def __init__(self, name, color, **kwargs):
        super().__init__(**kwargs)
        self.set_color(color)
        self._name = name

        self.setStyleSheet("background-color: " + self._color)

        self.clicked.connect(self.handleClick)

    def handleClick(self):
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


class Toolbar(QHBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._menu_bar = QMenuBar()
        self._load = QMenu("Load")
        self._save = QMenu("Save Execution")
        self._quit = QMenu("Quit")
        self._help = QMenu("Help")
        self._menu_bar.addMenu(self._load)
        self._menu_bar.addMenu(self._save)
        self._menu_bar.addMenu(self._quit)
        self._menu_bar.addMenu(self._help)

        self.setMenuBar(self._menu_bar)


# The main application.
class App(QApplication):

    def __init__(self, args):

        super().__init__(args)
        self.setStyleSheet('*{font-size: 20px; color: white; background-color: #292929;}')

        self._root = QWidget()
        self._layout = QGridLayout()

        self._toolbar = QWidget()
        self._toolbar.setLayout(Toolbar())

        self._config = QWidget()
        self._config.setLayout(ConfigPanel())

        self._game_grid = QWidget()
        self._game_grid.setLayout(GameGrid())

        self._layout.addWidget(self._toolbar)
        self._layout.addWidget(self._config)
        self._layout.addWidget(self._game_grid)

        self._root.setLayout(self._layout)
        self._root.show()
        self.exec_()


# Instantiate and run the application.
app = App(sys.argv)
