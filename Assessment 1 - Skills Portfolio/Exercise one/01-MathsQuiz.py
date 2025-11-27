# Exercise 1 - Space Math Adventure Quiz
# This is my math quiz game with different difficulty levels
# I used tkinter for the GUI and PIL for images

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
from enum import Enum
import math

from config.animations import AnimationManager, ScreenManager
from config.settings import *
from utils.helpers import MathHelper, PowerUpManager

# Color scheme for the game - wanted it to look space themed
# spent way too long picking these colors lol
PRIMARY_BG = "#020F1F"
PANEL_BG = "#071A3F"
INPUT_BG = "#04293A"
ENTRY_BG = "#074973"
ENTRY_ERROR_BG = "#360B0B"
ENTRY_TEXT_COLOR = "#E1F5FE"
ACCENT_CYAN = "#23C4ED"
ACCENT_GOLD = "#F1C40F"
ACCENT_ORANGE = "#FF8F34"
SUCCESS_COLOR = "#00E676"
WARNING_COLOR = "#FFB703"
ERROR_COLOR = "#FF4C60"
INFO_COLOR = "#4FC3F7"


# This function loads images and makes sure they dont get stretched weird
# had to look up how to preserve aspect ratio cause my images were getting squished
def load_image_with_aspect(path, max_width, max_height, remove_color=None):
    """Load image preserving aspect ratio"""
    try:
        original = Image.open(path).convert("RGBA")
        # Calculate aspect ratio preserving dimensions
        # basically checking if image is wider or taller than what we want
        original_ratio = original.width / original.height
        target_ratio = max_width / max_height
        
        if original_ratio > target_ratio:
            # Image is wider
            new_width = max_width
            new_height = int(max_width / original_ratio)
        else:
            # Image is taller
            new_height = max_height
            new_width = int(max_height * original_ratio)
        
        resized = original.resize((new_width, new_height), Image.LANCZOS)

        # This part removes black backgrounds from icons
        # was annoying having black boxes around my rocket and exit buttons
        if remove_color is not None:
            data = resized.getdata()
            cleaned = []
            target = tuple(remove_color)
            for pixel in data:
                # if pixel matches the color we want to remove, make it transparent
                if pixel[:3] == target:
                    cleaned.append((pixel[0], pixel[1], pixel[2], 0))
                else:
                    cleaned.append(pixel)
            resized.putdata(cleaned)

        return ImageTk.PhotoImage(resized)
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        # Create fallback image
        fallback = Image.new('RGBA', (max_width, max_height), color='#2C3E50')
        return ImageTk.PhotoImage(fallback)


# Helper function to show messages to the player
# makes it easier to give feedback without repeating code everywhere
def show_feedback(message, color="#FFFFFF", duration=1500):
    """Display smooth feedback messages in a consistent style."""
    if 'result_display' not in globals():
        return
    result_display.config(text=message, fg=color)
    # auto clear the message after a bit so it doesnt stay forever
    if duration:
        main_window.after(duration, lambda: result_display.config(text=""))


# Changes the input box color based on state
# red when theres an error, normal blue otherwise
def set_input_state(state="normal"):
    """Tint the answer box to reflect its current status."""
    if 'input_container' not in globals() or 'answer_input' not in globals():
        return

    if state == "error":
        # turn red when user enters invalid stuff
        input_container.config(bg=ENTRY_ERROR_BG, highlightbackground=ERROR_COLOR)
        answer_input.config(bg="#1B0000", fg=ENTRY_TEXT_COLOR)
    else:
        # normal blue color
        input_container.config(bg=INPUT_BG, highlightbackground=ACCENT_CYAN)
        answer_input.config(bg=ENTRY_BG, fg=ENTRY_TEXT_COLOR)

# === Game Difficulty Levels ===
# Using Enum cause it makes it easier to manage the different levels
# each level has: id, color, background image, min number, max number
class GameLevel(Enum):
    """Defines different challenge levels for space adventure"""
    BEGINNER = (0, "#4A6572", SPACE_BG_PATH, 1, 15)      # Simple numbers
    EXPLORER = (1, "#344955", PLANET_BG_PATH, 10, 50)   # Medium range
    MASTER = (2, "#232F34", GALAXY_BG_PATH, 50, 200)    # Complex challenges

    @property
    def level_id(self):
        return self.value[0]

    @property
    def theme_color(self):
        return self.value[1]

    @property
    def background_path(self):
        return self.value[2]

    @property
    def min_value(self):
        return self.value[3]

    @property
    def max_value(self):
        return self.value[4]


