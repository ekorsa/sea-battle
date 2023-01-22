from random import randint


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, bow, length, o):
        # 0 vertical, 1 horizontal orientation
        self.bow = bow
        self.l = length
        self.o = o
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            if self.o == 0:
                curr_dot = Dot(self.bow.x + i, self.bow.y)
                ship_dots.append(curr_dot)
                continue
            if self.o == 1:
                curr_dot = Dot(self.bow.x, self.bow.y + i)
                ship_dots.append(curr_dot)
        return ship_dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["o"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def add_ship(self, ship):
        for i in ship.dots:
            if self.out(i) or i in self.busy:
                raise BoardWrongShipException

        for i in ship.dots:
            self.field[i.x][i.y] = '■'
        self.ships.append(ship)
        self.count += 1
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for i in ship.dots:
            for dx, dy in near:
                contour_dot = Dot(i.x + dx, i.y + dy)
                if not (self.out(contour_dot)) and not (contour_dot in self.busy):
                    self.busy.append(contour_dot)
                    if verb:
                        self.field[contour_dot.x][contour_dot.y] = '.'

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException

        if d in self.busy:
            raise BoardUsedException

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                if ship.lives == 1:
                    print("Destroyed!!!")
                    self.field[d.x][d.y] = 'X'
                    ship.lives = 0
                    self.contour(ship, verb=True)
                    self.count -= 1
                    return True
                else:
                    ship.lives -= 1
                    print("Hit!!!")
                    self.field[d.x][d.y] = 'X'
                    return True

        print("Miss!!!")
        self.field[d.x][d.y] = '.'
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        x = randint(0, self.board.size - 1)
        y = randint(0, self.board.size - 1)
        return Dot(x, y)


class User(Player):
    def ask(self):
        while True:
            coordinate = input("Your turn. fill x and y in format like \"1 2\" :").split()
            if len(coordinate) != 2:
                print("Please fill 2 coordinates!")
                continue
            elif coordinate[0].isnumeric() and coordinate[1].isnumeric():
                return Dot(int(coordinate[0]) - 1, int(coordinate[1]) - 1)
            else:
                print("Please fill 2 coordinates!")
                continue


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        list_ships = [3, 2, 2, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for ship_len in list_ships:
            while True:
                if attempts > 2000:
                    return None
                attempts += 1
                o = randint(0, 1)
                x = randint(0, self.size - ship_len)
                y = randint(0, self.size - 1)
                if o == 1:  # horizontal
                    x, y = y, x
                ship = Ship(Dot(x, y), ship_len, o)
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    @staticmethod
    def greet():
        print("-------------------")
        print("    Welcome to     ")
        print("    sea battle     ")
        print("-------------------")
        print(" input format :x y ")
        print(" x - string number ")
        print(" y - column number ")

    def loop(self):
        move = True
        while True:
            if move:
                print("Player move:")
                print("Our Board:")
                print(self.us.board)
                print("Enemy Board:")
                print(self.us.enemy)
                result = self.us.move()
                if result:
                    if self.us.enemy.count == 0:
                        print("Player is winner!")
                        break
                else:
                    move = not move

            else:
                print("Enemy move:")
                result = self.ai.move()
                if result:
                    if self.ai.enemy.count == 0:
                        print("AI is winner!")
                        break
                else:
                    move = not move

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
