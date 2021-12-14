class Cell():
    """
    Cell: holds the position and the current state of a cell

    Parameters:
    i,j    (int): position of the Cell
    state  (str): either "Alive", "Dead" or "Born"

    """

    def __init__(self, i, j, state="Born"):
        """ Initialize the attributes """
        self.i = i
        self.j = j
        self.state = state

    def setState(self, state):
        """ Setter of the state of the Cell """
        assert state in ["Alive", "Born", "Dead"]
        self.state = state

    def getState(self):
        """ Getter of the state of the Cell """
        return self.state

    def copy(self):
        """ Copy constructor of the Cell """
        return Cell(self.i, self.j, self.state)