# === Game State Controller ===
# This class keeps track of everything happening in the game
# like score, what level, how many problems done, etc
class GameSession:
    """Manages the complete game state and progress"""
    def __init__(self):
        self.current_level = GameLevel.BEGINNER
        self.points = 0
        self.problems_solved = 0
        self.active_challenge = None  # stores the current math problem
        self.attempts_made = 0  # how many tries on current problem
        self.remaining_time = GAME_DURATION
        self.timer_reference = None  # need this to cancel timer if needed
        self.active_powerups = []  # list of active powerups
        self.powerup_charges = 3  # how many boosts player has left

    def initialize_new_game(self, selected_level=GameLevel.BEGINNER):
        """Prepare for a new game session"""
        self.current_level = selected_level
        self.points = 0
        self.problems_solved = 0
        self.active_challenge = None
        self.attempts_made = 0
        self.remaining_time = GAME_DURATION
        self.active_powerups = []
        self.powerup_charges = 3


# Global game session instance
Game = GameSession()


# === Core Game Mechanics ===
class GameEngine:
    """Handles all game logic and mathematical operations"""
    
    @staticmethod
    def show_level_selection():
        """Display the level selection interface"""
        display_screen(level_select_frame)
    
    @staticmethod
    def generate_number(level: GameLevel):
        """Create random numbers based on selected level"""
        return random.randint(level.min_value, level.max_value)
    
    @staticmethod
    def select_operation():
        """Randomly choose mathematical operation"""
        # Added multiplication to make it more interesting
        # weights make addition/subtraction more common than multiplication
        operations = ['+', '-', '*']
        weights = [40, 40, 20]  # 40% add, 40% subtract, 20% multiply
        return random.choices(operations, weights=weights)[0]
    
    @staticmethod
    def present_challenge(level: GameLevel):
        """Display a new mathematical challenge"""
        num1 = GameEngine.generate_number(level)
        num2 = GameEngine.generate_number(level)
        operation = GameEngine.select_operation()

        # Make sure subtraction gives positive answers (swap if needed)
        # and keep multiplication simple for beginners
        if operation == '-' and num1 < num2:
            num1, num2 = num2, num1  # swap so we dont get negative answers
        elif operation == '*' and level == GameLevel.BEGINNER:
            num2 = random.randint(2, 5)  # smaller numbers for beginners

        Game.active_challenge = (num1, num2, operation)
        
        # Update display elements
        challenge_title.config(text=f"CHALLENGE {Game.problems_solved + 1}/{MAX_CHALLENGES}")
        problem_display.config(text=f"{num1} {operation} {num2} = ?")
        result_display.config(text="")
        answer_input.delete(0, "end")
        answer_input.focus()
        Game.attempts_made = 0
        begin_countdown()
        
        return num1, num2, operation
    
    @staticmethod
    def verify_solution(num1, num2, operation, player_answer):
        """Check if player's answer is correct"""
        if operation == '+':
            correct = num1 + num2
        elif operation == '-':
            correct = num1 - num2
        else:  # multiplication
            correct = num1 * num2
            
        is_correct = player_answer == correct
        
        if is_correct:
            # give more points if they get it right first try
            base_points = 15 if Game.attempts_made == 0 else 7
            show_feedback(f"SUCCESS! +{base_points} POINTS", SUCCESS_COLOR, duration=1200)
            return True, base_points
        else:
            Game.attempts_made += 1
            # give them 2 chances total
            if Game.attempts_made < 2:
                show_feedback("NOT QUITE! TRY AGAIN!", WARNING_COLOR, duration=1200)
                answer_input.delete(0, "end")  # clear the input
                begin_countdown()  # restart timer
                return False, 0
            else:
                # show the answer if they fail twice
                show_feedback(f"ANSWER: {correct}", ERROR_COLOR, duration=None)
                return False, 0
    
    @staticmethod
    def show_final_results():
        """Display end-of-game results and rating"""
        final_score = Game.points
        maximum_score = 15 * MAX_CHALLENGES
        
        # Determine performance rating
        if final_score >= 135:
            rating = "COSMIC GENIUS 🌟"
            message = "Your math skills are out of this world!"
        elif final_score >= 120:
            rating = "GALACTIC SCHOLAR 🚀"
            message = "Amazing mathematical journey!"
        elif final_score >= 90:
            rating = "SPACE EXPLORER 🌌"
            message = "Great problem-solving skills!"
        elif final_score >= 60:
            rating = "PLANET TRAVELER 🪐"
            message = "Good effort! Keep practicing!"
        else:
            rating = "SPACE CADET 🌠"
            message = "The stars await your improvement!"
        
        summary = f"FINAL SCORE: {final_score}/{maximum_score}\nRANK: {rating}\n\n{message}\n\nEmbark on another adventure?"
        
        return summary, rating


