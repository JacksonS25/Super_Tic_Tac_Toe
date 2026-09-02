import tkinter as tk
from tkinter import messagebox

class SuperTicTacToe(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Super Tic-Tac-Toe")
        self.geometry("600x650")
        self.configure(bg="#222222")

        # Game State Variables
        self.current_player = "X"
        self.active_board = None  # None means player can choose any active board
        
        # Track status of the 9 local boards: "X", "O", "Tie", or None
        self.global_board_state = [[None for _ in range(3)] for _ in range(3)]
        
        # Track the actual buttons: [global_r][global_c][local_r][local_c]
        self.buttons = [[[[None for _ in range(3)] for _ in range(3)] for _ in range(3)] for _ in range(3)]
        # Track the local board frame containers for background color highlighting
        self.board_frames = [[None for _ in range(3)] for _ in range(3)]

        self.create_ui()

    def create_ui(self):
        # Top Status Label
        self.status_label = tk.Label(
            self, text="Player X's Turn - Play Anywhere!", 
            font=("Arial", 14, "bold"), bg="#222222", fg="#FFFFFF", pady=10
        )
        self.status_label.pack()

        # Master Outer Frame holding the 3x3 large grid
        master_frame = tk.Frame(self, bg="#444444", bd=4, relief="ridge")
        master_frame.pack(expand=True, fill="both", padx=20, pady=10)

        # Build the 3x3 Global Grid
        for gr in range(3):
            master_frame.grid_rowconfigure(gr, weight=1)
            master_frame.grid_columnconfigure(gr, weight=1)
            
            for gc in range(3):
                # Create a local sub-board frame
                sub_frame = tk.Frame(
                    master_frame, bg="#333333", bd=3, relief="groove", 
                    highlightbackground="#555555", highlightthickness=2
                )
                sub_frame.grid(row=gr, column=gc, sticky="nsew", padx=4, pady=4)
                self.board_frames[gr][gc] = sub_frame

                # Build the 3x3 Local Grid inside this frame
                for lr in range(3):
                    sub_frame.grid_rowconfigure(lr, weight=1)
                    sub_frame.grid_columnconfigure(lr, weight=1)
                    
                    for lc in range(3):
                        btn = tk.Button(
                            sub_frame, text="", font=("Arial", 12, "bold"),
                            bg="#333333", fg="#FFFFFF", activebackground="#555555",
                            command=lambda g_r=gr, g_c=gc, l_r=lr, l_c=lc: self.handle_click(g_r, g_c, l_r, l_c)
                        )
                        btn.grid(row=lr, column=lc, sticky="nsew", padx=1, pady=1)
                        self.buttons[gr][gc][lr][lc] = btn

        self.highlight_valid_boards()

    def handle_click(self, gr, gc, lr, lc):
        # 1. Validation Check: Is it an allowed board?
        if self.active_board is not None and self.active_board != (gr, gc):
            return
        
        # 2. Validation Check: Is the sub-board already won, or is the cell already taken?
        if self.global_board_state[gr][gc] is not None or self.buttons[gr][gc][lr][lc]["text"] != "":
            return

        # 3. Register the Move
        btn = self.buttons[gr][gc][lr][lc]
        btn.config(text=self.current_player, fg="#FF4A4A" if self.current_player == "X" else "#4A90E2")

        # 4. Check if this move wins the local 3x3 sub-board
        if self.check_local_win(gr, gc, self.current_player):
            self.global_board_state[gr][gc] = self.current_player
            self.mark_local_board_won(gr, gc, self.current_player)
            
            # Check if this local win clinches the entire global game
            if self.check_global_win(self.current_player):
                messagebox.showinfo("Game Over", f"Congratulations! Player {self.current_player} wins Super Tic-Tac-Toe!")
                self.reset_game()
                return
        elif self.check_local_tie(gr, gc):
            self.global_board_state[gr][gc] = "Tie"
            self.mark_local_board_won(gr, gc, "Tie")

        # 5. Check Global Tie
        if all(self.global_board_state[r][c] is not None for r in range(3) for c in range(3)):
            messagebox.showinfo("Game Over", "It's a global tie!")
            self.reset_game()
            return

        # 6. Rule Mechanic: Determine the next valid active board
        # The opponent is sent to the global coordinates corresponding to the picked local coordinates (lr, lc)
        if self.global_board_state[lr][lc] is None:
            self.active_board = (lr, lc)
        else:
            # If target sub-board is already completed, player can choose ANY incomplete board
            self.active_board = None

        # 7. Alternate Turn
        self.current_player = "O" if self.current_player == "X" else "X"
        self.update_status_label()
        self.highlight_valid_boards()

    def check_local_win(self, gr, gc, player):
        b = self.buttons[gr][gc]
        # Check rows & columns
        for i in range(3):
            if b[i][0]["text"] == b[i][1]["text"] == b[i][2]["text"] == player: return True
            if b[0][i]["text"] == b[1][i]["text"] == b[2][i]["text"] == player: return True
        # Check diagonals
        if b[0][0]["text"] == b[1][1]["text"] == b[2][2]["text"] == player: return True
        if b[0][2]["text"] == b[1][1]["text"] == b[2][0]["text"] == player: return True
        return False

    def check_local_tie(self, gr, gc):
        return all(self.buttons[gr][gc][r][c]["text"] != "" for r in range(3) for c in range(3))

    def check_global_win(self, player):
        g = self.global_board_state
        for i in range(3):
            if g[i][0] == g[i][1] == g[i][2] == player: return True
            if g[0][i] == g[1][i] == g[2][i] == player: return True
        if g[0][0] == g[1][1] == g[2][2] == player: return True
        if g[0][2] == g[1][1] == g[2][0] == player: return True
        return False

    def mark_local_board_won(self, gr, gc, winner):
        frame = self.board_frames[gr][gc]
        if winner == "Tie":
            frame.config(highlightbackground="#777777")
            color = "#555555"
        else:
            frame.config(highlightbackground="#FF4A4A" if winner == "X" else "#4A90E2")
            color = "#552222" if winner == "X" else "#222255"
        
        # Tint all buttons inside the captured sub-board
        for r in range(3):
            for c in range(3):
                self.buttons[gr][gc][r][c].config(bg=color, state="disabled")

    def highlight_valid_boards(self):
        for r in range(3):
            for c in range(3):
                # If sub-board is finished, keep it dimmed
                if self.global_board_state[r][c] is not None:
                    continue
                
                # Highlight logic
                if self.active_board is None or self.active_board == (r, c):
                    self.board_frames[r][c].config(highlightbackground="#2ECC71", highlightthickness=3) # Bright Green
                else:
                    self.board_frames[r][c].config(highlightbackground="#555555", highlightthickness=2) # Default

    def update_status_label(self):
        if self.active_board is None:
            location_str = "Play Anywhere!"
        else:
            location_str = f"Must play in Board ({self.active_board[0]+1}, {self.active_board[1]+1})"
        self.status_label.config(text=f"Player {self.current_player}'s Turn — {location_str}")

    def reset_game(self):
        self.destroy()
        new_game = SuperTicTacToe()
        new_game.mainloop()
