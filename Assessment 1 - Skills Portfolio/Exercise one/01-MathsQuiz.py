import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
from enum import Enum
import math

from config.animations import AnimationManager, ScreenManager
from config.settings import *
from utils.helpers import MathHelper, PowerUpManager


# Image loading helper with aspect ratio preservation
def load_image_with_aspect(path, max_width, max_height):
    """Load image preserving aspect ratio"""
    try:
        original = Image.open(path)
        # Calculate aspect ratio preserving dimensions
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
        return ImageTk.PhotoImage(resized)
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        # Create fallback image
        fallback = Image.new('RGB', (max_width, max_height), color='#2C3E50')
        return ImageTk.PhotoImage(fallback)

# === Game Difficulty Levels ===
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
class GameSession:
    """Manages the complete game state and progress"""
    def __init__(self):
        self.current_level = GameLevel.BEGINNER
        self.points = 0
        self.problems_solved = 0
        self.active_challenge = None
        self.attempts_made = 0
        self.remaining_time = GAME_DURATION
        self.timer_reference = None
        self.active_powerups = []
        self.powerup_charges = 3

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
        operations = ['+', '-', '*']  # Added multiplication for variety
        weights = [40, 40, 20]  # Weighted probability
        return random.choices(operations, weights=weights)[0]
    
    @staticmethod
    def present_challenge(level: GameLevel):
        """Display a new mathematical challenge"""
        num1 = GameEngine.generate_number(level)
        num2 = GameEngine.generate_number(level)
        operation = GameEngine.select_operation()

        # Ensure positive results and reasonable difficulty
        if operation == '-' and num1 < num2:
            num1, num2 = num2, num1
        elif operation == '*' and level == GameLevel.BEGINNER:
            num2 = random.randint(2, 5)  # Simpler multiplication for beginners

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
            base_points = 15 if Game.attempts_made == 0 else 7
            result_display.config(text=f"SUCCESS! +{base_points} POINTS", fg="#4CAF50")
            return True, base_points
        else:
            Game.attempts_made += 1
            if Game.attempts_made < 2:
                result_display.config(text="NOT QUITE! TRY AGAIN!", fg="#FF9800")
                answer_input.delete(0, "end")
                begin_countdown()
                return False, 0
            else:
                result_display.config(text=f"ANSWER: {correct}", fg="#F44336")
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
def activate_time_boost():
    """Add extra time to current challenge"""
    if Game.powerup_charges > 0:
        Game.remaining_time += 15
        Game.powerup_charges -= 1
        powerup_indicator.config(text=f"BOOSTS: {Game.powerup_charges}")
        result_display.config(text="+15 SECONDS! ⏰", fg="#2196F3")
        main_window.after(1000, lambda: result_display.config(text=""))
    else:
        result_display.config(text="NO BOOSTS REMAINING! 😔", fg="#FF5252")
        main_window.after(1500, lambda: result_display.config(text=""))

def activate_double_points():
    """Double points for next correct answer"""
    if Game.powerup_charges > 0 and not any('double' in p for p in Game.active_powerups):
        Game.active_powerups.append('double_points')
        Game.powerup_charges -= 1
        powerup_indicator.config(text=f"BOOSTS: {Game.powerup_charges}")
        result_display.config(text="NEXT ANSWER WORTH DOUBLE! 💎", fg="#E91E63")
        main_window.after(1500, lambda: result_display.config(text=""))
    elif Game.powerup_charges <= 0:
        result_display.config(text="NO BOOSTS REMAINING! 😔", fg="#FF5252")
        main_window.after(1500, lambda: result_display.config(text=""))
    else:
        result_display.config(text="DOUBLE POINTS ALREADY ACTIVE! ✨", fg="#FF9800")
        main_window.after(1500, lambda: result_display.config(text=""))

def apply_powerup_effects(points):
    """Apply active power-up effects to scored points"""
    final_points = points
    
    if 'double_points' in Game.active_powerups:
        final_points *= 2
        Game.active_powerups.remove('double_points')
        result_display.config(text=f"DOUBLE POINTS ACTIVATED! +{final_points} 🎉", fg="#E91E63")
        main_window.after(1500, lambda: result_display.config(text=""))
    
    return final_points


# === Time Management System ===
def begin_countdown():
    """Initialize challenge timer"""
    Game.remaining_time = GAME_DURATION
    update_timer_display()

def update_timer_display():
    """Update and manage the countdown timer"""
    if Game.remaining_time >= 0:
        timer_indicator.config(
            text=f"TIME: {Game.remaining_time}s",
            fg="#FF5252" if Game.remaining_time <= 8 else "#FFD740"
        )
        Game.remaining_time -= 1
        Game.timer_reference = main_window.after(1000, update_timer_display)
    else:
        time_expired()

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
        
    result_display.config(text=f"TIME'S UP! ANSWER: {correct}", fg="#FF4081")
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

