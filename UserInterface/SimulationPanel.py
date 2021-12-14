from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSlider
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


# 4) SimulationPanel()
class SimulationPanel(QHBoxLayout):
    """
    Simulation Panel: presents the user the simulation controllers: play/pause/reset, speed settings and
    options to navigate the history of the board (arrows left/right).

    Parameters:
    model (CheckboardModel): the model, in order to make use of primitives to control the simulation

    """

    def __init__(self, model, **kwargs):
        """ Creates the set of buttons and the speed slider, and connect them to the model """

        super().__init__(**kwargs)

        self.model = model
        self.model.observeBoard(self.alignArrowStatus)  # To keep arrow status aligned with current status

        # Arrow-Left
        self._left = QPushButton(QIcon("./Icons/iconmonstr-arrow-left.svg"), "")
        self._left.clicked.connect(self.clickLeft)
        self._left.setEnabled(False)
        self._left.setMinimumSize(40, 30)

        # Arrow-Right
        self._right = QPushButton(QIcon("./Icons/iconmonstr-arrow-12.svg"), "")
        self._right.clicked.connect(self.clickRight)
        self._right.setEnabled(False)
        self._right.setMinimumSize(40, 30)

        # Pause
        self._pause = QPushButton(QIcon("./Icons/iconmonstr-media-control-49.svg"), "")
        self._pause.clicked.connect(self.clickPause)
        self._pause.setEnabled(False)
        self._pause.setMinimumSize(40, 30)

        # Play
        self._play = QPushButton(QIcon("./Icons/iconmonstr-media-control-48.svg"), "")
        self._play.clicked.connect(self.clickPlay)
        self._play.setMinimumSize(40, 30)

        # Speed slider
        self._speed = QSlider(Qt.Horizontal)
        self._speed.setMaximumSize(250, 50)
        self._speed.setMinimum(self.model.getMinSpeed())
        self._speed.setMaximum(self.model.getMaxSpeed())
        self._speed.setValue(self.model.getSpeed())
        self._speed.valueChanged[int].connect(self.sliderModified)

        # Reset
        self._reset = QPushButton("Reset")
        self._reset.clicked.connect(self.clickReset)
        self._reset.setMinimumSize(40, 30)

        # Build the interface structure
        self.addWidget(self._left)
        self.addWidget(self._right)
        self.addWidget(self._pause)
        self.addWidget(self._play)
        self.addStretch()
        self.addWidget(QLabel("Speed:"))
        self.addWidget(self._speed)
        self.addStretch()
        self.addWidget(self._reset)

    def clickLeft(self):
        """ On a click to Arrow-Lef we go to the previous configuration in the board history
        (if this is not possible this button is not active thanks to alignArrowStatus,
         which is called on each board update) """
        self.model.goBack()

    def clickRight(self):
        """ On a click to Arrow-Right we go to the next configuration in the board history
        (if this is not possible this button is not active thanks to alignArrowStatus,
         which is called on each board update) """
        self.model.goNext()

    def alignArrowStatus(self):
        """ Method connected to board update in the model, aligns the status of the two arrows button,
        in order to behave accordingly to the navigation of the history """
        self._left.setEnabled(self.model.getLeftEnabled())
        self._right.setEnabled(self.model.getRightEnabled())

    def clickPause(self):
        """ On a click to Pause button we pause the game, disable this button and enable the play button """
        self.model.pause()
        self._pause.setEnabled(False)
        self._play.setEnabled(True)

    def clickPlay(self):
        """ On a click to Play button we play the game, disable this button and enable the pause button """
        self.model.play()
        self._play.setEnabled(False)
        self._pause.setEnabled(True)

    def clickReset(self):
        """ On a click to Reset button we pause the game and reset the simulation delegating the model """
        self.clickPause()
        self.model.reset()

    def sliderModified(self, value):
        """ When the slider is modified we set the model speed to the value the slider is configured """
        self.model.setSpeed(value)
