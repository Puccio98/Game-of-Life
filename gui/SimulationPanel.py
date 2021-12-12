from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSlider
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


# 4) SimulationPanel()
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