def check_player_answer():
    """Process and validate player's solution"""
    stop_timer()
    
    try:
        player_answer = int(answer_input.get())
    except ValueError:
        result_display.config(text="PLEASE ENTER A VALID NUMBER", fg="#FF5252")
        begin_countdown()
        return

    num1, num2, operation = Game.active_challenge
    
    is_correct, base_points = GameEngine.verify_solution(num1, num2, operation, player_answer)
    
    if is_correct:
        # Apply power-up effects before scoring
        actual_points = apply_powerup_effects(base_points)
        Game.points += actual_points
        
        disable_player_input()
        score_indicator.config(text=f"SCORE: {Game.points}/{15 * MAX_CHALLENGES}")
        main_window.after(1500, advance_to_next)
    else:
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
    game_elements = [game_back_control, challenge_title, timer_indicator, 
                     problem_display, input_container, result_display, score_indicator,
                     powerup_frame]
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
main_window = tk.Tk()
main_window.title("Space Math Adventure")
main_window.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
main_window.resizable(False, False)

# Create application screens
main_menu_frame = tk.Frame(main_window, bg="black")
level_select_frame = tk.Frame(main_window, bg="black")
game_frame = tk.Frame(main_window, bg="black")

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

# Launch Adventure button
launch_image = load_image_with_aspect(START_IMG_PATH, 300, 65)
launch_button = tk.Label(main_menu_frame, image=launch_image, bg="black", cursor="hand2")
launch_button.image = launch_image
launch_button.bind("<Button-1>", lambda e: GameEngine.show_level_selection())
launch_button.place(relx=0.5, rely=0.6, anchor="center")

# Exit Mission button
exit_image = load_image_with_aspect(QUIT_IMG_PATH, 300, 65)
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

# Challenge progress
challenge_title = tk.Label(game_frame, font=("Arial", 22, "bold"), 
                          fg="#FFD700", bg="black")
challenge_title.place(relx=0.5, y=90, anchor="center")

# Time indicator
timer_indicator = tk.Label(game_frame, font=("Arial", 16, "bold"), 
                          bg="black", fg="#FFD740", padx=10, pady=5)
timer_indicator.place(relx=0.5, y=140, anchor="center")

# Math problem display
problem_display = tk.Label(game_frame, font=("Arial", 24, "bold"), 
                          bg="black", fg="#FFFFFF", padx=20, pady=10)
problem_display.place(relx=0.5, y=200, anchor="center")

# Answer input area
input_container = tk.Frame(game_frame, bg="#1B5E20", relief=tk.RAISED, bd=3)
input_container.place(relx=0.5, y=280, anchor="center")

# Player answer input
answer_input = tk.Entry(input_container, font=("Arial", 20, "bold"), width=12,
                       bg="#1B5E20", fg="#FFFFFF", insertbackground="#FFFFFF",
                       relief=tk.SOLID, bd=4, justify="center")
answer_input.pack(side=tk.LEFT, padx=12, pady=10)
answer_input.bind('<Return>', lambda e: check_player_answer())

# Submit action button
submit_action = tk.Button(input_container, text="SOLVE", font=("Arial", 14, "bold"),
                         command=check_player_answer, bg="#E65100", fg="#FFFFFF",
                         activebackground="#FF5722", relief=tk.RAISED, bd=4,
                         cursor="hand2", padx=25, pady=10)
submit_action.pack(side=tk.LEFT, padx=12, pady=10)

# Result feedback
result_display = tk.Label(game_frame, font=("Arial", 16, "bold"), 
                         bg="black", fg="#FFFFFF", padx=10, pady=5)
result_display.place(relx=0.5, y=340, anchor="center")

# Score tracking
score_indicator = tk.Label(game_frame, font=("Arial", 16, "bold"), 
                          bg="black", fg="#FFD700", padx=10, pady=5)
score_indicator.place(relx=0.5, y=380, anchor="center")

# Power-up controls
powerup_frame = tk.Frame(game_frame, bg="black", relief=tk.RAISED, bd=2)
powerup_frame.place(relx=0.85, y=150, anchor="center")

# Power-up title
powerup_title = tk.Label(powerup_frame, text="SPACE BOOSTS 🚀", 
                        font=("Arial", 12, "bold"), bg="black", fg="#FFD700")
powerup_title.pack(pady=(5, 10))

# Boost counter
powerup_indicator = tk.Label(powerup_frame, text="BOOSTS: 3", 
                            font=("Arial", 11, "bold"), bg="black", fg="#00E676")
powerup_indicator.pack()

# Time boost button
time_boost_btn = tk.Button(powerup_frame, text="⏰ TIME BOOST\n+15 Seconds", 
                          font=("Arial", 10, "bold"), command=activate_time_boost, 
                          bg="#01579B", fg="white", activebackground="#0277BD",
                          relief=tk.RAISED, bd=3, padx=15, pady=8, width=12,
                          cursor="hand2")
time_boost_btn.pack(pady=8)

# Double points button  
double_points_btn = tk.Button(powerup_frame, text="💎 DOUBLE POINTS\nNext Answer x2", 
                             font=("Arial", 10, "bold"), command=activate_double_points,
                             bg="#880E4F", fg="white", activebackground="#AD1457",
                             relief=tk.RAISED, bd=3, padx=15, pady=8, width=12,
                             cursor="hand2")
double_points_btn.pack(pady=8)

# Power-up instructions
instructions = tk.Label(powerup_frame, text="Use boosts wisely!\nLimited supply.", 
                       font=("Arial", 9), bg="black", fg="#B0BEC5")
instructions.pack(pady=(10, 5))


# Initialize application
display_screen(main_menu_frame)
main_window.mainloop()