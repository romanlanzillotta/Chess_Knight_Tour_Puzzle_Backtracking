class NumberDimError(Exception):
    pass


class OutOfBoundsError(Exception):
    pass


class MoveNotAllowedError(Exception):
    pass


def get_user_dims(input_legend, err_legend, bounds, list_valid=None):
    err_msg = ""
    while True:
        try:
            user_in = input(err_msg + input_legend)
            lst_user = user_in.strip().split(" ")
            lst_ints = [int(i)-1 for i in lst_user]
            if len(lst_ints) != 2:
                raise NumberDimError
            if all([bool(0 <= i <= j) for i, j in zip(lst_ints, bounds)]):
                if list_valid is None:
                    return lst_ints[0], lst_ints[1]
                else:
                    if tuple(lst_ints) in list_valid:
                        return lst_ints[0], lst_ints[1]
                    else:
                        raise MoveNotAllowedError
            else:
                raise OutOfBoundsError
        except (ValueError, TypeError, NumberDimError, OutOfBoundsError, MoveNotAllowedError):
            err_msg = err_legend


class Board:
    def __init__(self, X, Y):
        self.X = X+1
        self.Y = Y+1
        self.spaces = len(str(self.X * self.Y))
        self.board = [["_" * self.spaces for _ in range(self.X)] for _ in range(self.Y)]
        self.cur_pos = None
        self.visited = []
        self.solution = None

    def copy_board(self):
        return [[self.board[j][i] for i in range(self.X)] for j in range(self.Y)]

    def clone_board(self):
        new_board = Board(self.X-1, self.Y-1)
        new_board.board = self.copy_board()
        new_board.visited = self.visited[:]
        new_board.cur_pos = self.cur_pos
        return new_board

    def update_pos(self, x_, y_):
        self.board[y_][x_] = "X".rjust(self.spaces)
        if self.cur_pos is not None:
            self.board[self.cur_pos[1]][self.cur_pos[0]] = "*".rjust(self.spaces)
        self.cur_pos = (x_, y_)
        self.visited.append(self.cur_pos)
        return self

    def print(self, aux_board=None):
        if aux_board is None:
            aux_board = self.board
        print(" " * len(str(self.Y)) + "-" * (self.spaces + 1) * len(aux_board[0]) + "---")
        for i in range(len(aux_board) - 1, -1, -1):
            print(str(i + 1).rjust(len(str(self.Y))) + "| " + " ".join(aux_board[i]) + " |")
        print(" " * len(str(self.Y)) + "-" * (self.spaces + 1) * len(aux_board[0]) + "---")
        print(" " * (len(str(self.Y)) + 2) +
              " ".join([str(i).rjust(self.spaces) for i in range(1, len(aux_board[0]) + 1)]))

    def restrict_moves(self, pos):
        delta = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]
        moves = [(pos[0] + t[0], pos[1] + t[1]) for t in delta]
        restr_moves = [move for move in moves if (-1 < move[0] < self.X) and (-1 < move[1] < self.Y)]
        restr_moves = [move for move in restr_moves if not (move in self.visited)]
        restr_moves = [move for move in restr_moves if not (move == pos)]
        return restr_moves

    def find_moves(self, pos, steps):
        restr_moves = self.restrict_moves(pos)
        if steps == 1:
            return pos, str(len(restr_moves))
        else:
            q = []
            for move in restr_moves:
                a, b = self.find_moves(move, steps-1)
                q.append(b.rjust(self.spaces))
            return restr_moves, q

    def show_moves(self, moves, q):
        aux_board = self.copy_board()
        for i, move in enumerate(moves):
            aux_board[move[1]][move[0]] = q[i].rjust(self.spaces)
        self.print(aux_board)

    def test_win(self):
        return len(self.visited) == (self.X*self.Y)

    def backtracking_solve(self, new_board, boards = None):
        if (self.cur_pos is not None) and self.board is not None:
                if not boards:
                    boards = []
                boards.append(new_board)
                possible_moves = new_board.restrict_moves(new_board.cur_pos)
                # trivial case:
                if new_board.test_win():
                    # solution found. add last one and return list of boards
                    return True, boards
                else:
                    # add board and call recursivity
                    found = False
                    for move in possible_moves:
                        (x_, y_) = move
                        another_board = boards[-1].clone_board().update_pos(x_, y_)
                        found, boards = self.backtracking_solve(another_board, boards)
                        if found:
                            break
                        else:
                            # no solution here, "stuck". Backtrack one step
                            boards.pop()
                    return found, boards

    def solve(self):
        found, boards = self.backtracking_solve(self.clone_board())
        if found:
            solution = []
            for board in boards:
                solution.append(board.cur_pos)
            self.solution = solution
            return found

    def show_solution(self):
        if self.solution:
            new_board = Board(self.X-1, self.Y-1)
            for i, move in enumerate(self.solution):
                new_board.board[move[1]][move[0]] = str(i + 1).rjust(self.spaces)
            new_board.print()


def get_manual_solve():
    while True:
        try:
            manual_solve = input("Do you want to try the puzzle? (y/n):").strip().lower()
            if manual_solve in ["y", "yes"]:
                return True
            elif manual_solve in ["n", "no"]:
                return False
            else:
                raise Exception
        except Exception:
            print("Invalid input!")

# get initial conditions from user and set the board
n, m = get_user_dims("Enter your board dimensions:", "Invalid dimensions!", (99, 99))
x, y = get_user_dims("Enter the knight's starting position:", "Invalid position!", (n, m))
board = Board(n, m)
board.update_pos(x, y)
# ask if the user will solve it manually or the backtracking algorithm will solve it.
manual_solve = get_manual_solve()

# Test if solution exists for the board and initial condition
if not board.solve():
    print("No solution exists!")
else:
    if manual_solve:
        # calculate initial possible moves and let the user input new moves until there are no more left to make
        possible_moves, len_pm = board.find_moves(board.cur_pos, 2)
        board.show_moves(possible_moves, len_pm)
        while len(possible_moves) > 0:
            x, y = get_user_dims("Enter your next move:", "Invalid position!", (n, m), possible_moves)
            board.update_pos(x, y)
            possible_moves, len_pm = board.find_moves(board.cur_pos, 2)
            board.show_moves(possible_moves, len_pm)
        if board.test_win():
            print("What a great tour! Congratulations!")
        else:
            print("No more possible moves!")
            print(f'Your knight visited {len(board.visited)} squares!')
    else:
        # show the backtracking solution found.
        print()
        print("Here's the solution!")
        board.show_solution()