# === Power-Up System ===
# Added powerups to make the game more fun
# player gets 3 boosts per game
def activate_time_boost():
    """Add extra time to current challenge"""
    if Game.powerup_charges > 0:
        Game.remaining_time += 15  # add 15 seconds
        Game.powerup_charges -= 1
        powerup_indicator.config(text=f"BOOSTS: {Game.powerup_charges}")
        show_feedback("+15 SECONDS! ⏰", INFO_COLOR, duration=1000)
    else:
        show_feedback("NO BOOSTS REMAINING! 😔", ERROR_COLOR)

def activate_double_points():
    """Double points for next correct answer"""
    if Game.powerup_charges > 0 and not any('double' in p for p in Game.active_powerups):
        Game.active_powerups.append('double_points')
        Game.powerup_charges -= 1
        powerup_indicator.config(text=f"BOOSTS: {Game.powerup_charges}")
        show_feedback("NEXT ANSWER WORTH DOUBLE! 💎", "#FF5AA5")
    elif Game.powerup_charges <= 0:
        show_feedback("NO BOOSTS REMAINING! 😔", ERROR_COLOR)
    else:
        show_feedback("DOUBLE POINTS ALREADY ACTIVE! ✨", WARNING_COLOR)

# Apply any active powerups to the points earned
def apply_powerup_effects(points):
    """Apply active power-up effects to scored points"""
    final_points = points
    
    # check if double points is active and apply it
    if 'double_points' in Game.active_powerups:
        final_points *= 2
        Game.active_powerups.remove('double_points')  # remove after using
        show_feedback(f"DOUBLE POINTS ACTIVATED! +{final_points} 🎉", "#FF5AA5")
    
    return final_points


# === Time Management System ===
def begin_countdown():
    """Initialize challenge timer"""
    Game.remaining_time = GAME_DURATION
    update_timer_display()

# Timer countdown - updates every second
def update_timer_display():
    """Update and manage the countdown timer"""
    if Game.remaining_time >= 0:
        # turn red when time is running out (less than 8 seconds)
        timer_indicator.config(
            text=f"TIME: {Game.remaining_time}s",
            fg=ERROR_COLOR if Game.remaining_time <= 8 else WARNING_COLOR
        )
        Game.remaining_time -= 1
        # schedule next update in 1 second
        Game.timer_reference = main_window.after(1000, update_timer_display)
    else:
        time_expired()  # time ran out

def stop_timer():
    """Halt the countdown timer"""
    if Game.timer_reference:
        main_window.after_cancel(Game.timer_reference)
        Game.timer_reference = None

def time_expired():
    """Handle timer completion"""
    num1, num2, operation = Game.active_challenge
    if operation == '+':
        correct = num1 + num2
    elif operation == '-':
        correct = num1 - num2
    else:
        correct = num1 * num2
        
    show_feedback(f"TIME'S UP! ANSWER: {correct}", "#FF4081", duration=None)
    disable_player_input()
    main_window.after(2000, advance_to_next)


# === Input Control System ===
def disable_player_input():
    """Prevent player interaction during transitions"""
    answer_input.config(state="disabled")
    submit_action.config(state="disabled")

def enable_player_input():
    """Allow player to interact with the game"""
    answer_input.config(state="normal")
    submit_action.config(state="normal")


# === Game Flow Control ===
def advance_to_next():
    """Progress to next challenge or conclude game"""
    stop_timer()
    Game.problems_solved += 1
    if Game.problems_solved < MAX_CHALLENGES:
        enable_player_input()
        GameEngine.present_challenge(Game.current_level)
    else:
        show_game_results()

