from tkinter import *
from SuperMatrix import *


###########################################
#  Power Four                             #
#  coded by Maximin Duvillard             #
#  references : none yet                  #
#                                         #
#  version of february of 2016            #
#                                         #
#           with an A.I.                  #
#                                         #
###########################################

# Todo: Change first color ?
# Todo: change player when victory ...
# Fixme: bad function undo_move ... to check.
# Fixme: big big problem in restart ...
# Todo: human player is not supposed to always start, which is the case here ??
# Todo: let the human player the possibility to choose whether or not he chooses to start first??
# Todo: keyboard shortcuts for undo, restart, etc. ??

class MenuBar(Frame):
    """bar of menu rolling"""

    def __init__(self, boss=None):
        Frame.__init__(self, borderwidth=2, relief=GROOVE)
        # #### Menu <File> #####
        file_menu = Menubutton(self, text='File')
        file_menu.pack(side=LEFT, padx=5)
        me1 = Menu(file_menu)
        me1.add_command(label='Options', underline=0,
                        command=boss.options)
        me1.add_command(label='Undo', underline=0,
                        command=boss.undo)
        # me1.add_command(label='Redo', underline=0,
        #                 command=boss.redo)
        me1.add_command(label='Restart', underline=0,
                        command=boss.reset)
        me1.add_command(label='Quit', underline=0,
                        command=boss.quit)
        file_menu.configure(menu=me1)

        # #### Menu <Help> #####
        help_menu = Menubutton(self, text='Help')
        help_menu.pack(side=LEFT, padx=5)
        me2 = Menu(help_menu)
        me2.add_command(label='Principe of the game', underline=0,
                        command=boss.principe)
        me2.add_command(label='By the way ...', underline=0,
                        command=boss.by_the_way)
        help_menu.configure(menu=me2)


