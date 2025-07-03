# ping_pong_game_python.py

import tkinter as tk
from tkinter import messagebox
import random
import time

class PingPongGame:
    def __init__(self, master):
        """
        Initializes the Ping Pong Game application with Tkinter.
        """
        self.master = master
        master.title("Python Pong Master")
        master.geometry("800x700") # Increased height to accommodate buttons and title
        master.resizable(True, True)
        master.config(bg="#1c1c2c") # Deeper dark background

        self.game_running = False
        self.player1_score = 0
        self.player2_score = 0
        self.winning_score = 5

        # --- Title ---
        self.title_label = tk.Label(master, text="PONG MASTER", font=("Inter", 30, "bold"), fg="white", bg="#1c1c2c")
        self.title_label.pack(pady=10)

        # --- Score Board ---
        self.score_frame = tk.Frame(master, bg="#3a3a4a", padx=15, pady=10, bd=0, relief="flat", highlightbackground="#6a5acd", highlightthickness=2)
        self.score_frame.pack(pady=10, padx=20, fill="x")
        self.score_frame.config(highlightbackground="#6a5acd", highlightthickness=3) # Vibrant purple border for scoreboard

        self.player1_score_label = tk.Label(self.score_frame, text="PLAYER 1: 0", font=("Inter", 24, "bold"), fg="#8be9fd", bg="#3a3a4a")
        self.player1_score_label.pack(side="left", expand=True)

        self.player2_score_label = tk.Label(self.score_frame, text="PLAYER 2: 0", font=("Inter", 24, "bold"), fg="#8be9fd", bg="#3a3a4a")
        self.player2_score_label.pack(side="right", expand=True)

        # --- Canvas for Game ---
        self.canvas = tk.Canvas(master, bg="#0d0d1a", bd=0, highlightthickness=3, highlightbackground="#6a5acd")
        self.canvas.pack(pady=15, padx=20, fill="both", expand=True)

        # Game dimensions (initial values, will be adjusted by resize_game_elements)
        self.canvas_width = 700
        self.canvas_height = 400
        self.canvas.bind("<Configure>", self.on_canvas_resize) # Bind resize event

        # Game elements properties
        self.paddle_width = 10
        self.paddle_height = 100
        self.ball_radius = 10
        self.ball_speed = 5 # Base speed

        self.player1_paddle = self.canvas.create_rectangle(
            0, (self.canvas_height - self.paddle_height) / 2,
            self.paddle_width, (self.canvas_height + self.paddle_height) / 2,
            fill="#50fa7b" # Green paddle
        )
        self.player2_paddle = self.canvas.create_rectangle(
            self.canvas_width - self.paddle_width, (self.canvas_height - self.paddle_height) / 2,
            self.canvas_width, (self.canvas_height + self.paddle_height) / 2,
            fill="#50fa7b" # Green paddle
        )
        self.ball = self.canvas.create_oval(
            (self.canvas_width / 2) - self.ball_radius, (self.canvas_height / 2) - self.ball_radius,
            (self.canvas_width / 2) + self.ball_radius, (self.canvas_height / 2) + self.ball_radius,
            fill="#f1fa8c" # Yellowish ball
        )
        self.center_line = self.canvas.create_line(
            self.canvas_width / 2, 0,
            self.canvas_width / 2, self.canvas_height,
            fill="#6272a4", dash=(10, 10) # Muted purple dashed line
        )

        self.ball_dx = self.ball_speed
        self.ball_dy = self.ball_speed

        # --- Game Status ---
        self.game_status_label = tk.Label(master, text="PRESS \"START GAME\" TO BEGIN!", font=("Inter", 16, "bold"), fg="#ff79c6", bg="#1c1c2c")
        self.game_status_label.pack(pady=10)

        # --- Control Buttons ---
        self.button_frame = tk.Frame(master, bg="#1c1c2c")
        self.button_frame.pack(pady=10)

        # Custom button styling function
        def create_styled_button(parent, text, command):
            button = tk.Button(parent, text=text, command=command,
                               font=("Inter", 12, "bold"), fg="white",
                               bg="#bd93f9", # Base purple color for gradient effect
                               activebackground="#ff79c6", # Active pink color
                               relief="flat", bd=0, padx=20, pady=10,
                               cursor="hand2",
                               width=15) # Fixed width for consistency
            # Apply gradient and shadow effects using Tkinter's internal styling or by drawing on a canvas if needed for complex effects.
            # For simplicity, we'll use a solid color with activebackground.
            button.bind("<Enter>", lambda e: button.config(bg="#ff79c6")) # Hover effect
            button.bind("<Leave>", lambda e: button.config(bg="#bd93f9")) # Leave effect
            button.pack(side="left", padx=10)
            return button

        self.start_button = create_styled_button(self.button_frame, "START GAME", self.start_game)
        self.reset_button = create_styled_button(self.button_frame, "RESET GAME", self.reset_game)
        self.how_to_play_button = create_styled_button(self.button_frame, "HOW TO PLAY", self.show_how_to_play)

        # Bind mouse and touch events for player paddle
        self.canvas.bind("<Motion>", self.move_player_paddle)
        self.canvas.bind("<B1-Motion>", self.move_player_paddle) # For dragging with left mouse button
        self.canvas.bind("<ButtonPress-1>", self.move_player_paddle) # For initial click positioning

        # For touch events (Tkinter on desktop doesn't directly support touch, but mouse events often map)
        # On some systems, <Motion> with a mouse can also trigger for touch if simulated.
        # For a truly robust touch solution, a different library might be needed, or specific OS/Tkinter versions.

        self.reset_game() # Initialize game state on startup

    def on_canvas_resize(self, event):
        """
        Adjusts game element positions and sizes when the canvas is resized.
        """
        self.canvas_width = event.width
        self.canvas_height = event.height

        # Update ball position relative to new center
        ball_coords = self.canvas.coords(self.ball)
        current_ball_center_x = (ball_coords[0] + ball_coords[2]) / 2
        current_ball_center_y = (ball_coords[1] + ball_coords[3]) / 2

        # Calculate new center and move ball
        new_ball_x1 = (self.canvas_width / 2) - self.ball_radius
        new_ball_y1 = (self.canvas_height / 2) - self.ball_radius
        new_ball_x2 = (self.canvas_width / 2) + self.ball_radius
        new_ball_y2 = (self.canvas_height / 2) + self.ball_radius
        self.canvas.coords(self.ball, new_ball_x1, new_ball_y1, new_ball_x2, new_ball_y2)

        # Update paddle positions relative to new canvas size
        self.canvas.coords(self.player1_paddle,
                           0, (self.canvas_height - self.paddle_height) / 2,
                           self.paddle_width, (self.canvas_height + self.paddle_height) / 2)
        self.canvas.coords(self.player2_paddle,
                           self.canvas_width - self.paddle_width, (self.canvas_height - self.paddle_height) / 2,
                           self.canvas_width, (self.canvas_height + self.paddle_height) / 2)

        # Update center line
        self.canvas.coords(self.center_line,
                           self.canvas_width / 2, 0,
                           self.canvas_width / 2, self.canvas_height)

        # Redraw everything
        self.canvas.update_idletasks()


    def draw_elements(self):
        """
        Redraws all game elements on the canvas.
        """
        # Tkinter automatically manages drawing when coords are updated,
        # but explicitly updating idletasks can ensure immediate redraw.
        pass # No explicit drawing needed here as coords are updated directly

    def move_player_paddle(self, event):
        """
        Moves the player's paddle based on mouse/touch Y position.
        """
        if self.game_running:
            y = event.y - self.paddle_height / 2
            # Keep paddle within canvas bounds
            if y < 0:
                y = 0
            elif y + self.paddle_height > self.canvas_height:
                y = self.canvas_height - self.paddle_height
            self.canvas.coords(self.player1_paddle, 0, y, self.paddle_width, y + self.paddle_height)

    def move_ai_paddle(self):
        """
        Moves the AI paddle to follow the ball.
        """
        ball_coords = self.canvas.coords(self.ball)
        ball_center_y = (ball_coords[1] + ball_coords[3]) / 2

        paddle2_coords = self.canvas.coords(self.player2_paddle)
        paddle2_center_y = (paddle2_coords[1] + paddle2_coords[3]) / 2

        deviation = 0.3 * self.paddle_height # How much the AI reacts to the ball's position

        if ball_center_y > paddle2_center_y + deviation:
            self.canvas.move(self.player2_paddle, 0, min(self.ball_speed * 0.8, self.canvas_height - paddle2_coords[3]))
        elif ball_center_y < paddle2_center_y - deviation:
            self.canvas.move(self.player2_paddle, 0, -min(self.ball_speed * 0.8, paddle2_coords[1]))

        # Keep AI paddle within bounds
        current_paddle2_y1 = self.canvas.coords(self.player2_paddle)[1]
        current_paddle2_y2 = self.canvas.coords(self.player2_paddle)[3]
        if current_paddle2_y1 < 0:
            self.canvas.coords(self.player2_paddle, self.canvas_width - self.paddle_width, 0, self.canvas_width, self.paddle_height)
        elif current_paddle2_y2 > self.canvas_height:
            self.canvas.coords(self.player2_paddle, self.canvas_width - self.paddle_width, self.canvas_height - self.paddle_height, self.canvas_width, self.canvas_height)


    def move_ball(self):
        """
        Updates the ball's position and handles collisions.
        """
        self.canvas.move(self.ball, self.ball_dx, self.ball_dy)

        ball_coords = self.canvas.coords(self.ball)
        ball_x1, ball_y1, ball_x2, ball_y2 = ball_coords

        # Wall collision (top/bottom)
        if ball_y2 > self.canvas_height or ball_y1 < 0:
            self.ball_dy *= -1

        # Paddle collision (Player 1)
        player1_paddle_coords = self.canvas.coords(self.player1_paddle)
        if ball_x1 < player1_paddle_coords[2] and \
           ball_y2 > player1_paddle_coords[1] and \
           ball_y1 < player1_paddle_coords[3]:
            self.ball_dx *= -1
            self.ball_speed += 0.2 # Increase speed on hit
            self.ball_dx = random.choice([-1, 1]) * self.ball_speed # Randomize direction after hit
            self.ball_dy = random.choice([-1, 1]) * self.ball_speed


        # Paddle collision (Player 2 - AI)
        player2_paddle_coords = self.canvas.coords(self.player2_paddle)
        if ball_x2 > player2_paddle_coords[0] and \
           ball_y2 > player2_paddle_coords[1] and \
           ball_y1 < player2_paddle_coords[3]:
            self.ball_dx *= -1
            self.ball_speed += 0.2 # Increase speed on hit
            self.ball_dx = random.choice([-1, 1]) * self.ball_speed
            self.ball_dy = random.choice([-1, 1]) * self.ball_speed

        # Scoring
        if ball_x1 < 0: # Ball passed Player 1's paddle
            self.player2_score += 1
            self.update_scores()
            self.reset_ball()
            self.ball_speed = 5 # Reset ball speed after scoring
            self.check_win()
        elif ball_x2 > self.canvas_width: # Ball passed Player 2's paddle
            self.player1_score += 1
            self.update_scores()
            self.reset_ball()
            self.ball_speed = 5 # Reset ball speed after scoring
            self.check_win()

        if self.game_running:
            self.master.after(20, self.game_loop) # Call game_loop every 20ms

    def reset_ball(self):
        """
        Resets the ball to the center and gives it a random initial direction.
        """
        self.canvas.coords(self.ball,
                           (self.canvas_width / 2) - self.ball_radius, (self.canvas_height / 2) - self.ball_radius,
                           (self.canvas_width / 2) + self.ball_radius, (self.canvas_height / 2) + self.ball_radius)
        self.ball_dx = (1 if random.random() > 0.5 else -1) * self.ball_speed
        self.ball_dy = (1 if random.random() > 0.5 else -1) * self.ball_speed

    def update_scores(self):
        """
        Updates the score display labels.
        """
        self.player1_score_label.config(text=f"PLAYER 1: {self.player1_score}")
        self.player2_score_label.config(text=f"PLAYER 2: {self.player2_score}")

    def update_game_status(self, message):
        """
        Updates the game status message label.
        """
        self.game_status_label.config(text=message)

    def check_win(self):
        """
        Checks if a player has reached the winning score.
        """
        if self.player1_score >= self.winning_score:
            self.update_game_status(f"PLAYER 1 WINS! FINAL SCORE: {self.player1_score}-{self.player2_score}")
            self.game_running = False
            messagebox.showinfo("Game Over", f"PLAYER 1 WINS! Final Score: {self.player1_score}-{self.player2_score}")
        elif self.player2_score >= self.winning_score:
            self.update_game_status(f"PLAYER 2 WINS! FINAL SCORE: {self.player1_score}-{self.player2_score}")
            self.game_running = False
            messagebox.showinfo("Game Over", f"PLAYER 2 WINS! Final Score: {self.player1_score}-{self.player2_score}")

    def game_loop(self):
        """
        The main game loop, responsible for moving elements and redrawing.
        """
        if self.game_running:
            self.move_ball()
            self.move_ai_paddle()
            # No explicit draw_elements call needed here as canvas.move updates directly
            # The after method schedules the next call

    def start_game(self):
        """
        Starts the game.
        """
        if not self.game_running:
            self.game_running = True
            self.player1_score = 0
            self.player2_score = 0
            self.update_scores()
            self.reset_ball()
            self.ball_speed = 5 # Reset ball speed at game start
            self.update_game_status("GAME ON!")
            self.game_loop()

    def reset_game(self):
        """
        Resets the game to its initial state.
        """
        self.game_running = False
        self.player1_score = 0
        self.player2_score = 0
        self.update_scores()
        self.reset_ball()
        self.ball_speed = 5 # Reset ball speed
        # Reset paddle positions
        self.canvas.coords(self.player1_paddle,
                           0, (self.canvas_height - self.paddle_height) / 2,
                           self.paddle_width, (self.canvas_height + self.paddle_height) / 2)
        self.canvas.coords(self.player2_paddle,
                           self.canvas_width - self.paddle_width, (self.canvas_height - self.paddle_height) / 2,
                           self.canvas_width, (self.canvas_height + self.paddle_height) / 2)
        self.update_game_status("GAME RESET. PRESS 'START GAME' TO PLAY!")

    def show_how_to_play(self):
        """
        Displays a 'How to Play' information box.
        """
        messagebox.showinfo(
            "How to Play Pong Master",
            "Welcome to Pong Master! Here's how to play this classic arcade game:\n\n"
            "1. Objective: Be the first player to score 5 points against your opponent.\n\n"
            "2. Your Paddle (Left):\n"
            "   - Mouse: Move your mouse cursor up and down over the game canvas to control your paddle's vertical position.\n\n"
            "3. Opponent (Right): The right paddle is controlled by the computer AI.\n\n"
            "4. Scoring: You score a point when the ball passes the opponent's paddle and goes off their side of the screen. The opponent scores if the ball passes your paddle.\n\n"
            "5. Ball Speed: The ball's speed will slightly increase each time it hits a paddle, making the game progressively more challenging!\n\n"
            "Good luck, and have fun mastering Pong!"
        )


if __name__ == "__main__":
    root = tk.Tk()
    game = PingPongGame(root)
    root.mainloop()
