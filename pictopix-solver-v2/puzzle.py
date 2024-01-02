import utility as u

'''
Defines a cell on the grid.
    state    : current state of the cell. (empty, filled, crossed)
    position : x/y position of the cell on the grid.
'''
class Cell:
    def __init__(self, x, y):
        self._state = u.CELL_EMPTY
        self._position = (x, y)

    def state(self) -> int:
        return self._state
    
    def set_state(self, state):
        if self._state == state:
            return False
        self._state = state
        return True

    def position(self) -> tuple[int, int]:
        return self._position


    def __repr__(self):
        if self._state == u.CELL_EMPTY:
            return "_"
        elif self._state == u.CELL_FILLED:
            return "█"
        else:
            return "X"
    
    def __str__(self):
        return self.__repr__()

'''
Defines the tomography hints that are initially provided.
    value : the value of the clue.
    index : the index of the clue, where later indexes should appear later in the line
'''
class Clue:
    def __init__(self, value, index):
        self._value = value
        self._index = index

    def value(self) -> int:
        return self._value
    
    def index(self) -> int:
        return self._index
    
    def __repr__(self):
        return "{}{}".format(self._value, u.get_super(self._index))

    def __str__(self):
        return self.__repr__()
    
'''
Defines a sequence of filled cells on a line.
    index  : what cell index the sequence starts on
    length : the length of the sequence 
'''
class Sequence:
    def __init__(self, index, length):
        self._index = index
        self._length = length

    def index(self) -> int:
        return self._index
    
    def length(self) -> int:
        return self._length
    
    def __repr__(self):
        return "{} at {}".format(self._length, self._index)
    
    def __str__(self):
        return self.__repr__()

'''
Defines a sequence of non-crossed cells on a line.
    solved : bool - if the segment is completely filled by a sequence
    cells  : the cells associated with the segment
    length : length of the segment
    clues  : the clues associated with the segment
'''
class Segment:
    def __init__(self, cells):
        self._solved = False
        self._cells = cells
        self._length = len(cells)
        self._clues = []
        self._sequences = self.generate_sequences()
        if len(self._sequences) == 1 and len(cells) == self._sequences[0].length():
            self._solved = True

    def generate_sequences(self):
        sequences = []
        cells = self._cells
        i = 0
        while i < len(cells):
            if cells[i].state() is u.CELL_FILLED:
                length = 0
                j = i
                while cells[j].state() is u.CELL_FILLED:
                    length += 1
                    j += 1
                    if j >= len(cells):
                        break
                sequences.append(Sequence(i, length))
                i = j
            else:
                i += 1
        print("seqs:", sequences)
        return sequences

    def cells(self) -> list[Cell]:
        return self._cells
    
    def length(self) -> int:
        return self._length
    
    def assign_clues(self, clues):
        self._clues = clues

    def clues(self) -> list[Clue]:
        return self._clues
    
    def solved(self) -> bool:
        return self._solved
    
    def __repr__(self):
        return "{} Clues: {}".format(self._cells, self._clues)
    
    def __str__(self):
        return self.__repr__()

'''
Defines a row or column of cells on the grid of a puzzle.
    update   : bool - True if the line needs an update (to generate segments/sequences/clues)
    cells    : the cells that lie on the row/column
    clues    : the clues associated with the line
    segments : the sequences of non-crossed tiles.

'''
class Line:
    def __init__(self, cells, clues):
        self._update = True
        self._cells = cells
        self._clues = [Clue(clues[i], i) for i in range(len(clues))]
        self._segments = []

    def cells(self) -> list[Cell]:
        return self._cells
    
    def clues(self) -> list[Clue]:
        return self._clues
    
    def segments(self) -> list[Segment]:
        return self._segments
    
    def generate_segments(self) -> list[Segment]:
        segments = []
        cells = self._cells
        i = 0
        while cells[i].state() is u.CELL_CROSSED:
            i += 1
            if i >= len(cells):
                return segments
        while i < len(cells):
            segcells = []
            while cells[i].state() is not u.CELL_CROSSED:
                segcells.append(cells[i])
                i += 1
                if i >= len(cells):
                    break
            segments.append(Segment(segcells))
            if i < len(cells):
                while cells[i].state() is u.CELL_CROSSED:
                    i += 1
                    if i >= len(cells):
                        return segments
        return segments
    
    def walk_segments(self, segments: list[Segment], reverse: bool = False):
        assignments = [[] for segment in segments]
        clues = [clue for clue in self._clues]
        if reverse:
            clues.reverse()
            segments = list(reversed(segments))
        for i in range(len(segments)):
            length = segments[i].length()
            tally = 0
            for j in range(len(clues)):
                clue = clues[j]
                tally += clue.value()
                if tally > length:
                    for k in range(j):
                        assignments[i].append(clues.pop(0))
                    break
                if length - tally == 1:
                    tally += 1
                if length == tally:
                    for k in range(j+1):
                        assignments[i].append(clues.pop(0))
                    break
            if length > tally:
                for j in range(len(clues)):
                    assignments[i].append(clues.pop(0))
        if reverse:
            assignments.reverse()
        return assignments


    def assign_clues_to_segments(self, segments: list[Segment]):
        if len(segments) == 1:
            segments[0].assign_clues(self._clues)
        else:
            ftob = self.walk_segments(segments)
            btof = self.walk_segments(segments, reverse=True)
            final = [[] for segment in segments]
            for i in range(len(segments)):
                for j in range(len(ftob[i])):
                    if ftob[i][j] in btof[i]:
                        final[i].append(ftob[i][j])
            for i in range(len(segments)):
                segments[i].assign_clues(final[i])
        self._segments = segments
        self._update = False

    def solved(self) -> bool:
        return False
    
    def update(self) -> bool:
        return self._update
    
    def trigger_update(self):
        if not self._update:
            self._update = True

    def __repr__(self):
        s = ""
        for c in self._cells:
            s += str(c) + " "
        s = s[:-1]
        s += " {}".format(self._clues)

        return s
    
    def __str__(self):
        return self.__repr__()

