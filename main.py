"""
###########################################
#  Power Four                             #
#  coded by Maximin Duvillard             #
#  references : none yet at this time     #
#                                         #
#  version of february 2016               #
#        completed in september           #
#          Two Players                    #
#                                         #
###########################################
"""
import tkinter
from tkinter import Frame, Canvas, Toplevel, Scale, Message
from super_matrix import SuperMatrix

from game_tools import gui, tools
# see https://github.com/Darkduv/Games # -> game_tools


# Todo : possibilities of variations :
# Todo : - bigger power like power five in a greater grid
# Todo : - more than 2 players ?
# Todo : log-in for record and/or play with scores ..
# Todo 2: a better way to code the search of a victory ??

# Todo 1: keyboard shortcuts like cmd + U for Undo, etc...  -> Partly done


class PowerFour(tools.GameNPlayer):
    _nb_players = 2
    _not_a_player = -1

    def __init__(self, n_rows: int = 6, n_cols: int = 7):
        super().__init__(self._nb_players)
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.grid = SuperMatrix(self._not_a_player, n_rows, n_cols)
        self.init_game()

    def init_game(self, *args, **kwargs):
        self.grid = SuperMatrix(-1, self.n_rows, self.n_cols)
        self.turn = 0
        self.player = 0

    def play(self, col: int) -> int:
        if 0 > col or self.n_cols <= col:
            raise tools.InvalidActionError("Col not in the good range")
        row = 0
        while row < self.n_rows \
                and self.grid[row][col] == self._not_a_player:
            row += 1
        row -= 1
        if row == -1:
            raise tools.InvalidActionError("Column is filled")
        self.grid[row][col] = self.player
        win = self.win(col)  # todo : efficient winning test

        self.next_player()
        return win

    def win(self, action) -> int:
        r"""Give the id of the winning player, -1 if no victory.
        /!\ Here the test is only on the current player"""
        # todo : efficient winning test
        player = self.player
        alignments = self.search_alignment(player)
        return player if alignments else -1

    def search_alignment(self, player: int = None):
        orientation = [[0, 1], [1, 0], [1, 1], [1, -1]]
        if player is None:
            player = self.player
        all_alignments = []
        for row in range(self.n_rows):
            for col in range(self.n_cols):
                if self.grid[row][col] != player:
                    continue
                for sens in orientation:
                    x2, y2 = row, col
                    alignment = [[row, col]]
                    for _ in range(3):
                        x2 += sens[0]
                        y2 += sens[1]
                        if not (0 <= x2 < self.n_rows
                                and 0 <= y2 < self.n_cols):
                            break
                        alignment.append([x2, y2])
                        if self.grid[x2][y2] != player:
                            break
                    else:
                        # add alignment
                        all_alignments.append(alignment)
        return all_alignments

    def __str__(self):
        s = ""
        s += f"Power 4, turn={self.turn}, player={self.player}\n"
        s += "=" * (2 * self.n_cols + 1) + "\n"
        for row in range(self.n_rows):
            s2 = ' '.join('.OX'[player + 1] for player in self.grid[row])
            s += f"|{s2}|\n"
        s += "=" * (2 * self.n_cols + 1)
        return s

    def can_play(self) -> bool:
        for col in range(self.n_cols):
            if self.grid[0][col] != self._not_a_player:
                return True
        return False

    def possible_actions(self):
        actions = []
        for col in range(self.n_cols):
            if self.grid[0][col] != self._not_a_player:
                actions.append(col)
        return actions

    def copy(self) -> "PowerFour":
        copy = PowerFour(n_rows=self.n_rows, n_cols=self.n_cols)
        copy.grid = [row[:] for row in self.grid]
        copy.turn = self.turn
        copy.player = self.player
        return copy


