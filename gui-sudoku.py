import pygame
from solver import solve, valid, find_empty
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 540, 600


class Grid:
    """board = [
        [7, 8, 0, 4, 0, 0, 1, 2, 0],
        [6, 0, 0, 0, 7, 5, 0, 0, 9],
        [0, 0, 0, 6, 0, 1, 0, 7, 8],
        [0, 0, 7, 0, 4, 0, 2, 6, 0],
        [0, 0, 1, 0, 5, 0, 9, 3, 0],
        [9, 0, 4, 0, 6, 0, 0, 0, 5],
        [0, 7, 0, 3, 0, 0, 0, 1, 2],
        [1, 2, 0, 0, 0, 7, 4, 0, 0],
        [0, 4, 9, 2, 0, 6, 0, 0, 7]
    ]"""
    randomBoard = [[0 for j in range(0, 9)] for i in range(0, 9)]

    def __init__(self, rows, cols, width, height):

        self.rows = rows
        self.cols = cols
        self.setDiagonal()
        self.randomizeBoard()
        self.createZeros()

        self.cubes = [[Cube(self.randomBoard[i][j], i, j, width, height) for j in range(cols)]
                      for i in range(rows)]

        self.width = width
        self.height = height
        self.model = None
        self.selected = None

    def setDiagonal(self):

        #n = random.randint(3,5)
        nList = list(range(1, 10))
        for i in range(0, 3):
            n = random.randint(0, 2)
            l = list(range(0, 3))
            while n != 0:
                j = random.choice(l)
                num = random.choice(nList)
                if self.randomBoard[i][j] == 0:
                    self.randomBoard[i][j] = num
                    nList.remove(num)
                    l.remove(j)
                    n -= 1

        mList = list(range(1, 10))
        for i in range(3, 6):
            n = random.randint(0, 2)
            l = list(range(3, 6))
            while n != 0:
                j = random.choice(l)
                num = random.choice(mList)
                if self.randomBoard[i][j] == 0:
                    self.randomBoard[i][j] = num
                    mList.remove(num)
                    l.remove(j)
                    n -= 1

        oList = list(range(1, 10))
        for i in range(6, 9):
            n = random.randint(0, 2)
            l = list(range(6, 9))
            while n != 0:
                j = random.choice(l)
                num = random.choice(oList)
                if self.randomBoard[i][j] == 0:
                    self.randomBoard[i][j] = num
                    oList.remove(num)
                    l.remove(j)
                    n -= 1

    def randomizeBoard(self):

        # setDiagonal(randomBoard)

        for i in range(len(self.randomBoard)):
            for j in range(len(self.randomBoard[0])):
                if self.randomBoard[i][j] == 0:
                    for num in range(1, 10):
                        if valid(self.randomBoard, num, (i, j)):
                            self.randomBoard[i][j] = num

                            if solve(self.randomBoard):
                                # randomizeBoard()
                                self.randomBoard[i][j] = num
                            else:
                                self.randomBoard[i][j] = 0
        # createZeros(randomBoard)

    def createZeros(self):

        for i in range(len(self.randomBoard)):
            positions = random.randint(4, 6)
            l = list(range(0, 9))
            while positions != 0:

                j = random.choice(l)
                if self.randomBoard[i][j] != 0:
                    self.randomBoard[i][j] = 0
                    l.remove(j)
                    positions -= 1

    def updateModel(self):
        self.model = [[self.cubes[i][j].value for j in range(
            self.cols)] for i in range(self.rows)]

    def place(self, val):
        row, col = self.selected

        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set(val)
            self.updateModel()

            if valid(self.model, val, (row, col)) and solve(self.model):
                return True
            else:
                self.cubes[row][col].set(0)
                self.cubes[row][col].set_temp(0)
                self.updateModel()
                return False

    def sketch(self, val):
        row, col = self.selected
        self.cubes[row][col].set_temp(val)

    def draw(self, win):

        gap = self.width / 9

        for i in range(self.rows+1):
            if i % 3 == 0 and i != 0:
                thick = 4
            else:
                thick = 1

            pygame.draw.line(win, (0, 0, 0), (0, i*gap),
                             (self.width, i*gap), thick)

            pygame.draw.line(win, (0, 0, 0), (i*gap, 0),
                             (i*gap, self.height), thick)

        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].draw(win)

    def select(self, row, col):

        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].selected = False

        self.cubes[row][col].selected = True
        self.selected = row, col

    def clear(self):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set_temp(0)

    def click(self, pos):

        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width / 9
            x = pos[0] // gap
            y = pos[1] // gap
            return (int(y), int(x))
        else:
            return None

    def is_finished(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cubes[i][j].value == 0:
                    return False
        return True

    def selfSolve(self, win):
        self.updateModel()
        find = find_empty(self.model)
        if not find:
            return True
        else:
            row, col = find

        for i in range(1, 10):
            if valid(self.model, i, (row, col)):

                self.model[row][col] = i
                self.cubes[row][col].set(i)
                self.cubes[row][col].drawChange(win, True)
                self.updateModel()

                if self.selfSolve(win):
                    pygame.time.delay(100)
                    return True

                self.model[row][col] = 0
                self.cubes[row][col].set(0)
                self.updateModel()
                self.cubes[row][col].drawChange(win, False)
                pygame.display.update()
                pygame.time.delay(500)

        return False


class Cube:
    rows = 9
    cols = 9

    def __init__(self, value, row, col, width, height):
        self.value = value
        self.temp = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    def draw(self, win):

        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        if self.temp != 0 and self.value == 0:
            text = fnt.render(str(self.temp), 1, (128, 128, 128))
            win.blit(text, (x+5, y+5))
        elif not(self.value == 0):
            text = fnt.render(str(self.value), 1, (0, 0, 0))
            win.blit(text, (x + (gap/2 - text.get_width()/2),
                     y + (gap/2 - text.get_height()/2)))

        if self.selected:
            pygame.draw.rect(win, (255, 0, 0), (x, y, gap, gap), 3)

    def drawChange(self, win, g=True):
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        text = fnt.render(str(self.value), 1, (0, 0, 0))
        win.blit(text, (x + (gap / 2 - text.get_width()),
                 y + (gap/2 - text.get_height())))

        if g:
            pygame.draw.rect(win, (0, 255, 0), (x, y, gap, gap), 3)
        else:
            pygame.draw.rect(win, (255, 255, 255), (x, y, gap, gap))
            pygame.draw.rect(win, (255, 0, 0), (x, y, gap, gap), 3)
            #blank = fnt.render(" ", 1, (0, 0, 0))
            # win.blit(blank, (x + (gap / 2 - text.get_width()),
            #                 y + (gap/2 - text.get_height())))

    def set(self, val):
        self.value = val

    def set_temp(self, val):
        self.temp = val


def redraw_window(win, board, time, strikes):
    win.fill((255, 255, 255))

    fnt = pygame.font.SysFont("comicsans", 40)
    text = fnt.render("Time: " + format_time(time), 1, (0, 0, 0))
    win.blit(text, (WIDTH - 160, 560))

    text = fnt.render("X "*strikes, 1, (255, 0, 0))
    win.blit(text, (20, 560))
    board.draw(win)


def format_time(secs):

    sec = secs % 60
    minutes = sec // 60
    hour = minutes // 60

    mat = " "+str(minutes)+":"+str(sec)
    return mat


def main():
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sudoku")

    board = Grid(9, 9, WIDTH, HEIGHT)

    key = None
    run = True

    start = time.time()
    strikes = 0
    #c = pygame.time.Clock()

    while run:
        play_time = round(time.time() - start)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    key = 1
                if event.key == pygame.K_2:
                    key = 2
                if event.key == pygame.K_3:
                    key = 3
                if event.key == pygame.K_4:
                    key = 4
                if event.key == pygame.K_5:
                    key = 5
                if event.key == pygame.K_6:
                    key = 6
                if event.key == pygame.K_7:
                    key = 7
                if event.key == pygame.K_8:
                    key = 8
                if event.key == pygame.K_9:
                    key = 9
                if event.key == pygame.K_DELETE:
                    board.clear()
                    key = None
                if event.key == pygame.K_RETURN:
                    i, j = board.selected
                    if board.cubes[i][j].temp != 0:
                        if board.place(board.cubes[i][j].temp):
                            print("Success")
                        else:
                            print("Wrong")
                            strikes += 1
                        key = None

                        if board.is_finished():
                            print("Game over")
                            run = False
                if event.key == pygame.K_SPACE:
                    board.selfSolve(win)
                # if event.key == pygame.K_LCTRL:
                #    randomizeBoard(board)

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = board.click(pos)

                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None
        if board.selected and key != None:
            board.sketch(key)

        redraw_window(win, board, play_time, strikes)
        pygame.display.update()


main()
pygame.quit()
