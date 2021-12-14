from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from scipy import signal
import numpy as np
import pickle

from Model.Cell import Cell
from Model.GameColors import GameColors


class CheckboardModel(QObject):
    """
    CheckboardModel: holds all the data needed for the app to run, the logic to update the view and the methods to manage the state.
    In our MVC this is the Model.

    Main Attributes:
    boardHistory      (list): holds all the boards that were displayed in the current game. Each board is a dictionary,
                              in which the keys are tuples (i,j): if the key (i,j) is in the dictionary it means
                              that such position is not empty, and the cell status is in the CurrentBoard[(i,j)],
                              which is an object of Cell() type.

    currentIndex       (int): integer that holds the index of the boardHistory that contains the board which is displayed now.

    countMatrix (np.ndarray): numpy matrix that is used to count the neighbors, in order to get the next board in the board history.
                              Its dimensions are (maxX,maxY) because we consider a finite board in this implementation. As it is
                              not possible to scroll the view, we cannot draw cells outside of the (maxX,maxY), and any computation
                              that would lead to a new cell outside of the boundaries is not considered.

    colors      (GameColors): object that holds the colors of the cells in the QGraphicsView.

    Other attributes' details are offered in the __init__() implementation.
    """

    boardUpdate = pyqtSignal()  # signal to notify the board content has changed
    colorUpdate = pyqtSignal()  # signal to notify an interface color of the board has changed
    cellSizeUpdate = pyqtSignal()  # signal to notify the cellSize on the board has changed

    def __init__(self, cellSize=15, cellSizeLB=4, cellSizeUB=100, maxX=370, maxY=220, speed=10, minSpeed=2, maxSpeed=30):
        """ Creates all the attributes needed for the app to run """
        super().__init__()
        self.cellSize = cellSize  # current cell size in the view (in pixels)
        self.cellSizeLB = cellSizeLB  # cell size Lower Bound
        self.cellSizeUB = cellSizeUB  # cell size Upper Bound

        self.boardHistory = []  # history of the boards of the current game
        self.boardHistory.append({})  # the first board is empty: an empty dict.
        self.currentIndex = 0

        # countMatrix to count efficiently the neighbors
        self.maxX = maxX
        self.maxY = maxY
        self.countMatrix = np.zeros((self.maxX, self.maxY))

        self.colors = GameColors()  # holds the colors of the view and exposes primitives to handle those

        # Attributes to handle speed settings
        self.speed = speed  # default: 10fps
        self.minSpeed = minSpeed  # 2fps
        self.maxSpeed = maxSpeed  # 30fps
        self.timer = QTimer()  # timer to handle auto-update of the simulation
        self.timer.timeout.connect(self.next)  # when the timer hits we call the .next() method
        self.running = False  # bool that holds if we're currently running the simulation or not

    # SIGNALS
    def observeBoard(self, slot):
        """ Method to observe (from outside) when the board is updated """
        self.boardUpdate.connect(slot)

    def observeColor(self, slot):
        """ Method to observe (from outside) when a color in the interface is updated """
        self.colorUpdate.connect(slot)

    def observeCellSize(self, slot):
        """ Method to observe (from outside) when the cellSize is updated """
        self.cellSizeUpdate.connect(slot)

    # SAVE/LOAD
    def saveGame(self, filename):
        """ Save the current game to .gol file. We just write the boardHistory to file """
        if filename != "":
            with open(filename + '.gol', 'wb') as f:
                pickle.dump(self.boardHistory, f)

    def loadGame(self, filename):
        """ Load a game from a file: we load the boardHistory and emit that the board has changed """
        if filename != "":
            with open(filename, 'rb') as f:
                self.boardHistory = pickle.load(f)
                self.currentIndex = 0
                self.boardUpdate.emit()

    # CELL SIZE
    def setCellSize(self, cellSize):
        """ Called when a new cellSize is selected: we make sure that the selected value respects the bounds and we emit the corresponding signal """
        assert self.cellSizeLB <= cellSize and cellSize <= self.cellSizeUB
        self.cellSize = cellSize
        self.cellSizeUpdate.emit()

    def getCellSize(self):
        """ Getter for cellSize """
        return self.cellSize

    def getCellSizeLB(self):
        """ Getter for cellSize lower bound """
        return self.cellSizeLB

    def getCellSizeUB(self):
        """ Getter for cellSize upper bound """
        return self.cellSizeUB

    # VIEW COLORS
    def setColor(self, key, value):
        """ When a new color is picked for a certain cell-state we delegate the GameColor() object to update, and we notify who observe such changes """
        self.colors.setColor(key, value)
        self.colorUpdate.emit()

    def getColor(self, key):
        """ Returns the current color of the given key through delegation to GameColor() """
        return self.colors.getColor(key)

    # BOARD MANAGEMENT
    def getBoard(self):
        """ Returns the current board so we can render it """
        return self.boardHistory[self.currentIndex]

    def addCell(self, i, j):
        """ Adds a new Cell() to the current board, considering the cases of empty position and the one where the Cell is "Dead" """
        if (i, j) not in self.boardHistory[self.currentIndex].keys():
            self.boardHistory[self.currentIndex][(i, j)] = Cell(i, j)
            self.boardUpdate.emit()
        elif self.boardHistory[self.currentIndex][(i, j)].getState() == "Dead":
            self.boardHistory[self.currentIndex][(i, j)] = Cell(i, j)
            self.boardUpdate.emit()

    def removeCell(self, i, j):
        """ Removes a cell in position (i,j) if this is in the current board """
        if (i, j) in self.boardHistory[self.currentIndex].keys():
            del self.boardHistory[self.currentIndex][(i, j)]
            self.boardUpdate.emit()

    def next(self):
        """ Board update logic: creates the board at the next iteration in the Game of Life simulation """

        """ Manage the boardHistory: if we go back in the timeline and press play we want all the future steps to be evaluated from
        the beginning, thus removing the future configurations """
        if self.currentIndex + 1 < len(self.boardHistory):
            self.boardHistory = self.boardHistory[0:self.currentIndex + 1]

        updatedBoard = {}  # new board (empty at the beginning)

        cm = self.__countNeighbors()  # matrix holding in [i,j] the neighborhood count of the cell in position (i,j)
        x, y = np.nonzero(cm)  # we take only the non-zero values of such count matrix, as those only will be new cells
        nonZero = set([e for e in zip(x, y)])
        previous = set(self.boardHistory[self.currentIndex].keys())

        """ The positions (i, j) to be checked are the ones that have a neighbor count > 0 or
        that previously where not empty. In this way we cycle over less positions (i,j) """
        toBeChecked = nonZero.union(previous)

        for s in toBeChecked:
            i = s[0]
            j = s[1]
            count = cm[i, j]

            if (i, j) in self.boardHistory[self.currentIndex].keys() and self.boardHistory[self.currentIndex][(i, j)].getState() != "Dead":
                # we're considering here the case of (i,j) was in the previous board and not "Dead"
                if count <= 1:
                    # dies because of loneliness
                    updatedBoard[(i, j)] = self.boardHistory[self.currentIndex][(i, j)].copy()
                    updatedBoard[(i, j)].setState("Dead")
                elif count >= 4:
                    # dies because of overpopulation
                    updatedBoard[(i, j)] = self.boardHistory[self.currentIndex][(i, j)].copy()
                    updatedBoard[(i, j)].setState("Dead")
                else:
                    # lives if count = 2 or 3
                    updatedBoard[(i, j)] = self.boardHistory[self.currentIndex][(i, j)].copy()
                    updatedBoard[(i, j)].setState("Alive")

            else:
                # Here we're considering a (i,j) that is not in the previous board or it was "Dead"
                if count == 3:
                    # a new cell is born
                    updatedBoard[(i, j)] = Cell(i, j)

        self.boardHistory.append(updatedBoard)
        self.currentIndex += 1
        self.boardUpdate.emit()

    def __countNeighbors(self):
        """ Utility method to count the amount of neighbors of each cell: starting from an empty countMatrix
        we place a 1 on each position that has a Cell not "Dead", then we use convolution over such matrix to count
        the amount of neighbors in the 8 adjacent cells for each position. Doing so we get a matrix which is returned """

        self.countMatrix = self.countMatrix * 0
        for key, cell in self.boardHistory[self.currentIndex].items():
            if cell.getState() != "Dead" and key[0] < self.maxX and key[1] < self.maxY:
                self.countMatrix[key[0], key[1]] = 1

        return signal.convolve2d(self.countMatrix, [[1, 1, 1], [1, 0, 1], [1, 1, 1]], 'same')

    # SIMULATION METHODS
    def goBack(self):
        """ Method to go back to the previous configuration in the game history """
        self.currentIndex -= 1
        if self.currentIndex < 0:
            self.currentIndex = 0
        self.boardUpdate.emit()

    def goNext(self):
        """ Method to go to the next configuration in the game history """
        if self.currentIndex + 1 < len(self.boardHistory):
            self.currentIndex += 1
        self.boardUpdate.emit()

    def play(self):
        """ Method to start the simulation, activating the timer update """
        self.running = True
        self.timer.start(1000 / self.speed)  # so that the speed is the fps

    def pause(self):
        """ Method to pause the simulation, stopping the timer """
        self.running = False
        self.timer.stop()

    def reset(self):
        """ Method to reset the simulation, clearing the history """
        self.boardHistory = []
        self.boardHistory.append({})
        self.currentIndex = 0
        self.boardUpdate.emit()

    def getLeftEnabled(self):
        """ Getter of the state of the Arrow-Left navigation button: if there is no previous state it has to be inactive """
        if self.currentIndex == 0:
            return False  # False means inactive button
        else:
            return True

    def getRightEnabled(self):
        """ Getter of the state of the Arrow-Right navigation button: if there is no future state in the history
        it has to be inactive """
        if self.currentIndex + 1 == len(self.boardHistory):
            return False  # False means inactive button
        else:
            return True

    def setSpeed(self, speed):
        """ Called when the slider is modified: we set the new speed and, in case we're currently running the simulation,
        we play the game, so that the timer is modified accordingly """
        self.speed = speed
        if self.running:
            self.play()

    def getSpeed(self):
        """ Getter for speed """
        return self.speed

    def getMinSpeed(self):
        """ Getter for speed min value """
        return self.minSpeed

    def getMaxSpeed(self):
        """ Getter for speed max value """
        return self.maxSpeed
