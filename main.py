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
from abc import ABC, abstractmethod
from super_matrix import SuperMatrix


# Todo : possibilities of variations :
# Todo : - bigger power like power five in a greater grid
# Todo : - more than 2 players ?
# Todo : log-in for record and/or play with scores ..
# Todo 2: a better way to code the search of a victory ??

# Todo 1: keyboard shortcuts like cmd + U for Undo, etc...  -> Partly done

class EmptyHistoricError(Exception):
    """Raise when trying accessing a value of an empty historic"""


class InvalidActionError(Exception):
    """Raise when trying to make an invalid action"""


EmptyHistoric = EmptyHistoricError()
InvalidAction = InvalidActionError()


class SimpleHistoric:
    """For keeping track of the actions"""

    def __init__(self, l_saves: list = None, current_undo: list = None):
        if l_saves is None:
            l_saves = []
        if current_undo is None:
            current_undo = []
        self.l_saves = l_saves
        self.current_undo = current_undo

    def save_new(self, save):
        """Save a state or an action"""
        self.l_saves.append(save)
        self.current_undo = []

    def undo(self):
        if not self.l_saves:
            raise EmptyHistoric
        save = self.l_saves.pop(-1)
        self.current_undo.append(save)
        return save

    def redo(self):
        if not self.current_undo:
            raise EmptyHistoric
        save = self.current_undo.pop(-1)
        self.l_saves.append(save)
        return save


class GameNPlayer(ABC):
    """Skeleton of a game of N players"""

    def __init__(self, nb_players=2):
        self.nb_players = nb_players
        self.player = 0  # player currently playing
        self.turn = 0  # nb round/turn

    @abstractmethod
    def play(self, action) -> bool:
        """Must implement the given action. Return if the player wins."""

    @abstractmethod
    def can_play(self) -> bool:
        """Can the current player play ?"""

    @abstractmethod
    def possible_actions(self):
        """Get the possibles actions for the current player"""

    @abstractmethod
    def win(self, action) -> int:
        """if winning, return the id of the player winning. else -1"""

    def next_player(self):
        """Update new id player"""
        self.player += 1
        self.player %= self.nb_players

    def undo_action(self, action):
        """ Undo the action """
        raise NotImplemented

    def redo_action(self, action_or_state):
        """ Redo the action """
        raise NotImplemented

    def apply(self, state_saved):
        """Set game to the given state"""
        raise NotImplemented

    @abstractmethod
    def init_game(self, *args, **kwargs):
        """ (Re) initialize the game """

    def copy(self) -> "GameNPlayer":
        """ Copy the object """
        raise NotImplemented

    def export_save(self):
        """ Export/Save the game in a lighter way than copying"""
        raise NotImplemented


class MenuBar(tkinter.Menu):

    def __init__(self, root=None):
        super().__init__(root)
        root.config(menu=self)

    def config_menu(self, hierarchy, parent: tkinter.Menu = None):
        if parent is None:
            parent = self
            # underline = 0
        else:
            # underline = None
            pass

        for option in hierarchy:
            if option is None:
                parent.add_separator()
                continue
            label, menu_command = option

            if isinstance(menu_command, list):
                menu = tkinter.Menu(parent, tearoff=0)
                self.config_menu(menu_command, parent=menu)
                parent.add_cascade(label=label, menu=menu)
            else:
                parent.add_command(label=label, command=menu_command)


