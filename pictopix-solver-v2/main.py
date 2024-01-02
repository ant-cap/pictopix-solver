from utility import AXIS_X, AXIS_Y, CELL_EMPTY, CELL_CROSSED, CELL_FILLED
from puzzle import Cell, Clue, Line, Puzzle
from solver import Solver

def main():
    puz = Puzzle(5, 5)
    solver = Solver(puz)

    while not puz.solved():
        solver.run()

if __name__ == "__main__":
    main() 