# Check what the player entered
def check_player_answer():
    """Process and validate player's solution"""
    stop_timer()  # stop the timer while checking
    
    # make sure they entered a number, not text
    try:
        player_answer = int(answer_input.get())
    except ValueError:
        # show error if they typed something weird
        set_input_state("error")
        show_feedback("PLEASE ENTER A VALID NUMBER", ERROR_COLOR)
        main_window.after(800, set_input_state)  # reset color after a bit
        begin_countdown()
        return

    num1, num2, operation = Game.active_challenge
    
    is_correct, base_points = GameEngine.verify_solution(num1, num2, operation, player_answer)
    
    if is_correct:
        # Apply power-up effects before scoring (like double points)
        actual_points = apply_powerup_effects(base_points)
        Game.points += actual_points
        
        disable_player_input()  # lock input while showing result
        score_indicator.config(text=f"SCORE: {Game.points}/{15 * MAX_CHALLENGES}")
        # wait a bit then move to next problem
        main_window.after(1500, advance_to_next)
    else:
        # if they used up all attempts, move on
        if Game.attempts_made >= 2:
            disable_player_input()
            score_indicator.config(text=f"SCORE: {Game.points}/{15 * MAX_CHALLENGES}")
            main_window.after(2000, advance_to_next)

def start_space_adventure(selected_level):
    """Begin a new game with chosen difficulty"""
    Game.initialize_new_game(selected_level)
    enable_player_input()
    score_indicator.config(text=f"SCORE: {Game.points}/{15 * MAX_CHALLENGES}")
    powerup_indicator.config(text=f"BOOSTS: {Game.powerup_charges}")
    display_screen(game_frame)

    # Get or create screen background - this ensures background shows for all levels
    screen_manager = ScreenManager.get_screen_background(game_frame, selected_level)
    screen_manager.activate()

    # Elevate game interface elements
    game_elements = [
        game_back_control,
        info_panel,
        challenge_title,
        timer_indicator,
        score_indicator,
        problem_display,
        input_glow,
        input_container,
        result_display,
        powerup_frame
    ]
    for element in game_elements:
        element.lift()

    GameEngine.present_challenge(Game.current_level)

def show_game_results():
    """Display final game results"""
    stop_timer()
    result_summary, performance_rating = GameEngine.show_final_results()
    
    if messagebox.askyesno("Mission Complete!", result_summary):
        display_screen(main_menu_frame)
    else:
        main_window.quit()


# === Screen Management ===
def display_screen(screen):
    """Switch between different game screens"""
    AnimationManager.stop_all_animations()
    screen.tkraise()
    
    if screen == main_menu_frame:
        menu_animation.play()
    elif screen == level_select_frame:
        level_select_animation.play()


# === Main Application Window ===
# Create the main window
main_window = tk.Tk()
main_window.title("Space Math Adventure")
main_window.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
main_window.resizable(False, False)  # dont let them resize it

# Create the different screens (menu, level select, game)
# using frames that we can switch between
main_menu_frame = tk.Frame(main_window, bg="black")
level_select_frame = tk.Frame(main_window, bg="black")
game_frame = tk.Frame(main_window, bg=PRIMARY_BG)

# make all screens fill the window
for screen in (main_menu_frame, level_select_frame, game_frame):
    screen.place(relwidth=1, relheight=1)


# === Main Menu Screen ===
menu_background = tk.Label(main_menu_frame)
menu_background.place(x=0, y=0, relwidth=1, relheight=1)
menu_animation = AnimationManager(menu_background, MENU_BG_PATH, APP_WIDTH, APP_HEIGHT)

# Title Section
title_label = tk.Label(main_menu_frame, text="SPACE MATH ADVENTURE", 
                      font=("Arial", 32, "bold"), bg="black", fg="#FFD700",
                      pady=20)
title_label.place(relx=0.5, rely=0.2, anchor="center")

subtitle_label = tk.Label(main_menu_frame, text="Master Mathematics Among the Stars", 
                         font=("Arial", 16), bg="black", fg="#4FC3F7")
subtitle_label.place(relx=0.5, rely=0.3, anchor="center")

# Launch Adventure button - using image instead of text button
launch_image = load_image_with_aspect(START_IMG_PATH, 300, 65, remove_color=(0, 0, 0))
launch_button = tk.Label(main_menu_frame, image=launch_image, bg="black", cursor="hand2")
launch_button.image = launch_image  # need to keep reference or image disappears
launch_button.bind("<Button-1>", lambda e: GameEngine.show_level_selection())
launch_button.place(relx=0.5, rely=0.6, anchor="center")

