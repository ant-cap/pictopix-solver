import pyautogui as ag
from pyscreeze import ImageNotFoundException
from PIL import Image
from operator import itemgetter
from os import listdir

### constants ###
DIMENSIONADR = "references/dimensions/"
GRIDADR      = "references/grids/"
NUMBERADR    = "references/numbers/"
TILEADR      = "references/tiles/"
MISCADR      = "references/misc/"
MAXIMIZE_GAME_TAB = True

# tile states
EMPTY   = 0
FILLED  = 1
CROSSED = 2

# axis alias
AXIS_X = 0
AXIS_Y = 1

# array diagnostics
NO_DIAG        = 0
ALREADY_SOLVED = 1
CAN_CROSS      = 2
CAN_FILL       = 3
EDGE_CASE      = 4

# edge case types

class Sequence():
        def __init__(self, index, value):
            self._index = index
            self._value = value
        
        def index(self):
            return self._index
        
        def value(self):
            return self._value
        
        def __repr__(self):
            return "{}.{}".format(self._index, self._value)

class Puzzle(object):

    class Sequence():
        def __init__(self, index, value):
            self._index = index
            self._value = value
        
        def index(self):
            return self._index
        
        def value(self):
            return self._value
        
        def __repr__(self):
            return "{}.{}".format(self._index, self._value)

    class TileArray(object):

        class Space(object):
            def __init__(self, tarray, indices):
                self._tiles = tarray.gt()[indices[0]:indices[1]]
                self._size = indices[1] - indices[0]
                self._clues = []
                self._occupied = False
                self._solved = True
                self._new = True
                self._delete = False
                for t in self._tiles:
                    if not self._occupied:
                        if t.gs() is FILLED:
                            self._occupied = True
                    if t.gs() is not FILLED:
                        self._solved = False

            def tiles(self):
                return self._tiles
            
            def size(self):
                return self._size
            
            def set_clues(self, clues):
                self._clues = clues

            def clues(self):
                return self._clues
            
            def occupied(self):
                return self._occupied
            
            def solved(self):
                return self._solved
            
            def delete(self):
                return self._delete
            
            def delete_me(self):
                self._delete = True

            def new(self):
                if self._new:
                    self._new = False
                    return True
                

            def __repr__(self):
                s = "["
                for i in range(len(self.tiles())):
                    s += str(self._tiles[i])
                    if i < len(self.tiles()) - 1:
                        s += ", "
                s += "] |"
                for i in range(len(self.clues())):
                    s += str(self._clues[i])
                    if i < len(self._clues) - 1:
                        s += ", "
                s += "|"
                return s
            
            def __str__(self):
                s = "["
                for i in range(len(self.tiles())):
                    s += str(self._tiles[i])
                    if i < len(self.tiles()) - 1:
                        s += ", "
                s += "] |"
                for i in range(len(self.clues())):
                    s += str(self._clues[i])
                    if i < len(self._clues) - 1:
                        s += ", "
                s += "|"
                return s
            
        def __init__(self, tiles=[]):
            self._tiles = tiles
            self._spaces = []
            self._solved = False
            self._update = True

        def get_spaces(self):
            return self._spaces

        def set_to_update(self):
            if self._update == False:
                self._update = True

        def update(self, clues):

            def generate_spaces():
                spaces = []
                tiles = self.gt()
                flag = False
                start = 0
                for i in range(len(tiles)):
                    if not flag:
                        if tiles[i].gs() is CROSSED:
                            continue
                        flag = True
                        start = i
                    else:
                        if tiles[i].gs() is CROSSED:
                            spaces.append(self.Space(self, (start, i)))
                            flag = False
                if flag:
                    spaces.append(self.Space(self, (start, i+1)))

                self._spaces = spaces

            def assign_clues():
                seqs = []
                for i in range(len(clues)):
                    seqs.append(Sequence(i, clues[i]))

                spaces = self.get_spaces()
                spaces_copy = [s for s in self.get_spaces()]
                offset = 0
                while True:
                    if not len(spaces_copy):
                        return
                    if spaces[0].size() < clues[0]:
                        spaces[0].delete_me()
                        spaces_copy.pop(0)
                        offset+=1
                    elif spaces[-1].size() < clues[-1]:
                        spaces[-1].delete_me()
                        spaces_copy.pop()
                    else:
                        break

                if len(spaces_copy) > len(clues):
                    occ = []
                    unocc = []
                    for i in range(len(spaces)):
                        if spaces[i].delete():
                            continue
                        if spaces[i].occupied():
                            occ.append(i)
                        else:
                            unocc.append(i)
                    if len(occ) == len(clues):
                        for i in unocc:
                            spaces[i].delete_me()

                seqscopy = [s for s in seqs]
                print(seqscopy)

                left = [[] for s in spaces_copy]
                for i in range(len(spaces_copy)):
                    size = spaces_copy[i].size()
                    tally = 0
                    for j in range(len(seqscopy)):
                        sequence = seqscopy[j]
                        tally += sequence.value()
                        if tally > size:
                            for k in range(j):
                                print("for {} in range {}".format(k,j))
                                left[i].append(seqscopy.pop(0))
                            break
                        if size - tally == 1:
                            tally += 1
                        if size == tally:
                            for k in range(j+1):
                                print("for {} in range {}+1".format(k, j))
                                left[i].append(seqscopy.pop(0))
                            break
                    if size > tally:
                        for j in range(len(seqscopy)):
                            left[i].append(seqscopy.pop(0))
                print("left:", left)
                right = [[] for s in spaces_copy]
                seqscopy = [s for s in seqs]
                seqscopy.reverse()
                for i in range(len(spaces_copy)-1, -1, -1):
                    size = spaces_copy[i].size()
                    tally = 0
                    for j in range(len(seqscopy)):
                        sequence = seqscopy[j]
                        tally += sequence.value()
                        if tally > size:
                            for k in range(j):
                                print("for {} in range {}".format(k,j))
                                right[i].insert(0, seqscopy.pop(0))
                            break
                        if size - tally == 1:
                            tally += 1
                        if size == tally:
                            for k in range(j+1):
                                print("for {} in range {}+1".format(k, j))
                                right[i].insert(0, seqscopy.pop(0))
                            break
                    if size > tally:
                        for j in range(len(seqscopy)):
                            right[i].insert(0, seqscopy.pop(0))
                print("right:", right)
                final = [[] for s in spaces]
                for i in range(len(left)):
                    for j in range(len(left[i])):
                        if left[i][j] in right[i]:
                            final[i+offset].append(left[i][j].value())
                for i in range(len(final)):
                    spaces[i].set_clues(final[i])

            if self._update:
                print("THese are the clues {}".format(clues))
                generate_spaces()
                assign_clues()
                print("Spaces: {} Solved: {}".format(self.get_spaces(), self.is_solved()))
                self._update = False
            else:
                print("No update")


        def gt(self):
            return self._tiles
        
        def is_solved(self):
            if self._spaces == []:
                self._solved = True
            if self._solved == False:
                solved = True
                for s in self._spaces:
                    if not s.solved():
                        solved = False
                        break
                if solved:
                    self._solved = True
            return self._solved

        def __str__(self):
            return str(self._tiles)
        
        def __repr__(self):
            return str(self._tiles)

    class Tile(object):
        def __init__(self, position, puzzle, indices):
            self._state = EMPTY
            self._position = position
            self._indices = indices
            self._puzzle = puzzle

        def gp(self):
            return self._position
        
        def gi(self):
            return self._indices

        def ss(self, state):
            s = self.gs()
            if s is state:
                return
            ag.moveTo(self.get_puz().offset(self.gp()))
            if s is CROSSED:
                ag.click(button='right')
            elif s is FILLED:
                ag.click(button='left')
            if state is CROSSED:
                ag.click(button='right')
            elif state is FILLED:
                ag.click(button='left')
            self._state = state

            self.get_puz().new_state(self.gi())

        def gs(self):
            return self._state
        
        def get_puz(self):
            return self._puzzle
        
        def __str__(self):
            if self._state == CROSSED:
                return "X"
            elif self._state == FILLED:
                return "O"
            else:
                return "."
            
        def __repr__(self):
            if self._state == CROSSED:
                return "X"
            elif self._state == FILLED:
                return "O"
            else:
                return "."

    def __init__(self):
        self._puzzle_dimensions = [0,0]
        self._grid = None
        self._x_clues = []
        self._y_clues = []
        self._tilearrays = {}
        self._game_box = None
        self._grid_box = None
        self._tilesize = 0
        self._solved = False
        self._buffer = []
        ag.PAUSE = 0.02

        if MAXIMIZE_GAME_TAB:
            try:
                ag.moveTo(ag.locateCenterOnScreen(MISCADR + "taskbaricon.png", confidence = 0.90))
                ag.click()
            except ag.ImageNotFoundException:
                pass

        ready = self.read_screen()

        if not ready:
            raise RuntimeError("not ready.")

        print("Good luck!")

        # First, cross out zerod rows/columns
        for i in range(len(self._x_clues)):
            if self._x_clues[i] == [0]:
                for tile in self._tilearrays[AXIS_X, i].gt():
                    tile.ss(CROSSED)
        for i in range(len(self._y_clues)):
            if self._y_clues[i] == [0]:
                for tile in self._tilearrays[AXIS_Y, i].gt():
                    tile.ss(CROSSED)

        print("Starting Puzzle:")
        for i in range(self._puzzle_dimensions[0]):
            print(self._tilearrays[AXIS_Y, i])

        self._running = True
    
    '''
    read_screen
    determines the dimensions, tilesize, and clues of the puzzle.
    '''
    def read_screen(self, c = 0):
        '''
        process_clues
        takes a screenshot of each number and compares it to the reference photos to determine clue values.
        '''
        def process_clues(box: list, axis: bool) -> bool:
            bigfound = False
            for i in range(self._puzzle_dimensions[0]):
                found = False
                tile = ag.screenshot(region=self.offset(box))

                ## image modification
                tile = tile.convert('RGBA')
                data = tile.load()
                for x in range(tile.size[0]):
                    for y in range(tile.size[1]):
                        if data[x, y] != (255, 255, 255, 255):
                            data[x, y] = (0, 0, 0, 0)

                for j in range(self._puzzle_dimensions[0], -1, -1):
                    name = str(j) + "x" + str(self._tilesize) + ".png"
                    try:
                        ag.locate(NUMBERADR + name, tile, grayscale=True)
                        print("{}x{}: found a {}".format(c, i, j))
                        if axis == AXIS_X:
                            self._x_clues[i].insert(0,j)
                        else:
                            self._y_clues[i].insert(0,j)
                        found = True
                        break
                    except ag.ImageNotFoundException:
                        continue
                if not found:
                    print("{}x{}: couldn't find anything".format(c, i))
                elif not bigfound:
                    bigfound = True

                if axis == AXIS_X:
                    box[0] += 1 + self._tilesize
                else:
                    box[1] += 1 + self._tilesize
            return bigfound
        '''
        take_pics
        takes pictures for debugging purposes
        '''
        def take_pics(box: list, axis: bool):
            if axis:
                a = 'x'
            else:
                a = 'y'
            firstbox = [box[0], box[1], box[2], box[3]]
            for i in range(self._puzzle_dimensions[0]):
                screenname = a + str(i) + ".png"
                tile = ag.screenshot(region=self.offset(box))

                ## image modification
                tile = tile.convert('RGBA')
                data = tile.load()
                for x in range(tile.size[0]):
                    for y in range(tile.size[1]):
                        if data[x, y] != (255, 255, 255, 255):
                            data[x, y] = (0, 0, 0, 0)
                tile.save(screenname)

                if axis == AXIS_X:
                    box[0] += (1 + self._tilesize)
                else:
                    box[1] += (1 + self._tilesize)
            return firstbox

        ag.moveTo(1, 1)
        img = ag.screenshot()

        # first determine the location of the game
        # found via searching for the pause button (always the top right)
        # and the fill button (always the bottom right)
        bottomleft = None 
        topright = None
        try:
            bottomleft = ag.locate(MISCADR + "fill.png", img, confidence = 0.9)
        except ImageNotFoundException:
            bottomleft = ag.locate(MISCADR + "fill2.png", img, confidence = 0.9)
        try:
            topright = ag.locate(MISCADR + "pause.png", img, confidence = 0.9)
        except ImageNotFoundException:
            print("failed to find pause button")
            return False
        
        width = topright[0] + topright[2] - bottomleft[0] + 4
        height = bottomleft[1] + bottomleft[3] - topright[1] + 4
        self._game_box = (int(bottomleft[0] - 2), int(topright[1] - 2), int(width), int(height))
        print(self._game_box)

        img = ag.screenshot("game.png", region=self._game_box)
        #ag.moveTo(ag.center(self._game_box))

        # determine puzzle dimensions
        for d in listdir(DIMENSIONADR):
            try:
                ag.locate(DIMENSIONADR + d, img, confidence = 0.9)
                dim = d[1:d.find(".png")]
                print('dim: ', dim)
                self._puzzle_dimensions = [int(dim[:dim.find("x")]), int(dim[dim.find("x")+1:])]
                break
            except ag.ImageNotFoundException:
                continue
        if self._puzzle_dimensions == [0, 0]:
            print("failed to set puzzle dimensions")
            return False
        
        # determine tile size
        for t in listdir(TILEADR):
            try:
                ag.locate(TILEADR + t, img, confidence = 0.9)
                print("tile size: ", t)
                self._tilesize = int(t[:t.find(".")])
                break
            except ag.ImageNotFoundException:
                continue

        if self._tilesize == 0:
            print("couldnt find tilesize")
            return False

        # determine grid box
        gridstr = str(self._puzzle_dimensions[0]) + "x" + str(self._puzzle_dimensions[1]) + "x" + str(self._tilesize) + ".png"
        try:
            self._grid_box = ag.locate(GRIDADR + gridstr, img, confidence = 0.9)
            print("GBOX", self._grid_box)
            ag.moveTo(self.offset(self._grid_box))
        except ag.ImageNotFoundException:
            print("huh coudlnt find grid")
            return False
        
        # set tile objects w/ positions
        self._grid = [[] for i in range(self._puzzle_dimensions[0])]
        tilebox = [int(self._grid_box[0]), int(self._grid_box[1]), int(self._tilesize), int(self._tilesize)]
        ag.moveTo(self.offset(tilebox))
        for i in range(self._puzzle_dimensions[1]):
            for j in range(self._puzzle_dimensions[0]):
                self._grid[j].append(self.Tile(tuple(tilebox), self, (j,i)))
                print("{},{} -- {}".format(j, i, str(self._grid[j][i].gp())))
                #ag.moveTo(self.offset(self._grid[i][-1]._location))
                tilebox[0] += tilebox[2]
            tilebox[0] = int(self._grid_box[0])
            tilebox[1] += tilebox[3]

        # set tilearrays
        for i1 in range(self._puzzle_dimensions[0] * 2):
            i2 = i1 if i1 < self._puzzle_dimensions[0] else i1-self._puzzle_dimensions[0]
            axis = AXIS_X if i1 < self._puzzle_dimensions[0] else AXIS_Y
            tiles = []
            if axis == AXIS_X:
                for j in range(len(self._grid[i2])):
                    tiles.append(self._grid[i2][j])
            else:
                for j in range(len(self._grid)):
                    tiles.append(self._grid[j][i2])
            self._tilearrays[axis, i2] = self.TileArray(tiles)

        # determine clues (OMG)
        self._x_clues = [[] for i in range(self._puzzle_dimensions[0])]
        self._y_clues = [[] for i in range(self._puzzle_dimensions[1])]
        ag.moveTo(1, 1)
        tilebox = [int(self._grid_box[0]), int(self._grid_box[1]), int(self._tilesize), int(self._tilesize)]
        
        tilebox[0] += 3
        tilebox[1] -= self._tilesize - 1
        #tilebox = take_pics(tilebox, False)
        print("--- PROCESSING X STARTING AT {} ---".format(tilebox))
        while process_clues(tilebox, False):
            tilebox[0] = int(self._grid_box[0]) + 3
            tilebox[1] -= self._tilesize
            c += 1
        tilebox[0] = int(self._grid_box[0]) - self._tilesize + 1
        tilebox[1] = int(self._grid_box[1]) + 3
        c = 0
        #tilebox = take_pics(tilebox, True)
        print("--- PROCESSING Y STARTING AT {} ---".format(tilebox))
        while process_clues(tilebox, True):
            tilebox[0] -= self._tilesize - 1
            tilebox[1] = int(self._grid_box[1]) + 3
            c += 1

        print("x:", self._x_clues)
        print("y:", self._y_clues)

        return True

    def run(self):
        def str_diagnosis(diagnosis):
            if diagnosis is NO_DIAG:
                return "NO DIAGNOSIS"
            if diagnosis is ALREADY_SOLVED:
                return "{} ALREADY SOLVED".format(diagnosis)
            if diagnosis is CAN_CROSS:
                return "{} CAN CROSS".format(diagnosis)
            if diagnosis is CAN_FILL:
                return "{} CAN FILL".format(diagnosis)
            if diagnosis is EDGE_CASE:
                return "{} EDGE CASE".format(diagnosis)

        def generate_next_step():
            def already_solved(space, clues):
                tiles = space.tiles()
                if not clues:
                    return False
                if clues is [0]:
                    print("no filled required.")
                    return True
                ti = 0
                for i in range(len(clues)):
                    while tiles[ti].gs() is not FILLED:
                        ti += 1
                        if ti >= len(tiles):
                            print("there were no filled tiles")
                            return False
                    print("sequence starts at", ti)
                    for j in range(clues[i]):
                        if tiles[ti].gs() is not FILLED:
                            print("was not long enough.")
                            return False
                        ti += 1
                        if ti >= len(tiles):
                            if j < clues[i] -1:
                                print("reached the end before sequence was finished")
                                return False
                    if ti < len(tiles):
                        if tiles[ti].gs() is FILLED:
                            print("sequence is too long")
                            return False
                print("tihs one works")
                return True
            
            def can_fill(space, clues):
                size = space.size()
                value = 0
                for c in clues:
                    value += c
                value += len(clues) - 1
                if len(clues) == 1:
                    return True if value > size / 2 else False
                else:
                    seqs = []
                    for i in range(len(clues)):
                        seqs.append(Sequence(i, clues[i]))
                    map = [-1 for i in space.tiles()]
                    mi = 0
                    for i in range(len(seqs)):
                        for j in range(seqs[i].value()):
                            map[mi] = seqs[i].index()
                            mi += 1
                        mi += 1
                    mi = len(map) - 1
                    for i in range(len(seqs)-1, -1, -1):
                        for j in range(seqs[i].value()):
                            if map[mi]  == seqs[i].index():
                                return True
                            mi -= 1
                        mi -= 1
                    return False

            
            def edge_case(space, clues):
                # tells run() how to solve
                FILL_FROM_START = 1
                FILL_FROM_END = 2
                CROSS_FROM_START = 3
                CROSS_FROM_END = 4
                vars = [False for x in range(5)]
                # One Clue
                clue = clues[0]
                tiles = space.tiles()
                for i in range(len(tiles)):
                    if tiles[i].gs() is FILLED:
                        left = i
                        right = i
                        while tiles[right].gs() is FILLED:
                            right += 1
                            if right >= len(tiles):
                                break
                        right -= 1
                        if left < clue - 1 and right - clue > -1:
                            vars[FILL_FROM_START] = True
                        elif right > len(tiles) - clue and left + clue < len(tiles):
                            vars[FILL_FROM_END] = True
                        if right - clue >= 0:
                            vars[CROSS_FROM_START] = True
                        if left + clue < len(tiles) - 1:
                            print("{} + {} <= {} - 1".format(left, clue, len(tiles)))
                            vars[CROSS_FROM_END] = True
                        for v in vars:
                            if v:
                                vars[0] = True
                                break
                        break
                return vars

            for i1 in range(self._puzzle_dimensions[0] * 2):
                i = i1 if i1 < self._puzzle_dimensions[0] else i1 - self._puzzle_dimensions[0]
                axis = AXIS_X if i == i1 else AXIS_Y
                output = [NO_DIAG, axis, i]
                tarr = self._tilearrays[axis, i]
                if tarr.is_solved():
                    continue
                spaces = tarr.get_spaces()
                for s in range(len(spaces)):
                    space = spaces[s]
                    if space.solved():
                        continue
                    if space.delete():
                        output[0] = CAN_CROSS
                        return space, output
                    clues = space.clues()
                    if already_solved(space, clues):
                        output[0] = ALREADY_SOLVED
                        return space, output
                    if space.new():
                        if can_fill(space, clues):
                            output[0] = CAN_FILL
                            return space, output
                    else:
                        if len(clues) == 1:
                            vars = edge_case(space, clues)
                            print("vars:", vars)
                            if vars[0]:
                                output[0] = EDGE_CASE
                                output.append(vars)
                                return space, output
            return None, (NO_DIAG, [])
                    
        for i1 in range(self._puzzle_dimensions[0] * 2):
            i = i1 if i1 < self._puzzle_dimensions[0] else i1 - self._puzzle_dimensions[0]
            axis = AXIS_X if i == i1 else AXIS_Y
            tarr = self._tilearrays[axis, i]
            clues = self._x_clues[i] if i == i1 else self._y_clues[i]
            print("{}-{}: ".format(axis, i), end="")
            tarr.update(clues)
            if tarr.is_solved():
                continue
        #input("gen next step:--------------------------------------------------")
        space, output = generate_next_step()
        diagnosis = output[0]
        if diagnosis is NO_DIAG:
            self._running = False
            return
        print("NEXT STEP id: {} {}".format(output[1], output[2]), "   space:", space, "diagnosis:", str_diagnosis(diagnosis))
        tiles = space.tiles()
        clues = space.clues()
        print("TILES::::::{}".format(tiles))
        if diagnosis is NO_DIAG:
            self._running = False
        elif diagnosis is ALREADY_SOLVED or diagnosis is CAN_CROSS:
            # cross out the non-filled tiles
            for i in range(len(tiles)):
                if tiles[i].gs() is not FILLED:
                    tiles[i].ss(CROSSED)
            
        elif diagnosis is CAN_FILL:
            marker = [-1 for t in range(len(tiles))]
            ti = 0
            if len(clues) == 1:
                for i in range(clues[0]):
                    marker[ti] = 1
                    ti += 1
                ti = len(tiles) - 1
                for i in range(clues[0]):
                    if marker[ti] == 1:
                        tiles[ti].ss(FILLED)
                    ti -= 1
            else:
                seqs = []
                for i in range(len(clues)):
                    seqs.append(Sequence(i, clues[i]))
                for i in range(len(seqs)):
                    for j in range(seqs[i].value()):
                        marker[ti] = seqs[i].index()
                        ti += 1
                    ti += 1
                ti = len(marker) - 1
                for i in range(len(seqs)-1, -1, -1):
                    for j in range(seqs[i].value()):
                        if marker[ti]  == seqs[i].index():
                            tiles[ti].ss(FILLED)
                        ti -= 1
                    ti -= 1
        
        elif diagnosis is EDGE_CASE:
            print("edge case:", output[3])
            FILL_FROM_START = 1
            FILL_FROM_END = 2
            CROSS_FROM_START = 3
            CROSS_FROM_END = 4
            vars = output[3]
            clue = clues[0]
            if vars[FILL_FROM_START]:
                start = False
                ti = 0
                for i in range(clue):
                    if not start:
                        if tiles[ti].gs() is not FILLED:
                            ti += 1
                            continue
                        start = True
                    tiles[ti].ss(FILLED)
                    ti += 1
            if vars[FILL_FROM_END]:
                start = False
                ti = len(tiles) - 1
                for i in range(clue):
                    if not start:
                        if tiles[ti].gs() is not FILLED:
                            ti -= 1
                            continue
                        start = True
                        continue
                    tiles[ti].ss(FILLED)
                    ti -= 1
            if vars[CROSS_FROM_START]:
                start = False
                origin = 0
                for i in range(len(tiles)-1,-1,-1):
                    if not start:
                        if tiles[i].gs() is not FILLED:
                            continue
                        origin = i
                        start = True
                    if i <= origin - clue:
                        tiles[i].ss(CROSSED)
            if vars[CROSS_FROM_END]:
                start = False
                origin = 0
                for i in range(len(tiles)):
                    if not start:
                        if tiles[i].gs() is not FILLED:
                            continue
                        origin = i
                        start = True
                    if i >= origin + clue:
                        tiles[i].ss(CROSSED)

    def new_state(self, indices):
        x = indices[0]
        y = indices[1]
        self._tilearrays[AXIS_X, x].set_to_update()
        self._tilearrays[AXIS_Y, y].set_to_update()

    def running(self):
        return self._running

    def offset(self, b):
        return (int(b[0] + self._game_box[0]), int(b[1] + self._game_box[1]), int(b[2]), int(b[3]))
    
    def offset_px(self, p):
        return (int(p[0] + self._game_box[0]), int(p[1] + self._game_box[1]))

def main():
    pbot = Puzzle()
    while pbot.running():
        pbot.run()
    print("end")


if __name__ == "__main__":
    main()