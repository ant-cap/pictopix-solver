from puzzle import Cell, Clue, Segment, Line, Puzzle
import utility as u

def diag_str(diag: int) -> str:
        if diag is u.DIAG_DELETE:
            return "delete"
        if diag is u.DIAG_SOLVABLE:
            return "solvable"
        return "none"

class Solver:
    def __init__(self, puzzle : Puzzle):
        self._puzzle = puzzle
        self._turncount = 0

    def run(self):
        self._puzzle.update()

        # first turn
        if not self._turncount:
            segment, diagnosis = self.pick_next_move()
            while diagnosis is u.DIAG_DELETE:
                for cell in segment.cells():
                    if cell.set_state(u.CELL_CROSSED):
                        self._puzzle.trigger_update_at_intersection(cell.position())
                self._puzzle.update()
                segment, diagnosis = self.pick_next_move()
            print("Initial Puzzle: \n{}".format(self._puzzle))
            self._turncount += 1
        
        segment, diagnosis = self.pick_next_move()
        print("diagnosis: {} {}".format(diag_str(diagnosis), segment))

        if diagnosis is u.DIAG_NONE:
            print("Done: \n{}".format(self._puzzle))
            self._puzzle.solve()
            return
        if diagnosis is u.DIAG_DELETE:
            self.execute_delete_segment(segment)
        elif diagnosis is u.DIAG_SOLVABLE:
            self.execute_solvable_segment(segment)
        print("Turn {}: \n{}".format(self._turncount, self._puzzle))
        self._turncount += 1
        
    def pick_next_move(self):
        move = self.delete_segment()
        if move:
            return move, u.DIAG_DELETE
        move = self.solvable_segment()
        if move:
            return move, u.DIAG_SOLVABLE
        return None, u.DIAG_NONE

    ################################
    ##                       #######
    ##  EXECUTION FUNCTIONS  #######
    ##                       #######
    ################################

    def execute_delete_segment(self, segment):
        for cell in segment.cells():
            if cell.set_state(u.CELL_CROSSED):
                self._puzzle.trigger_update_at_intersection(cell.position())

    def execute_solvable_segment(self, segment):
        cells  = segment.cells()
        clues  = segment.clues()
        cell_i = 0
        for i in range(len(clues)):
            for j in range(clues[i].value()):
                if cells[cell_i].set_state(u.CELL_FILLED):
                    self._puzzle.trigger_update_at_intersection(cells[cell_i].position())
                cell_i += 1
            if cell_i == segment.length():
                break
            if cells[cell_i].set_state(u.CELL_CROSSED):
                self._puzzle.trigger_update_at_intersection(cells[cell_i].position())
            cell_i += 1
        assert cell_i == segment.length()

    ################################
    ##                       #######
    ##  NEXT MOVE FUNCTIONS  #######
    ##                       #######
    ################################
        
    # HELPER
    def get_overlap(self, segment):
        if segment.sequences():
            return self.get_overlap_with_sequences(segment)
        cells = segment.cells()
        overlap = [None for cell in cells]
        clues = segment.clues()
        if not len(clues):
            return overlap
        clue_index = 0
        clue_value = clues[clue_index].value() 
        for i in range(len(cells)):
            if clue_value == 0:
                clue_index += 1
                if clue_index >= len(clues):
                    break
                clue_value = clues[clue_index].value()
                continue
            overlap[i] = clues[clue_index]
            clue_value -= 1
        clue_index = len(clues) - 1
        clue_value = clues[clue_index].value()
        hit_range = False
        for i in range(len(cells)-1, -1, -1):
            if clue_value == 0:
                clue_index -= 1
                if clue_index < 0:
                    hit_range = True
                else:
                    clue_value = clues[clue_index].value()
                continue
            if hit_range:
                overlap[i] = None
            else:
                if overlap[i] != clues[clue_index]:
                    overlap[i] = None
        return overlap



    
    def get_overlap_with_sequences(self, segment):
        cells = segment.cells()
        return [None for cell in cells]
        

    def delete_segment(self) -> Segment:
        lines = self._puzzle.lines()
        for l in lines:
            line = lines[l]
            num_segments = len(line.segments())
            if num_segments == 0:
                continue
            if num_segments == 1:
                if line.clues()[0].value() == 0:
                    return line.segments()[0]
            else:
                if line.segments()[0].length() < line.clues()[0].value():
                    return line.segments()[0]
                if line.segments()[-1].length() < line.clues()[-1].value():
                    return line.segments()[-1]
        return None

    def move_partial_solvable_segment(self) -> Segment:
        lines = self._puzzle.lines()
        for l in lines:
            line = lines[l]
            for i in range(len(line.segments())):
                segment = line.segments()[i]
                clues   = segment.clues()
                length  = segment.length()
                tally   = 0
                for j in range(len(clues)):
                    tally += clues[j].value() + 1
                tally -= 1
                if tally > length / 2:
                    return segment

    def solvable_segment(self) -> Segment:
        lines = self._puzzle.lines()
        for l in lines:
            line = lines[l]
            for i in range(len(line.segments())):
                segment = line.segments()[i]
                if segment.solved():
                    continue
                clues   = segment.clues()
                length  = segment.length()
                tally   = 0
                for j in range(len(clues)):
                    tally += clues[j].value() + 1
                tally -= 1
                if tally == length:
                    return segment
        return None
