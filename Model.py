from PyQt5.QtGui import QColor
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import pickle
import numpy as np
from scipy import signal


class GameColors():
    def __init__(self):
        self.colors = {"Alive": QColor("white"),
                       "Dead": QColor("red"),
                       "Born": QColor("blue")}

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
    cellSizeUpdate = pyqtSignal()

    def __init__(self, cellSize=15, maxX=370, maxY=220):
        super().__init__()
        self.maxX = maxX
        self.maxY = maxY
        self.boardHistory = []
        self.boardHistory.append({})
        self.currentIndex = 0
        self.cellSize = cellSize
        self.colors = GameColors()
        self.countMatrix = np.zeros((self.maxX, self.maxY))
        print(self.countMatrix.shape)

        self.speed = 10
        self.timer = QTimer()
        self.timer.timeout.connect(self.next)
        self.running = False

    def reset(self):
        self.boardHistory = []
        self.boardHistory.append({})
        self.currentIndex = 0
        self.boardUpdate.emit()
        # self.running = False
        self.maxX = 0
        self.maxY = 0

    def saveGame(self, filename):
        with open(filename + '.gol', 'wb') as f:
            pickle.dump(self.boardHistory, f)

    def loadGame(self, filename):
        with open(filename, 'rb') as f:
            self.boardHistory = pickle.load(f)
            self.currentIndex = 0
            self.boardUpdate.emit()

    def observeBoard(self, slot):
        self.boardUpdate.connect(slot)

    def observeColor(self, slot):
        self.colorUpdate.connect(slot)

    def observeCellSize(self, slot):
        self.cellSizeUpdate.connect(slot)

    def setColor(self, key, value):
        self.colors.setColor(key, value)
        self.colorUpdate.emit()

    def getColor(self, key):
        return self.colors.getColor(key)

    def setCellSize(self, cellSize):
        assert cellSize > 0
        self.cellSize = cellSize
        self.cellSizeUpdate.emit()

    def getCellSize(self):
        return self.cellSize

    def setSpeed(self, speed):
        self.speed = speed
        if self.running:
            self.play()

    def getSpeed(self):
        return self.speed

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

        cm = self.countNeighbors()
        x, y = np.nonzero(cm)
        nonZero = set([e for e in zip(x, y)])
        previous = set(self.boardHistory[self.currentIndex].keys())
        toBeChecked = nonZero.union(previous)

        for s in toBeChecked:
            i = s[0]
            j = s[1]
            count = cm[i, j]

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

    def goNext(self):
        if self.currentIndex + 1 < len(self.boardHistory):
            self.currentIndex += 1
        self.boardUpdate.emit()

    def play(self):
        self.running = True
        self.timer.start(1700 / self.speed)

    def pause(self):
        self.running = False
        self.timer.stop()

    def getLeftEnabled(self):
        if self.currentIndex == 0:
            return False
        else:
            return True

    def getRightEnabled(self):
        if self.currentIndex + 1 == len(self.boardHistory):
            return False
        else:
            return True

    def countNeighbors(self):
        self.countMatrix = self.countMatrix * 0
        for key, cell in self.boardHistory[self.currentIndex].items():
            if cell.getState() != "Dead" and key[0] < self.maxX and key[1] < self.maxY:
                print(key)
                self.countMatrix[key[0], key[1]] = 1

        return signal.convolve2d(self.countMatrix, [[1, 1, 1], [1, 0, 1], [1, 1, 1]], 'same')