class GridGUI(Frame):
    """GUI for the Grid of Power4
    TODO : force first player color ?
            #  (be careful with A.I. definition)"""
    _colors = ["red", "yellow"]
    _colors_all = []
    _names = ["Red", "Yellow"]

    def __init__(self, root):
        # Red = 0 and Yellow = 1
        # The panel of game is constituted of a re-scaling grid
        # containing it-self a canvas. at each re-scaling of the
        # grid,we calculate the tallest size possible for the
        # cases (squared) of the grid, et the dimensions of the
        # canvas are adapted in consequence.
        super().__init__(root)
        # Link of the event <resize> with an adapted manager :
        self.bind("<Configure>", self.rescale)
        # Canvas :
        self.can_grid = Canvas(self, bg="dark blue", borderwidth=0,
                               highlightthickness=1,
                               highlightbackground="white")
        # Link of the event <click of the mouse> with its manager :
        self.can_grid.bind("<Button-1>", self.click)
        self.can_grid.pack(side=tkinter.LEFT)

        self.side_panel = Canvas(self, bg="white", borderwidth=2,
                                 highlightthickness=0,
                                 highlightbackground="white")
        self.side_panel.pack(side=tkinter.RIGHT,
                             expand=tkinter.YES, fill=tkinter.BOTH)
        _side_canvas = tkinter.Canvas(self.side_panel,
                                      bg="white", borderwidth=0,
                                      highlightthickness=0,
                                      width=80, height=80)
        _side_canvas.place(relx=0.5, rely=0.666, anchor="center")
        _circle = _side_canvas.create_oval(0, 0, 79, 79,
                                           outline="grey",
                                           width=1,  fill="red")
        _circle_player = (_side_canvas, _circle)

        def _config_circle(fill):
            _circle_player[0].itemconfig(_circle_player[1], fill=fill)
        self._config_message_circle = _config_circle
        self.message = tkinter.Label(self.side_panel, text="Yellow's\n turn",
                                     font="Helvetica 18 bold",
                                     bg="white",
                                     borderwidth=0)
        self.message.place(relx=0.5, rely=0.35, anchor="center")
        self.side_panel.pack(side=tkinter.RIGHT,
                             expand=tkinter.YES, fill=tkinter.BOTH)
        # construction of a list of lists
        self.grid = PowerFour(6, 7)  # default values : 6*7
        self.history = tools.SimpleHistoric()
        self.width, self.height = 2, 2
        self.cote = 0
        self.win = False
        self.init_game()
        self.init_gui()

    def init_game(self, state: PowerFour = None):
        """Initialisation of the list which remember the state of the game"""
        self.win = False
        if state is None:
            self.grid.init_game()
        else:
            self.grid = state

    def init_gui(self):
        self.set_side()
        self.trace_grille()

    def set_side(self):
        """Set the side value in relation with the window size"""
        # maximal width and height possibles for the cases :
        l_max = self.width / self.grid.n_cols
        h_max = self.height / self.grid.n_rows
        # the side of a case would be the smallest of the two dimensions :
        self.cote = min(l_max, h_max)

    def rescale(self, event: tkinter.Event = None):
        """Operations made at each rescaling"""
        # the properties which are linked to the event of reconfiguration
        # contain all the new sizes of the panel :
        highlight_bordure = 1
        self.width, self.height = self.winfo_width() - highlight_bordure * 2, \
            self.winfo_height() - highlight_bordure * 2
        self.set_side()
        self.trace_grille()
        if event:
            pass

    def trace_grille(self):
        """Layout of the grid, in function of dimensions and options"""
        # -> determining new dimensions for the canvas :
        wide, high = self.cote * self.grid.n_cols, self.cote * self.grid.n_rows
        self.can_grid.configure(width=wide, height=high)
        # Layout of the grid:
        self.can_grid.delete(tkinter.ALL)  # erasing of the past Layouts
        # Layout of all the pawns,
        # white or black according to the state of the game :
        for row in range(self.grid.n_rows):
            for col in range(self.grid.n_cols):
                x1 = col * self.cote + 3  # size of pawns =
                x2 = (col + 1) * self.cote - 3  # size of the case -6
                y1 = row * self.cote + 3  #
                y2 = (row + 1) * self.cote - 3
                color = ["white", "red", "yellow", "black"][
                    self.grid.grid[row][col] + 1]
                self.can_grid.create_oval(x1, y1, x2, y2, outline="grey",
                                          width=1, fill=color)
        # self.can_grid.update()
        self.message.config(text=f"{['Red', 'Yellow'][self.grid.player]}'s"
                                 f"\n turn")
        self._config_message_circle(["red", "yellow"][self.grid.player])

        # self.side_panel.update()

    def click(self, event):
        """Management of the mouse click : return the pawns"""
        # We start to determinate the line and the columns :
        if self.win:
            return
        # row, int(event.y / self.cote),
        col = int(event.x / self.cote)
        if not 0 <= col < self.grid.n_cols:
            raise tools.InvalidActionError(
                "Click in the grid to make a valid action")

        player = self.grid.player
        self.history.save_new(self.grid.copy())
        win = self.grid.play(col)
        # maximal width and height possibles for the cases :
        self.set_side()
        wide, high = self.cote * self.grid.n_cols, self.cote * self.grid.n_rows
        self.can_grid.configure(width=wide, height=high)
        row = 0
        x1 = self.cote * col + 3
        x2 = self.cote * (col + 1) - 3
        color_player = ["red", "yellow"][player]
        while row < self.grid.n_rows:
            y1 = row * self.cote + 3
            y2 = (row + 1) * self.cote - 3
            self.can_grid.create_oval(x1, y1 - self.cote, x2, y2 - self.cote,
                                      outline="grey", width=1, fill="white")
            self.update()
            self.can_grid.create_oval(x1, y1, x2, y2, outline="grey",
                                      width=1, fill=color_player)
            self.update()
            self.can_grid.after(100)
            if self.grid.grid[row][col] != -1:
                break
            row += 1

        if win == -1:
            # self.side_panel.destroy()
            # self.side_panel = Label(text=["Red", "Yellow"][self.player]+\
            # "'s\n turn", font="Helvetica 15 bold")
            self.message.config(
                text=f"{['Red', 'Yellow'][self.grid.player]}'s\n turn")

            self._config_message_circle(["red", "yellow"][self.grid.player])

            self.side_panel.pack(side=tkinter.RIGHT)
            self.side_panel.update()
            self.trace_grille()
        else:
            self.win = True
            self.display_victory(player)

            self.message.config(
                text=f"{['Red', 'Yellow'][player]}\n wins !!")
            self._config_message_circle(["red", "yellow"][player])

    def undo(self, event=None):
        last_state = self.history.undo()
        self.win = False
        self.grid = last_state
        if event:
            pass
        self.trace_grille()

    def reset(self, event=None):
        self.init_game()
        self.win = False
        self.init_gui()
        if event:
            pass

    def display_victory(self, player=None):
        all_alignment = self.grid.search_alignment(player)
        if not all_alignment:
            return False
        for alignment in all_alignment:
            for pawn in alignment:
                self.grid.grid[pawn[0]][pawn[1]] = 2
        self.trace_grille()
        return True