class Panel(Frame):
    """Panel for the game (n x m grid)"""

    def __init__(self):
        # Red = 0 and Yellow = 1
        # The panel of game is constituted of a re-scaling grid
        # containing it-self a canvas. at each re-scaling of the
        # grid,we calculate the tallest size possible for the
        # cases (squared) of the grid, et the dimensions of the
        # canvas are adapted in consequence.
        Frame.__init__(self)
        self.computer = 0
        self.n_lig, self.n_col = 6, 7  # initial grid = 4 x 4
        # Link of the event <resize> with an adapted manager :
        self.bind("<Configure>", self.rescale)
        # Canvas :
        self.can = Canvas(self, bg="dark blue", borderwidth=0,
                          highlightthickness=1, highlightbackground="white")
        # Link of the event <click of the mouse> with its manager :
        self.can.bind("<Button-1>", self.click)
        self.can.pack(side=LEFT)
        self.can_bis = Canvas(self, bg="white", borderwidth=0,
                              highlightthickness=1, highlightbackground="white")
        self.turn = self.can_bis.create_text(self.can_bis.winfo_width() / 2, self.can_bis.winfo_height() / 3,
                                             text="Yellow's\n turn", font="Helvetica 18 bold")
        x1 = self.can_bis.winfo_width() / 3
        y = self.can_bis.winfo_height() * 2 / 3
        y1 = y - x1
        x2 = x1 * 2
        y2 = y + x1
        self.turn_bis = self.can_bis.create_oval(x1, y1, x2, y2, outline="grey", width=1, fill="yellow")
        # self.can_bis = Label(text="Red's\n turn")
        self.can_bis.pack(side=RIGHT)
        self.player = 1  # TODO = to change color of first player.
        self.state = SuperMatrix(2, self.n_lig, self.n_col)  # construction of a list of lists
        self.game = SuperList()
        # self.history = []
        self.coup = 0
        self.width, self.height = 2, 2
        self.cote = 0
        self.win = False
        self.init_jeu()

    def init_jeu(self, state=None):
        """Initialisation of the list which remember the state of the game"""
        self.win = False
        if state is None:
            # self.player = 1 # TODO : here to force first player color ? (be careful with A.I. definition
            self.state = SuperMatrix(2, self.n_lig, self.n_col)
            self.game.append(self.state)
        else:
            self.state = state.copy()
        self.game.append(self.state)
        self.trace_grille()

    def rescale(self, event):
        """Operations made at each rescaling"""
        # the properties which are linked to the event of reconfiguration
        # contain all the new sizes of the panel :
        self.width, self.height = event.width - 4, event.height - 4
        # The subtract of 4 pixels allowed to compensate the width
        # of the 'highlightbordure" rolling the canvas)
        self.trace_grille()

    def trace_grille(self):
        """Layout of the grid, in function of dimensions and options"""
        # maximal width and height possibles for the cases :
        l_max = self.width / self.n_col
        h_max = self.height / self.n_lig
        # the side of a case would be the smallest of the two dimensions :
        self.cote = min(l_max, h_max)
        # -> establishment of new dimensions for the canvas :
        wide, high = self.cote * self.n_col, self.cote * self.n_lig
        self.can.configure(width=wide, height=high)
        # Layout of the grid:
        self.can.delete(ALL)  # erasing of the past Layouts
        # Layout of all the pawns, white or black according to the sate of the game :
        for l in range(self.n_lig):
            for c in range(self.n_col):
                x1 = c * self.cote + 3  # size of pawns =
                x2 = (c + 1) * self.cote - 3  # size of the case -6
                y1 = l * self.cote + 3  #
                y2 = (l + 1) * self.cote - 3
                color = ["red", "yellow", "white", "black"][self.state[l][c]]
                self.can.create_oval(x1, y1, x2, y2, outline="grey",
                                     width=1, fill=color)
        self.can_bis.configure(width=self.width - wide, height=self.height)
        self.can_bis.delete(self.turn, self.turn_bis)
        self.turn = self.can_bis.create_text(self.can_bis.winfo_width() / 2, self.can_bis.winfo_height() / 3,
                                             text=["Red", "Yellow"][self.player] + "'s\n turn",
                                             font="Helvetica 18 bold")
        x = self.can_bis.winfo_width() / 3
        y = self.can_bis.winfo_height() / 3
        r = min([x, y, 40])
        y1 = y * 2 - r
        x1 = 3 * x / 2 - r
        x2 = 3 * x / 2 + r
        y2 = y * 2 + r
        self.turn_bis = self.can_bis.create_oval(x1, y1, x2, y2, outline="grey",
                                                 width=1, fill=["red", "yellow"][self.player])

    def click(self, event):
        """Management of the mouse click : return the pawns"""
        # We start to determinate the line and the columns :
        lig, col = int(event.y / self.cote), int(event.x / self.cote)
        if self.player == 1:  # the human is Yellow
            self.play_game(col, lig)

    def play(self, col, lig=0):
        if 0 <= lig < self.n_lig and 0 <= col < self.n_col:
            # maximal width and height possibles for the cases :
            l_max = self.width / self.n_col
            h_max = self.height / self.n_lig
            # the side of a case would be the smallest of the two dimensions :
            self.cote = min(l_max, h_max)
            wide, high = self.cote * self.n_col, self.cote * self.n_lig
            self.can.configure(width=wide, height=high)
            n = 0
            x1 = self.cote * col + 3
            x2 = self.cote * (col + 1) - 3
            while n < self.n_lig and self.state[n][col] == 2:
                y1 = n * self.cote + 3
                y2 = (n + 1) * self.cote - 3
                color = ["red", "yellow"][self.player]
                self.can.create_oval(x1, y1 - self.cote, x2, y2 - self.cote, outline="grey",
                                     width=1, fill="white")
                self.update()
                self.can.create_oval(x1, y1, x2, y2, outline="grey",
                                     width=1, fill=color)
                self.update()
                self.can.after(100)
                n += 1

            if 1 <= n <= self.n_lig:
                self.state[n - 1][col] = self.player
                # self.history.append([n-1, col, self.player])
                self.coup += 1
                if not self.display_victory():
                    self.game[self.coup] = self.state.copy()
                    self.player += 1
                    self.player %= 2
                    # self.can_bis.destroy()
                    # self.can_bis = Label(text=["Red", "Yellow"][self.player]+"'s\n turn", font="Helvetica 15 bold")
                    self.can_bis.itemconfig(self.turn, text=["Red", "Yellow"][self.player] + "'s\n turn")
                    self.can_bis.itemconfig(self.turn_bis, fill=["red", "yellow"][self.player])

                    # print("hello")
                    self.can_bis.pack(side=RIGHT)
                    self.can_bis.update()
                    self.trace_grille()
                else:
                    self.can_bis.itemconfig(self.turn, text=["Red", "Yellow"][self.player] + "\nwins !!")
                    self.can_bis.delete(self.turn_bis)
                    self.win = True
                    self.game[self.coup] = self.state.copy()
                    self.player += 1
                    self.player %= 2

                return True
            else:
                return False

        else:
            return False

    def play_game(self, col, lig):
        # here computer is Red and human yellow
        if self.play(col, lig) and not self.win:
            list_col = self.col_possible()
            if list_col:
                # t = randint(0, len(list_col)-1)
                # self.play(list_col[t])  # Todo :
                play = self.brut_force(2)  # here to change the difficulty and the time spent by the computer to think
                self.play(play[0][0])

    def col_possible(self):
        return [i for i in range(self.n_col) if self.state[0][i] == 2]

    def coups_possibles(self):
        ll = SuperList()
        for i in self.col_possible():
            for j in range(self.n_lig):
                if self.state[j][i] == 2:
                    ll[i] = [i, j]
        return ll

    def brut_force(self, proof):
        save = self.state.copy()
        list_weight = ListWeight()

        if proof == 0:
            for i in self.coups_possibles().copy():
                self.state[i[1]][i[0]] = 0  # Computer is 0 (Red) here
                if self.victory_threaten():
                    self.state = save.copy()
                    list_weight.append([i, 10])
                    self.player = 0
                    self.state = save.copy()
                    break
                else:
                    self.player = 1
                    ll = self.coups_possibles().copy()
                    if ll:
                        save2 = self.state.copy()
                        list_weight2 = ListWeight()
                        for j in ll:
                            self.state[j[1]][j[0]] = 1
                            if self.victory_threaten():
                                list_weight2.append([j, -10])
                                self.state = save2.copy()
                                break
                            else:
                                list_weight2.append([j, 0])
                            self.state = save2.copy()
                        list_weight.append([i, list_weight2.position_weight_min()[1]])
                    else:
                        list_weight.append([i, 0])
                self.player = 0
                self.state = save.copy()
            return list_weight.position_weight_max()

        for i in self.coups_possibles().copy():
            self.state[i[1]][i[0]] = 0  # Computer is 0 (Red) here
            if self.victory_threaten():
                self.state = save.copy()
                list_weight.append([i, 50])
                self.player = 0
                self.state = save.copy()
                break
            else:
                self.player = 1
                ll = self.coups_possibles().copy()
                if ll:
                    save2 = self.state.copy()
                    list_weight2 = ListWeight()
                    for j in ll:
                        self.state[j[1]][j[0]] = 1
                        if self.victory_threaten():
                            list_weight2.append([j, -50])
                            self.state = save2.copy()
                            self.player = 1
                            break
                        else:
                            maxi = self.brut_force(proof-1)
                            if maxi:
                                list_weight2.append([j, maxi[1]])
                        self.state = save2.copy()
                        self.player = 1
                    mini = list_weight2.position_weight_min()
                    list_weight.append([i, mini[1]])
                else:
                    list_weight.append([i, 0])
                self.player = 0
                self.state = save.copy()
        return list_weight.position_weight_max()

    def victory_threaten(self):
        # Todo : threaten.... ??
        orientation = [[0, 1], [1, 0], [1, 1], [-1, 1]]
        color = self.player
        all_alignments = []
        for x in range(self.n_lig):
            for y in range(self.n_col):
                if self.state[x][y] != color:
                    continue
                for sens in orientation:
                    x2, y2 = x, y
                    victory = True
                    alignment = [[x, y]]
                    for n in range(3):
                        x2 += sens[0]
                        y2 += sens[1]
                        alignment.append([x2, y2])
                        try:
                            if x2 < 0 or y2 < 0 or self.state[x2][y2] != color:
                                victory = False
                                break
                        except IndexError:
                            victory = False
                            break

                    if victory:
                        # return alignment
                        all_alignments.append(alignment)
        return all_alignments

    def display_victory(self):
        all_alignment = self.victory_threaten()
        if not all_alignment:
            return False
        else:
            for alignment in all_alignment:
                for pawn in alignment:
                    self.state[pawn[0]][pawn[1]] = 3
                self.trace_grille()
            return True