class PowerFour(GameNPlayer):
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
            raise InvalidActionError("Col not in the good range")
        row = 0
        while row < self.n_rows \
                and self.grid[row][col] == self._not_a_player:
            row += 1
        row -= 1
        if row == -1:
            raise InvalidActionError("Column is filled")
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
        s += "="*(2*self.n_cols + 1)+"\n"
        for row in range(self.n_rows):
            s += f"|{' '.join('.OX'[player+1] for player in self.grid[row])}|\n"
        s += "="*(2*self.n_cols + 1)
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
        self.can = Canvas(self, bg="dark blue", borderwidth=0,
                          highlightthickness=1, highlightbackground="white")
        # Link of the event <click of the mouse> with its manager :
        self.can.bind("<Button-1>", self.click)
        self.can.pack(side=tkinter.LEFT)
        self.can_bis = Canvas(self, bg="white", borderwidth=0,
                              highlightthickness=1, highlightbackground="white")
        self.turn = self.can_bis.create_text(self.can_bis.winfo_width() / 2,
                                             self.can_bis.winfo_height() / 3,
                                             text="Yellow's\n turn",
                                             font="Helvetica 18 bold")
        x1 = self.can_bis.winfo_width() / 3
        y = self.can_bis.winfo_height() * 2 / 3
        y1 = y - x1
        x2 = x1 * 2
        y2 = y + x1
        self.turn_bis = self.can_bis.create_oval(x1, y1, x2, y2, outline="grey",
                                                 width=1, fill="yellow")
        # self.can_bis = Label(text="Red's\n turn")
        self.can_bis.pack(side=tkinter.RIGHT, expand=tkinter.YES)
        # construction of a list of lists
        self.grid = PowerFour(6, 7)  # default values : 6*7
        self.history = SimpleHistoric()
        self.width, self.height = 2, 2
        self.cote = 0
        self.win = False
        self.init_jeu()

    def init_jeu(self, state: PowerFour = None):
        """Initialisation of the list which remember the state of the game"""
        self.win = False
        if state is None:
            self.grid.init_game()
        else:
            self.grid = state
        self.set_side()
        self.trace_grille()

    def set_side(self):
        """Set the side value in relation with the window size"""
        # maximal width and height possibles for the cases :
        l_max = self.width / self.grid.n_cols
        h_max = self.height / self.grid.n_rows
        # the side of a case would be the smallest of the two dimensions :
        self.cote = min(l_max, h_max)

    def rescale(self, event):
        """Operations made at each rescaling"""
        # the properties which are linked to the event of reconfiguration
        # contain all the new sizes of the panel :
        self.width, self.height = event.width - 4, event.height - 4
        # The subtraction of 4 pixels allows to compensate the width
        # of the 'highlight bordure' rolling the canvas
        self.set_side()
        self.trace_grille()

    def trace_grille(self):
        """Layout of the grid, in function of dimensions and options"""
        # -> establishment of new dimensions for the canvas :
        wide, high = self.cote * self.grid.n_cols, self.cote * self.grid.n_rows
        self.can.configure(width=wide, height=high)
        # Layout of the grid:
        self.can.delete(tkinter.ALL)  # erasing of the past Layouts
        # Layout of all the pawns,
        # white or black according to the state of the game :
        for l in range(self.grid.n_rows):
            for c in range(self.grid.n_cols):
                x1 = c * self.cote + 3  # size of pawns =
                x2 = (c + 1) * self.cote - 3  # size of the case -6
                y1 = l * self.cote + 3  #
                y2 = (l + 1) * self.cote - 3
                color = ["white", "red", "yellow", "black"][self.grid.grid[l][c]+1]
                self.can.create_oval(x1, y1, x2, y2, outline="grey",
                                     width=1, fill=color)
        self.can_bis.configure(width=self.width - wide, height=self.height)
        self.can_bis.delete(self.turn, self.turn_bis)
        self.turn = \
            self.can_bis.create_text(
                self.can_bis.winfo_width() / 2,
                self.can_bis.winfo_height() / 3,
                text=f"{['Red', 'Yellow'][self.grid.player]}'s"
                     f"\n turn",
                font="Helvetica 18 bold")
        x = self.can_bis.winfo_width() / 3
        y = self.can_bis.winfo_height() / 3
        r = min([x, y, 40])
        y1 = y * 2 - r
        x1 = 3 * x / 2 - r
        x2 = 3 * x / 2 + r
        y2 = y * 2 + r
        self.turn_bis\
            = self.can_bis.create_oval(x1, y1, x2, y2, outline="grey", width=1,
                                       fill=["red", "yellow"][self.grid.player])

    def click(self, event):
        """Management of the mouse click : return the pawns"""
        # We start to determinate the line and the columns :
        # row, int(event.y / self.cote),
        if self.win:
            return
        col = int(event.x / self.cote)
        if not 0 <= col < self.grid.n_cols:
            raise InvalidActionError(
                "Click in the grid to make a valid action")
            # return

        player = self.grid.player
        self.history.save_new(self.grid.copy())
        win = self.grid.play(col)
        # maximal width and height possibles for the cases :
        self.set_side()
        wide, high = self.cote * self.grid.n_cols, self.cote * self.grid.n_rows
        self.can.configure(width=wide, height=high)
        row = 0
        x1 = self.cote * col + 3
        x2 = self.cote * (col + 1) - 3
        color_player = ["red", "yellow"][player]
        while row < self.grid.n_rows:
            y1 = row * self.cote + 3
            y2 = (row + 1) * self.cote - 3
            self.can.create_oval(x1, y1 - self.cote, x2, y2 - self.cote,
                                 outline="grey", width=1, fill="white")
            self.update()
            self.can.create_oval(x1, y1, x2, y2, outline="grey",
                                 width=1, fill=color_player)
            self.update()
            self.can.after(100)
            if self.grid.grid[row][col] != -1:
                break
            row += 1

        if win == -1:
            # self.can_bis.destroy()
            # self.can_bis = Label(text=["Red", "Yellow"][self.player]+\
            # "'s\n turn", font="Helvetica 15 bold")
            self.can_bis.itemconfig(
                self.turn,
                text=f"{['Red', 'Yellow'][self.grid.player]}'s\n turn")
            self.can_bis.itemconfig(
                self.turn_bis, fill=["red", "yellow"][self.grid.player])

            self.can_bis.pack(side=tkinter.RIGHT)
            self.can_bis.update()
            self.trace_grille()
        else:
            self.win = True
            self.display_victory(player)
            self.update()

            self.can_bis.itemconfig(
                self.turn,
                text=f"{['Red', 'Yellow'][player]}\n wins !!")
            self.can_bis.delete(self.turn_bis)

    def undo(self, event=None):
        last_state = self.history.undo()
        self.win = False
        self.grid = last_state
        if event:
            pass
        self.trace_grille()

    def reset(self, event=None):
        self.init_jeu()
        self.win = False
        self.trace_grille()
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
        # self.master.geometry("400x300")
        # self.master.title(" Game of power four - Two Player")

        self.geometry("400x300")
        self.title("Game of power four - Two Player")

        self.jeu = GridGUI(self)

        menu_config = [
            ('File', [
                ('Options', self.options),
                None,
                ('Undo', self.jeu.undo),
                ('Restart', self.jeu.reset),
                None,
                ('Quit', self.destroy)
            ]),
            ('Help', [
                ('Principle of the game', self.principle),
                ('About...', self.about)
            ])
        ]

        self.m_bar = MenuBar(self)
        self.m_bar.config_menu(menu_config)

        self.jeu.pack(expand=tkinter.YES, fill=tkinter.BOTH, padx=8, pady=8)

        self.bind("<Command-z>", self.jeu.undo)
        self.bind("<Command-r>", self.jeu.reset)

    def options(self):
        """Choice of the number of lines and columns for the grid"""
        opt = Toplevel(self)
        cur_l = Scale(opt, length=200, label="Number of lines :",
                      orient=tkinter.HORIZONTAL,
                      from_=1, to=12, command=self.update_nb_rows)
        cur_l.set(self.jeu.grid.n_rows)  # initial position of the cursor
        cur_l.pack()
        cur_h = Scale(opt, length=200, label="Number of columns :",
                      orient=tkinter.HORIZONTAL,
                      from_=1, to=12, command=self.update_nb_cols)
        cur_h.set(self.jeu.grid.n_cols)
        cur_h.pack()

    def update_nb_cols(self, n):
        """Updates the number of columns."""
        self.jeu.n_col = int(n)
        self.jeu.init_jeu()

    def update_nb_rows(self, n):
        """Updates the number of rows."""
        self.jeu.n_row = int(n)
        self.jeu.init_jeu()

    # def redo(self):
    #     if self.jeu.coup < len(self.jeu.game):
    #         self.jeu.coup += 1
    #         game = self.jeu.game[self.jeu.coup]
    #         self.jeu.init_state()
    #         self.jeu.state = game.copy()
    #     self.jeu.trace_grille()

    def principle(self):
        """window-message containing
         the small description of the principle of this game"""
        msg = Toplevel(self)
        Message(msg, bg="navy", fg="ivory", width=400,
                font="Helvetica 10 bold",
                text="You have to manage alone!!!!! \n"
                     "Réf : Max&Cie, 2017") \
            .pack(padx=10, pady=10)

    def about(self):
        """window-message indicating the author and the type of licence"""
        msg = Toplevel(self)
        Message(msg, width=200, aspect=100, justify=tkinter.CENTER,
                text="Jeu de Power_Four\n\n by M.Duvillard.\n"
                     "Licence = ???").pack(padx=10, pady=10)


if __name__ == '__main__':
    P4 = PowerFourGUI()
    P4.mainloop()
