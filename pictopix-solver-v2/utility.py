AXIS_X = 0
AXIS_Y = 1

CELL_EMPTY   = 0
CELL_FILLED  = 1
CELL_CROSSED = 2

DIAG_NONE     = 0
DIAG_DELETE   = 1
DIAG_SOLVABLE = 2

"""credits to stackoverflow"""
class style:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

"""credits to geeksforgeeks.org"""
def get_super(x): 
    x = str(x)
    normal = "0123456789"
    super_s = "⁰¹²³⁴⁵⁶⁷⁸⁹"
    res = x.maketrans(''.join(normal), ''.join(super_s)) 
    return x.translate(res) 