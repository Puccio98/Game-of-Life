from PyQt5.QtGui import QColor
from PyQt5.QtCore import QObject, pyqtSignal

default_colors = {
    "Alive": QColor("white"),
    "Dead": QColor("red"),
    "Born": QColor("blue")
}


class InterfaceColors():
    def __init__(self):
        self.colors = {"Alive": QColor("white"),
                       "Dead": QColor("red"),
                       "Born": QColor("blue")
                       }

    def setColor(self, key, value):
        pass


class Cell():
    def __init__(self, i, j, state="Born"):
        self.i = i
        self.j = j
        self.state = state

    def setState(self, state):
        self.state = state

    def getState(self):
        return self.state

    def copy(self):
        return Cell(self.i, self.j, self.state)


class Checkboard(QObject):
    boardUpdate = pyqtSignal()

    def __init__(self, rows, cols):
        super().__init__()
        self.boardHistory = []
        self.boardHistory.append({})
        self.currentIndex = 0
        self.rows = rows
        self.cols = cols

    def observe(self, slot):
        self.boardUpdate.connect(slot)

    def getBoard(self):
        return self.boardHistory[self.currentIndex]

    def addCell(self, i, j):
        if (i, j) not in self.boardHistory[self.currentIndex].keys():
            self.boardHistory[self.currentIndex][(i, j)] = Cell(i, j)
            self.boardUpdate.emit()

    def modifyCell(self, i, j, state):
        if (i, j) in self.boardHistory[self.currentIndex].keys():
            self.boardHistory[self.currentIndex][(i, j)].setState(state)
            self.boardUpdate.emit()

    def removeCell(self, i, j):
        if (i, j) in self.boardHistory[self.currentIndex].keys():
            del self.boardHistory[self.currentIndex][(i, j)]
            self.boardUpdate.emit()

    def next(self):
        if self.currentIndex + 1 < len(self.boardHistory):
            self.boardHistory = self.boardHistory[0:self.currentIndex + 1]
        updatedBoard = {}

        for i in range(self.rows):
            for j in range(self.cols):
                count = self._countNeighbors(i, j)

                if (i, j) in self.boardHistory[self.currentIndex].keys():
                    if self.boardHistory[self.currentIndex][(i, j)].getState() != "Dead":
                        if count <= 1:
                            updatedBoard[(i, j)] = self.boardHistory[self.currentIndex][(i, j)].copy()
                            updatedBoard[(i, j)].setState("Dead")
                        elif count >= 4:
                            updatedBoard[(i, j)] = self.boardHistory[self.currentIndex][(i, j)].copy()
                            updatedBoard[(i, j)].setState("Dead")
                        else:
                            updatedBoard[(i, j)] = self.boardHistory[self.currentIndex][(i, j)].copy()
                            updatedBoard[(i, j)].setState("Alive")

                else:
                    if count == 3 and (i, j):
                        updatedBoard[(i, j)] = Cell(i, j)

        self.boardHistory.append(updatedBoard)
        self.currentIndex += 1
        # self.history.append(self.board)
        self.boardUpdate.emit()

    def goBack(self):
        self.currentIndex -= 1
        if self.currentIndex < 0:
            self.currentIndex = 0
        self.boardUpdate.emit()

    def _countNeighbors(self, i, j):
        count = 0
        positions = [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
                     (i, j - 1), (i, j + 1),
                     (i + 1, j - 1), (i + 1, j), (i + 1, j + 1)]

        for p in positions:
            if p in self.boardHistory[self.currentIndex].keys() and self.boardHistory[self.currentIndex][p].getState() != "Dead":
                count += 1
        return count
