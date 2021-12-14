import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

from Model.CheckboardModel import CheckboardModel
from UserInterface.Toolbar import Toolbar
from UserInterface.ConfigPanel import ConfigPanel
from UserInterface.GameGrid import GameGrid
from UserInterface.SimulationPanel import SimulationPanel


class App(QApplication):
    """
    The main application: creates both the model and the view+controllers.

    The app U.I. consists of four parts:
    1) Toolbar()             contains load/save/help functions (on top)
    2) ConfigPanel()         to manage Cell Size and Interface Colors (right below the Toolbar)
    3) GameGrid()            the grid where the Game of Life is displayed (in the center)
    4) SimulationPanel()     contains the controllers for the game: play/pause/back/next/speed/reset (under the GameGrid)

    All the data needed for the app to run are stored into CheckboardModel() class, which is connected to the all 4 components.

    """

    def __init__(self, args):
        """ Generates the app: creates the model and the UI."""

        super().__init__(args)

        # Some style for the interface
        self.setStyleSheet("*{font-size: 20px;} \n" +
                           "QPushButton:enabled{background-color: #d3d3d3;} \n" +
                           "QPushButton:disabled{background-color: white;}")

        # Model
        self._model = CheckboardModel()

        # Base widget and layout of the app
        self._root = QWidget()
        self._layout = QVBoxLayout()

        # 1) Toolbar()
        self._toolbar = QWidget()
        self._toolbar.setLayout(Toolbar(self._model))

        # 2) ConfigPanel()
        self._config = QWidget()
        self._config.setLayout(ConfigPanel(self._model))

        # 3) GameGrid()
        self._game_grid = GameGrid(self._model)

        # 4) SimulationPanel()
        self._simulation_panel = QWidget()
        self._simulation_panel.setLayout(SimulationPanel(self._model))

        # Logic to create the layout tree
        self._layout.addWidget(self._toolbar)
        self._layout.addWidget(self._config)
        self._layout.addWidget(self._game_grid)
        self._layout.setAlignment(self._game_grid, Qt.AlignCenter)
        self._layout.addWidget(self._simulation_panel)

        self._root.setLayout(self._layout)
        self._root.show()
        self.exec_()  # Runs the app


# Instantiate and run the application.
app = App(sys.argv)
