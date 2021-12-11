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
        self.cellSizeInput = QLineEdit(str(self.model.getCellSize()))
        self.cellSizeInput.setMaxLength(3)
        self.cellSizeInput.setMinimumSize(50, 30)
        self.cellSizeInput.setMaximumSize(50, 30)
        self.cellSizeInput.setValidator(QIntValidator(5, 100)) #  cell size in [5, 100] pixels
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
