from PyQt5.QtGui import QColor


class GameColors():
    """
    GameColors: holds the colors that are in use in the checkboard

    Attributes:
    colors    (dict): the keys are the status of a cell (either "Alive", "Dead" or "Born"),
                      the values are the QColor() associated to that status, which will be used in the View.

    """

    def __init__(self):
        """ Creates the dictionary of pairs {status: color} """
        self.colors = {"Alive": QColor("white"),
                       "Dead": QColor("red"),
                       "Born": QColor("blue")}

    def setColor(self, key, value):
        """ Setter for the color associated to the key """
        assert key in self.colors.keys() and type(value) == QColor
        self.colors[key] = value

    def getColor(self, key):
        """ Getter for the color associated to the key """
        assert key in self.colors.keys()
        return self.colors[key]
