from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QToolButton, QLabel, QColorDialog
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt


# 2) ConfigPanel
class ConfigPanel(QHBoxLayout):
    """ Toolbar: presents the user Cell Size modification functionality and custom Game Color functionalities

    Parameters:
    model (CheckboardModel): the model, in order to make use of primitives to modify Cell Size and Game Colors

    """

    def __init__(self, model, **kwargs):
        """ Generate the ConfigPanel layout and connects each line-edit and button to its corresponding functionality """

        super().__init__(**kwargs)
        self.model = model

        # Line Edit to manage Cell Size
        self.cellSizeInput = QLineEdit(str(self.model.getCellSize()))  # get from the model the first cell size
        self.cellSizeInput.setMaxLength(3)
        self.cellSizeInput.setMinimumSize(50, 30)
        self.cellSizeInput.setMaximumSize(50, 30)
        self.cellSizeInput.setValidator(QIntValidator())  # int only
        self.cellSizeInput.returnPressed.connect(self.enterNewCellSize)  # action triggered on "ENTER"

        self.addWidget(QLabel("Cell Size:"), alignment=Qt.AlignLeft)
        self.addWidget(self.cellSizeInput, alignment=Qt.AlignLeft)

        # Feedback label: when the selected Cell Size is either too large or too small we show this label
        self.feedback = QLabel("Cell size has to be in [4, 100] interval!")
        self.feedback.setStyleSheet("*{color: red}")  # an error should be in red
        self.feedback.setVisible(False)
        self.addWidget(self.feedback, alignment=Qt.AlignLeft)
        self.addStretch()

        # Color controllers (3 couples QLabel+ColorButton)
        color_controllers_names = ["Alive", "Dead", "Born"]
        for n in color_controllers_names:
            self.addWidget(QLabel(n + ":"), alignment=Qt.AlignRight)
            self.addWidget(ColorButton(name=n, model=self.model), alignment=Qt.AlignLeft)

    def enterNewCellSize(self):
        """ Function called when a new Cell Size is entered: if the new value is
        inside the [4, 100] bound we set the new cell size in the model,
        otherwise we show an error message."""

        newCellSize = int(self.cellSizeInput.text())
        if 4 <= newCellSize and newCellSize <= 100:
            self.feedback.setVisible(False)
            self.model.setCellSize(newCellSize)  # If the newCellSize respects the bounds we update the model
        else:
            self.feedback.setVisible(True)


class ColorButton(QToolButton):
    """ ColorButton: button to control one game color

    Parameters:
    name  (str): name of the button, could be either "Alive", "Dead" or "Born"
    model (CheckboardModel): the model, in order to interact with Game Colors in the Model

    """

    def __init__(self, name, model, **kwargs):
        """ Creates the button and connects to the model """

        super().__init__(**kwargs)
        self.model = model
        self.name = name

        self.alignColor()
        self.clicked.connect(self.handleClick)
        self.model.observeColor(self.alignColor)

    def handleClick(self):
        """ On a click we get the new color from a QColorDialog and we update the model """
        newColor = QColorDialog.getColor()
        self.model.setColor(self.name, newColor)

    def alignColor(self):
        """ Once the model is updated we get notified here, and we update our color"""
        color = self.model.getColor(self.name)
        self.setStyleSheet("background-color: " + color.name())
