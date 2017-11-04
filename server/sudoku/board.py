
from threading import Lock
from test_patterns import PATTERN1
import logging

class Board:
    #contains a 9X9 cell grid
    def __init__(self):
        self.LOCK = Lock()
        self.ROWS = list()
        for r in range(9):
            row = [Cell() for c in range(9)]
            self.ROWS.append(row)

    def setup_board(self):
        for r_b in range(3):
            block = PATTERN1[r_b] #contains 3 lists
            for c_b in range(3):
                for r in range(3):
                    o = (r + c_b) % 3 #helps choose the correct block
                    sblock = block[o]
                    for c in range(3):
                        y = r_b * 3 + r
                        x = c_b * 3 + c
                        v = sblock[c]
                        self.__set_correct_val(x, y, v)
    
    def __set_correct_val(self, x, y, v):
        if not( x in range(9) and y in range(9) and v in range(1,10)):
            return False
        self.LOCK.acquire()
        self.ROWS[y][x].set_correct_value(v)
        self.LOCK.release()
        return True
    #returns truth value about success of operation
    def add_number(self, x, y, nr):
        #try adding a number to the board
        if not( x in range(9) and y in range(9) and nr in range(1,10)):
            raise ValueError('User entered incorrect value')
        self.LOCK.acquire()
        p = self.ROWS[y][x].set_value(nr)
        self.LOCK.release()
        return p or False
    
    #Retrieve the user visible value
    def get_current_value(self, x, y):
        if not( x in range(9) and y in range(9)):
            return None
        self.LOCK.acquire()
        v = self.ROWS[y][x].get_value()
        self.LOCK.release()
        return v
    
    def get_correct_value(self, x, y):
        if not( x in range(9) and y in range(9)):
            return None
        self.LOCK.acquire()
        v = self.ROWS[y][x].get_correct_value()
        self.LOCK.release()
        return v
    
    #not threadsafe
    def print_board(self):
        for r in range(9):
            rr = self.ROWS[r]
            for c in range(9):
                s = "" + str(rr[c].correct_value)
                print s,
            print

class Cell:
    #Empty cell value 0, valid values 1 through 9
    
    TYPE_PRE_ENTERED = 1
    TYPE_USER_ENTERED = 2
    SUPPORTED_TYPES = {TYPE_PRE_ENTERED: "pre entered", TYPE_USER_ENTERED: "user entered"}
    
    def __init__(self):
        #type of cell, value of cell, user_entered_value
        self.lock = Lock()
        self.type = Cell.TYPE_PRE_ENTERED
        self.correct_value = 0
        self.user_value = 0
    
    def set_value(self, val):
        p = False
        if not val in range(1, 10):
            return False
        self.lock.acquire()
        self.user_value = val
        p = val == self.correct_value
        self.lock.release()
        return p
        
    def get_value(self):
        v = 0
        self.lock.acquire()
        v = self.user_value
        self.lock.release()
        return v
        
    def set_correct_value(self, val):
        if not val in range(1, 10):
            return False
        self.lock.acquire()
        self.correct_value = val
        self.lock.release()
    
    def get_correct_value(self):
        v = 0
        self.lock.acquire()
        v = self.user_value
        self.lock.release()
        return v
    
    def set_type(self, new_type):
        if not Cell.SUPPORTED_TYPES.has_key(new_type):
            return False
        self.lock.acquire()
        self.type = new_type
        self.lock.release()
        return True
    
    def debug_self(self):
        return "Type is " + Cell.SUPPORTED_TYPES,get(self.type) + ", correct value is " + str(self.correct_value) + ", user entered value is " + str(self.user_value)
    
#Testing the logic 
def test_new_cell():
    cell = Cell()
    assert cell.type == Cell.TYPE_PRE_ENTERED
    assert cell.user_value == 0 and cell.correct_value == 0
    print("New cell works as planned")

def test_modding_cell():
    cell = Cell()
    cell.set_type(Cell.TYPE_USER_ENTERED)
    assert cell.type == Cell.TYPE_USER_ENTERED
    t_res = cell.set_type(5)
    assert t_res == False
    assert cell.type == Cell.TYPE_USER_ENTERED
    
    cell.set_value(3)
    assert cell.user_value == 3
    print("Cell modding tests passed")

def test_generating_board():
    board = Board()
    print("Board generates without errors")

def test_modding_board():
    board = Board()
    
    res = board.add_number(0,0,4)
    assert board.ROWS[0][0].user_value == 4
    
    try:
        res = board.add_number(10,10,5)
        assert False
    except ValueError:
        res = None
    try:
        board.add_number(0,10,5)
        assert False
    except ValueError:
        res = None
    try:
        board.add_number(10,0,5)
        assert False
    except ValueError:
        res = None
    try:
        board.add_number(0,0,0)
        assert False
    except ValueError:
        res = None
    print("Board modding without errors")
    
def test_getting_value_no_issues():
    board = Board()
    board.add_number(0,1,4)
    
    val = board.get_current_value(0,1)
    assert val == 4
    val = 5
    val2 = board.get_current_value(0,1)
    assert val2 == 4
    print("Getting value from board poses no issues")
    
def test_draw_board():
    board = Board()
    board.setup_board()
    board.print_board()

if __name__ == '__main__':
    FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
    logging.basicConfig(level=logging.DEBUG,format=FORMAT)
    LOG = logging.getLogger()
    
    nr_of_tests = 6
    nr_of_failed = 0
    
    #run tests
    LOG.debug("Running %s tests", nr_of_tests)
    try:
        test_new_cell()
    except AssertionError:
        nr_of_failed = nr_of_failed + 1
    
    try:
        test_modding_cell()
    except AssertionError:
        nr_of_failed = nr_of_failed + 1
    
    try:
        test_generating_board()
    except AssertionError:
        nr_of_failed = nr_of_failed + 1
    
    try:
        test_modding_board()
    except AssertionError:
        nr_of_failed = nr_of_failed + 1
    
    try:
        test_getting_value_no_issues()
    except AssertionError:
        nr_of_failed = nr_of_failed + 1
        
    try:
        test_draw_board()
    except AssertionError:
        nr_of_failed = nr_of_failed + 1
    LOG.debug("Tests completed. Passed %s of %s", nr_of_tests - nr_of_failed, nr_of_tests)
    