# Exit Mission button
exit_image = load_image_with_aspect(QUIT_IMG_PATH, 300, 65, remove_color=(0, 0, 0))
exit_button = tk.Label(main_menu_frame, image=exit_image, bg="black", cursor="hand2")
exit_button.image = exit_image
exit_button.bind("<Button-1>", lambda e: main_window.quit())
exit_button.place(relx=0.5, rely=0.75, anchor="center")


# === Level Selection Screen ===
level_select_background = tk.Label(level_select_frame)
level_select_background.place(x=0, y=0, relwidth=1, relheight=1)
level_select_animation = AnimationManager(level_select_background, DIFFICULTY_BG_PATH, APP_WIDTH, APP_HEIGHT)

# Level selection title
level_title = tk.Label(level_select_frame, text="CHOOSE YOUR MISSION", 
                      font=("Arial", 28, "bold"), bg="black", fg="#FFD700")
level_title.place(relx=0.5, rely=0.1, anchor="center")

# Level selection options
space_levels = [
    ("BEGINNER", "Numbers 1-15\nBasic Operations", 150, GameLevel.BEGINNER),
    ("EXPLORER", "Numbers 10-50\nAll Operations", 250, GameLevel.EXPLORER),
    ("MASTER", "Numbers 50-200\nComplex Challenges", 350, GameLevel.MASTER)
]

for level_name, description, y_position, game_level in space_levels:
    # Level container
    level_container = tk.Frame(level_select_frame, bg="#2C3E50", relief=tk.RAISED, bd=2)
    level_container.place(x=200, y=y_position, width=560, height=80)
    
    # Level name
    name_label = tk.Label(level_container, text=level_name, font=("Arial", 18, "bold"),
                         bg="#2C3E50", fg="white", padx=20, pady=10)
    name_label.place(x=10, y=13)
    
    # Level description
    desc_label = tk.Label(level_container, text=description, font=("Arial", 11),
                         bg="#2C3E50", fg="lightblue", justify=tk.LEFT)
    desc_label.place(x=225, y=20)
    
    # Launch level button
    level_btn = tk.Label(level_container, text="LAUNCH", font=("Arial", 14, "bold"),
                        bg="#E74C3C", fg="white", cursor="hand2", 
                        padx=25, pady=12, relief=tk.RAISED, bd=3)
    level_btn.bind("<Button-1>", lambda e, gl=game_level: start_space_adventure(gl))
    level_btn.place(x=400, y=13)

# Return to menu
return_image = load_image_with_aspect(BACK_IMG_PATH, 300, 65)
return_button = tk.Label(level_select_frame, image=return_image, bg="black", cursor="hand2")
return_button.image = return_image
return_button.bind("<Button-1>", lambda e: display_screen(main_menu_frame))
return_button.place(relx=0.5, rely=0.9, anchor="center")


# === Game Play Screen ===
# Navigation control
game_return_image = load_image_with_aspect(BACK_IMG_PATH, 180, 50)
game_back_control = tk.Label(game_frame, image=game_return_image, bg="black", cursor="hand2")
game_back_control.image = game_return_image
game_back_control.bind("<Button-1>", lambda e: (stop_timer(), display_screen(level_select_frame)))
game_back_control.place(x=25, y=10)

# Challenge progress and indicators
info_panel = tk.Frame(
    game_frame,
    bg=PANEL_BG,
    highlightbackground=ACCENT_GOLD,
    highlightcolor=ACCENT_GOLD,
    highlightthickness=1,
    bd=0,
    padx=20,
    pady=12
)
info_panel.place(relx=0.5, y=85, anchor="center")

challenge_title = tk.Label(
    info_panel,
    font=("Arial", 20, "bold"),
    fg=ACCENT_GOLD,
    bg=PANEL_BG,
    padx=10
)
challenge_title.grid(row=0, column=0, padx=20)

timer_indicator = tk.Label(
    info_panel,
    font=("Arial", 16, "bold"),
    bg="#0A2A43",
    fg=WARNING_COLOR,
    padx=15,
    pady=6
)
timer_indicator.grid(row=0, column=1, padx=20)

score_indicator = tk.Label(
    info_panel,
    font=("Arial", 16, "bold"),
    bg="#0A2A43",
    fg=ACCENT_GOLD,
    padx=15,
    pady=6
)
score_indicator.grid(row=0, column=2, padx=20)

