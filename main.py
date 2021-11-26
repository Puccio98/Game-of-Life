import sys
from PyQt5.QtWidgets import QToolButton, QSizePolicy, QApplication, QMenu, QMenuBar, QWidget, QGridLayout, QVBoxLayout, QLineEdit, QColorDialog, QHBoxLayout, QBoxLayout, QLabel, QPushButton, QToolBar
from PyQt5.QtGui import QColor

default_colors = {
    "Alive": "white",
    "Dead": "red",
    "Born": "blue"
}


class GameGrid(QGridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class SimulationPanel(QGridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class GridSizeInput(QLineEdit):
    def __init__(self, name, val=50, **kwargs):
        super().__init__(**kwargs)
        self._val = val
        self._name = name

        self.setMaxLength(4)
        self.setText(str(self._val))


class ColorButton(QToolButton):
    def __init__(self, name, color, **kwargs):
        super().__init__(**kwargs)
        self._color = color
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

        # self._model.insertDigit(self._value)


class ConfigPanel(QHBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.addWidget(QLabel("Grid Size:"))
        self._grid_size_controllers = []
        self.addWidget(GridSizeInput("Rows"))
        self.addWidget(GridSizeInput("Cols"))

        self._color_controllers = []
        color_controllers_names = ["Alive", "Dead", "Born"]
        for n in color_controllers_names:
            self.addWidget(QLabel(n + ":"))
            self.addWidget(ColorButton(name=n, color=default_colors[n]))


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
        self.setStyleSheet('*{font-size: 20px;}')

        self._root = QWidget()
        self._layout = QGridLayout()

        self._toolbar = QWidget()
        self._toolbar.setLayout(Toolbar())

        self._config = QWidget()
        self._config.setLayout(ConfigPanel())

        self._layout.addWidget(self._toolbar)
        self._layout.addWidget(self._config)

        self._root.setLayout(self._layout)
        self._root.show()
        self.exec_()


# Instantiate and run the application.
app = App(sys.argv)