class PowerFourGUI(tkinter.Tk):
    """corps principal du programme"""

    def __init__(self):
        super().__init__()

        self.geometry("400x300")
        self.title("Game of power four - Two Player")

        self.game = GridGUI(self)

        menu_config = [
            ('File', [
                ('Options', self.options),
                None,
                ('Undo', self.game.undo),
                ('Restart', self.game.reset),
                None,
                ('Quit', self.destroy)
            ]),
            ('Help', [
                ('Principle of the game', self.principle),
                ('About...', self.about)
            ])
        ]

        self.m_bar = gui.RecursiveMenuBar(self)
        self.m_bar.config_menu(menu_config)

        self.game.pack(expand=tkinter.YES, fill=tkinter.BOTH, padx=8, pady=8)

        self.bind("<Command-z>", self.game.undo)
        self.bind("<Command-r>", self.game.reset)

        children = self.winfo_children()
        while children:
            child = children.pop()
            if isinstance(child, tkinter.Menu):
                child.config(font=(None, 12))
                children.extend(child.winfo_children())

    def options(self):
        """Choice of the number of lines and columns for the grid"""
        opt = Toplevel(self)
        cur_l = Scale(opt, length=200, label="Number of lines :",
                      orient=tkinter.HORIZONTAL,
                      from_=1, to=12, command=self.update_nb_rows)
        cur_l.set(self.game.grid.n_rows)  # initial position of the cursor
        cur_l.pack()
        cur_h = Scale(opt, length=200, label="Number of columns :",
                      orient=tkinter.HORIZONTAL,
                      from_=1, to=12, command=self.update_nb_cols)
        cur_h.set(self.game.grid.n_cols)
        cur_h.pack()

    def update_nb_cols(self, n):
        """Updates the number of columns."""
        self.game.grid.n_cols = int(n)
        self.game.init_game()
        self.game.rescale()

    def update_nb_rows(self, n):
        """Updates the number of rows."""
        self.game.grid.n_rows = int(n)
        self.game.init_game()
        self.game.rescale()

    # def redo(self):
    #     if self.game.coup < len(self.game.game):
    #         self.game.coup += 1
    #         game = self.game.game[self.game.coup]
    #         self.game.init_state()
    #         self.game.state = game.copy()
    #     self.game.trace_grille()

    def principle(self):
        """window-message containing
         the small description of the principle of this game"""
        msg = Toplevel(self)
        Message(msg, bg="navy", fg="ivory", width=400,
                font="Helvetica 10 bold",
                text="You have to manage alone!!!!! \n"
                     "References : Max&Cie, 2017") \
            .pack(padx=10, pady=10)

    def about(self):
        """window-message indicating the author and the type of licence"""
        msg = Toplevel(self)
        Message(msg, width=200, aspect=100, justify=tkinter.CENTER,
                text="Game of Connect Four\n\n by M.Duvillard.\n"
                     "Licence = ???").pack(padx=10, pady=10)


if __name__ == '__main__':
    P4 = PowerFourGUI()
    P4.mainloop()