class Ping(Frame):
    """main program"""

    def __init__(self, root):
        Frame.__init__(self, root)
        self.master.geometry("400x300")
        self.master.title(" Game of power four - One Player")

        self.m_bar = MenuBar(self)
        self.m_bar.pack(side=TOP, expand=NO, fill=X)

        self.jeu = Panel()
        self.jeu.pack(expand=YES, fill=BOTH, padx=8, pady=8)
        self.pack()

        root.bind("<Command-z>", self.undo)
        root.bind("<Command-r>", self.reset)
        self.pack()

    def options(self):
        """Choice of the number of lines and columns for the grid"""
        opt = Toplevel(self)
        cur_l = Scale(opt, length=200, label="Number of lines :",
                      orient=HORIZONTAL,
                      from_=1, to=12, command=self.maj_lines)
        cur_l.set(self.jeu.n_lig)  # initial position of the cursor
        cur_l.pack()
        cur_h = Scale(opt, length=200, label="Number of columns :",
                      orient=HORIZONTAL,
                      from_=1, to=12, command=self.maj_columns)
        cur_h.set(self.jeu.n_col)
        cur_h.pack()

    def maj_columns(self, n):
        """maj_columns
        :param n: int number of columns
        :type self: Ping
        """
        self.jeu.n_col = int(n)
        self.jeu.init_jeu()

    def maj_lines(self, n):
        """for giving a major of n"""
        self.jeu.n_lig = int(n)
        self.jeu.init_jeu()

    def reset(self, event=None):
        """  french!  """
        self.jeu.init_jeu()
        self.jeu.coup = 0
        self.jeu.trace_grille()
        if event:
            pass

    def undo(self, event=None):
        # here undo only if red = computer and yellow = human (and undo -> for human)
        if self.jeu.player == 1:
            if self.jeu.coup > 1:
                self.jeu.coup -= 2
                self.jeu.init_jeu(self.jeu.game[self.jeu.coup].copy())
        else:
            if self.jeu.coup > 0:
                self.jeu.coup -= 1
                self.jeu.player = 1
                self.jeu.init_jeu(self.jeu.game[self.jeu.coup].copy())
        if event:
            pass

    # def redo(self):
    #     if self.jeu.coup < len(self.jeu.game):
    #         self.jeu.coup += 1
    #         game = self.jeu.game[self.jeu.coup]
    #         self.jeu.init_jeu()
    #         self.jeu.state = game.copy()
    #     self.jeu.trace_grille()

    def principe(self):
        """window-message containing the small description of the principe of this game"""
        msg = Toplevel(self)
        Message(msg, bg="navy", fg="ivory", width=400,
                font="Helvetica 10 bold",
                text="You have to manage alone!!!!! \n"
                     "Réf : Max&Cie, 2017") \
            .pack(padx=10, pady=10)

    def by_the_way(self):
        """window-message indicating the author and the type of licence"""
        msg = Toplevel(self)
        Message(msg, width=200, aspect=100, justify=CENTER,
                text="Jeu de Power_Four\n\n by Maximin D.\n"
                     "Licence = None").pack(padx=10, pady=10)


if __name__ == '__main__':
    game = Tk()
    Pg = Ping(game)
    Pg.mainloop()