from PyQt5.QtGui import QColor
from PyQt5.QtCore import QObject, pyqtSignal


class InterfaceColors():
    def __init__(self):
        self.colors = {"Alive": QColor("white"),
                       "Dead": QColor("red"),
                       "Born": QColor("blue")
                       }

    def setColor(self, key, value):
        assert key in self.colors.keys() and type(value) == QColor
        self.colors[key] = value

    def getColor(self, key):
        assert key in self.colors.keys()
        return self.colors[key]


class Cell():
    def __init__(self, i, j, state="Born"):
        self.i = i
        self.j = j
        self.state = state

    def setState(self, state):
        assert state in ["Alive", "Born", "Dead"]
        self.state = state

    def getState(self):
        return self.state

    def copy(self):
        return Cell(self.i, self.j, self.state)


class CheckboardModel(QObject):
    boardUpdate = pyqtSignal()
    colorUpdate = pyqtSignal()
    gridSizeUpdate = pyqtSignal()

    def __init__(self, N):
        super().__init__()
        self.boardHistory = []
        self.boardHistory.append({})
        self.currentIndex = 0
        self.N = N
        self.colors = InterfaceColors()
        self.speed = 0

    def observeBoard(self, slot):
        self.boardUpdate.connect(slot)

    def observeColor(self, slot):
        self.colorUpdate.connect(slot)

    def observeGridSize(self, slot):
        self.gridSizeUpdate.connect(slot)

    def setColor(self, key, value):
        self.colors.setColor(key, value)
        self.colorUpdate.emit()

    def getColor(self, key):
        return self.colors.getColor(key)

    def setN(self, N):
        assert N > 0
        self.N = N
        self.gridSizeUpdate.emit()

    def getN(self):
        return self.N

    def setSpeed(self, speed):
        print(speed)
        self.speed = speed

    def getBoard(self):
        return self.boardHistory[self.currentIndex]

    def addCell(self, i, j):
        if (i, j) not in self.boardHistory[self.currentIndex].keys():
            self.boardHistory[self.currentIndex][(i, j)] = Cell(i, j)
            self.boardUpdate.emit()
        elif self.boardHistory[self.currentIndex][(i, j)].getState() == "Dead":
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

        for i in range(self.N):
            for j in range(self.N):
                count = self._countNeighbors(i, j)

                if (i, j) in self.boardHistory[self.currentIndex].keys() and self.boardHistory[self.currentIndex][(i, j)].getState() != "Dead":
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
                    if count == 3:
                        updatedBoard[(i, j)] = Cell(i, j)

        self.boardHistory.append(updatedBoard)
        self.currentIndex += 1
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
