from PyQt5.QtWidgets import QMessageBox, QAction, QFileDialog, QApplication, QMenu, QMenuBar, QHBoxLayout
from PyQt5.QtGui import QIcon


# 1) Toolbar()
class Toolbar(QHBoxLayout):
    """ Toolbar: presents the user the save, load and help funtionalities

    Parameters:
    model (CheckboardModel): the model, in order to make use of primitives to save/load Games

    """

    def __init__(self, model, ** kwargs):
        """ Generates the toolbar layout and connects each button to the corresponding action """

        super().__init__(**kwargs)
        self.model = model
        self._menu_bar = QMenuBar()

        self._file = QMenu("&File")
        self._menu_bar.addMenu(self._file)

        self._save = QAction(QIcon("./Icons/iconmonstr-save-1.svg"), "Save Game")
        self._save.triggered.connect(self.saveAction)
        self._file.addAction(self._save)

        self._load = QAction(QIcon("./Icons/iconmonstr-folder-21.svg"), "Load")
        self._load.triggered.connect(self.loadAction)
        self._file.addAction(self._load)

        self._file.addSeparator()

        self._quit = QAction("Quit")
        self._quit.triggered.connect(self.quitAction)
        self._file.addAction(self._quit)

        self._help = QAction("&Help")
        self._help.triggered.connect(self.helpDialog)
        self._menu_bar.addAction(self._help)

        self.setMenuBar(self._menu_bar)

    def saveAction(self):
        """ Save action: displays dialog to gather file name and calls the model to save the game with the selected one """
        file = QFileDialog.getSaveFileName(caption="Save Game", filter="Game of Life (*.gol)")
        self.model.saveGame(file[0])

    def loadAction(self):
        """ Load action: displays dialog to gather the file.gol to load """
        file = QFileDialog.getOpenFileName(caption="Load Game", filter="Game of Life (*.gol)")
        self.model.loadGame(file[0])

    def quitAction(self):
        """ Quit action: calls the QApplication exit method """
        QApplication.exit()

    def helpDialog(self):
        """ Help action: displays the help dialog """
        HelpDialog()


class HelpDialog(QMessageBox):
    """HelpDialog: dialog with Game of Life wiki link and the commands of this implementation"""

    def __init__(self):
        """ Creates the the help dialog and its content """
        super().__init__()
        self.setWindowTitle("Help")
        self.setMinimumSize(100, 200)

        self.setText("<h2>Conway's Game of Life</h2>")
        link = "https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life"
        self.setInformativeText("<a href=\"" + link + "\">Here</a> you can find how the game works."
                                + "<h3>Commands:</h3>"
                                + "<li> <b>Left Click:</b> add cells"
                                + "<li> <b>Right Click:</b> remove cells"
                                + "<li> <b>Enter over Cell Size:</b> update cell size")

        self.exec_()