'''
Defines a Nonogram/Picross puzzle. (to change)
    solved  : bool         - True if solved
    dim_x   : int          - how many columns
    dim_y   : int          - how many rows
    grid    : list[[Cell]] - the grid of cells
    clues_x : list[int]    - clues for x axis
    clues_y : list[int]    - clues for y axis
    lines   : dict(Line)   - each line in the puzzle
'''
class Puzzle:
    def __init__(self, dx, dy):
        self._solved = False
        self._dim_x = dx
        self._dim_y = dy
        self._grid = []
        for x in range(dx):
            column = []
            for y in range(dy):
                column.append(Cell(x, y))
            self._grid.append(column)

        if dx == 10:
            self._clues_x = [[0], [0], [1], [2], [1,1,2], [1,2,2], [4], [2], [0], [0]]
            self._clues_y = [[0], [4], [2, 2], [2], [2], [2], [0], [2], [2], [0]]
        else:
            self._clues_x = [[2,1], [1,2], [1,1], [1,2], [2,1]]
            self._clues_y = [[3], [1,1], [5], [1,1], [1,1]]
            #self._clues_x = [[1], [2], [2,1], [1], [1]]
            #self._clues_y = [[3], [1], [0], [3], [1]]

        self._lines = {}
        for i in range(len(self._clues_x)*2):
            index = i if i < len(self._clues_x) else i-len(self._clues_x)
            axis = u.AXIS_X if index == i else u.AXIS_Y
            cells = []
            if axis == u.AXIS_X:
                for y in range(len(self._clues_y)):
                    cells.append(self._grid[index][y])
                self._lines[axis, index] = Line(cells, self._clues_x[index])
            elif axis == u.AXIS_Y:
                for x in range(len(self._clues_x)):
                    cells.append(self._grid[x][index])
                self._lines[axis, index] = Line(cells, self._clues_y[index])

    def __repr__(self):
        message = ""
        len_vert_clues = 0
        len_hori_clues = 0
        series = self._lines
        axis = u.AXIS_Y
        for i in range(self._dim_y):
            line = series[axis, i]
            if len_hori_clues < len(line.clues()):
                len_hori_clues = len(line.clues())
        axis = u.AXIS_X
        for i in range(self._dim_x):
            line = series[axis, i]
            if len_vert_clues < len(line.clues()):
                len_vert_clues = len(line.clues())

        for j in range(len_vert_clues):
            row = ""
            for clue in range(len_hori_clues):
                row += "   "
            row += " "
            for i in range(self._dim_x):
                line = series[axis, i]
                clues = [clue for clue in line.clues()]
                clues.reverse()
                if j < len(clues):
                    row += str(clues[j])
                else:
                    row += "  "
                if i < self._dim_x:
                    row += " "
            message = row + "\n" + message
        axis = u.AXIS_Y
        for i in range(self._dim_y):
            row = ""
            line = series[axis, i]
            clues = [clue for clue in line.clues()]
            clues.reverse()
            for j in range(len_hori_clues-1, -1, -1):
                if j < len(clues):
                    row += str(clues[j])
                else:
                    row += "  "
                if j < len_hori_clues:
                    row += " "
            row += " "
            cells = line.cells()
            for j in range(len(cells)):
                row += str(cells[j]) + " "
                if j < len(cells) - 1:
                    row += " "
            message += row
            if i < self._dim_y:
                message += "\n"

        return "\n" + message + "\n"

    def update(self):
        for line in self._lines:
            if self._lines[line].update():
                self._lines[line].assign_clues_to_segments(self._lines[line].generate_segments())

    def lines(self) -> dict:
        return self._lines
    
    def solved(self) -> bool:
        if not self._solved:
            for line in self._lines:
                if not self._lines[line].solved():
                    return self._solved
            self._solved = True
        return self._solved
    
    def solve(self):
        self._solved = True

    def trigger_update_at_intersection(self, pos : tuple[int, int]):
        self._lines[u.AXIS_X, pos[0]].trigger_update()
        self._lines[u.AXIS_Y, pos[1]].trigger_update()
        print("update triggered at {} {}".format(pos[0], pos[1]))

def main():
    p = Puzzle(5, 5)

if __name__ == "__main__":
    main()