# Math problem display
problem_display = tk.Label(
    game_frame,
    font=("Arial", 26, "bold"),
    bg=PANEL_BG,
    fg="#FFFFFF",
    padx=40,
    pady=20,
    highlightbackground=ACCENT_CYAN,
    highlightthickness=2,
    bd=0
)
problem_display.place(relx=0.5, y=190, anchor="center")

# Answer input area - made it look nicer with a glow effect
input_glow = tk.Frame(game_frame, bg="#0D6EFD", bd=0, highlightthickness=0)
input_glow.place(relx=0.5, y=285, anchor="center")

input_container = tk.Frame(
    input_glow,
    bg=INPUT_BG,
    relief=tk.FLAT,
    bd=0,
    highlightbackground=ACCENT_CYAN,
    highlightthickness=3,  # cyan border
    padx=10,
    pady=10
)
input_container.pack()

# Player answer input - where they type their answer
answer_input = tk.Entry(
    input_container,
    font=("Arial", 22, "bold"),
    width=10,
    bg=ENTRY_BG,
    fg=ENTRY_TEXT_COLOR,
    insertbackground="#FFFFFF",
    relief=tk.FLAT,
    justify="center"
)
answer_input.pack(side=tk.LEFT, padx=12)
# pressing enter submits the answer
answer_input.bind('<Return>', lambda e: check_player_answer())
# reset color when they focus or type
answer_input.bind('<FocusIn>', lambda e: set_input_state())
answer_input.bind('<Key>', lambda e: set_input_state())
set_input_state()  # set initial color

# Submit action button
submit_action = tk.Button(
    input_container,
    text="SOLVE",
    font=("Arial", 16, "bold"),
    command=check_player_answer,
    bg=ACCENT_ORANGE,
    fg="#FFFFFF",
    activebackground="#FF9B54",
    relief=tk.FLAT,
    cursor="hand2",
    padx=25,
    pady=10
)
submit_action.pack(side=tk.LEFT, padx=(12, 5))

# Result feedback
result_display = tk.Label(
    game_frame,
    font=("Arial", 18, "bold"),
    bg=PRIMARY_BG,
    fg="#FFFFFF",
    pady=8
)
result_display.place(relx=0.5, y=360, anchor="center")

# Power-up controls
powerup_frame = tk.Frame(
    game_frame,
    bg=PANEL_BG,
    relief=tk.FLAT,
    bd=0,
    highlightbackground=ACCENT_CYAN,
    highlightthickness=1,
    padx=10,
    pady=10
)
powerup_frame.place(relx=0.82, y=300, anchor="center")

# Power-up title
powerup_title = tk.Label(
    powerup_frame,
    text="SPACE BOOSTS 🚀",
    font=("Arial", 13, "bold"),
    bg=PANEL_BG,
    fg=ACCENT_GOLD
)
powerup_title.pack(pady=(5, 10))

# Boost counter
powerup_indicator = tk.Label(
    powerup_frame,
    text="BOOSTS: 3",
    font=("Arial", 11, "bold"),
    bg=PANEL_BG,
    fg=SUCCESS_COLOR
)
powerup_indicator.pack()

# Time boost button
time_boost_btn = tk.Button(
    powerup_frame,
    text="⏰ TIME BOOST\n+15 Seconds",
    font=("Arial", 10, "bold"),
    command=activate_time_boost,
    bg="#1565C0",
    fg="white",
    activebackground="#1E88E5",
    relief=tk.FLAT,
    padx=15,
    pady=8,
    width=12,
    cursor="hand2"
)
time_boost_btn.pack(pady=8)

# Double points button  
double_points_btn = tk.Button(
    powerup_frame,
    text="💎 DOUBLE POINTS\nNext Answer x2",
    font=("Arial", 10, "bold"),
    command=activate_double_points,
    bg="#9C27B0",
    fg="white",
    activebackground="#AB47BC",
    relief=tk.FLAT,
    padx=15,
    pady=8,
    width=12,
    cursor="hand2"
)
double_points_btn.pack(pady=8)

# Power-up instructions
instructions = tk.Label(
    powerup_frame,
    text="Use boosts wisely!\nLimited supply.",
    font=("Arial", 9),
    bg=PANEL_BG,
    fg="#B0BEC5"
)
instructions.pack(pady=(10, 5))


# Initialize application - start with the main menu
display_screen(main_menu_frame)
main_window.mainloop()  # start the event loop