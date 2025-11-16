import tkinter as tk
from tkinter import messagebox
import random
from enum import Enum

# === Difficulty Levels ===
class Difficulty(Enum):
    EASY = (0, "#27AE60", "#2ECC71", 0, 9)  # Green theme
    MEDIUM = (1, "#F39C12", "#E67E22", 10, 99)  # Orange theme  
    HARD = (2, "#E74C3C", "#C0392B", 100, 999)  # Red theme

    @property
    def level(self):
        return self.value[0]

    @property
    def primary_color(self):
        return self.value[1]

    @property
    def secondary_color(self):
        return self.value[2]

    @property
    def min_val(self):
        return self.value[3]

    @property
    def max_val(self):
        return self.value[4]

# === Quiz State Management ===
class QuizContext:
    def __init__(self):
        self.difficulty = Difficulty.EASY
        self.score = 0
        self.question_count = 0
        self.current_question = None
        self.attempts = 0
        self.time_remaining = 30  # 30 seconds per question
        self.timer_id = None

    def reset(self, new_difficulty=Difficulty.EASY):
        self.difficulty = new_difficulty
        self.score = 0
        self.question_count = 0
        self.current_question = None
        self.attempts = 0
        self.time_remaining = 30

Context = QuizContext()

# === Quiz Logic ===
class QuizLogic:
    @staticmethod
    def random_int(difficulty: Difficulty):
        return random.randint(difficulty.min_val, difficulty.max_val)

    @staticmethod
    def decide_operation():
        return random.choice(['+', '-'])

    @staticmethod
    def generate_problem(difficulty: Difficulty):
        num1 = QuizLogic.random_int(difficulty)
        num2 = QuizLogic.random_int(difficulty)
        op = QuizLogic.decide_operation()

        if op == '-' and num1 < num2:
            num1, num2 = num2, num1

        return num1, num2, op

    @staticmethod
    def calculate_correct_answer(num1, num2, op):
        return num1 + num2 if op == '+' else num1 - num2

    @staticmethod
    def check_answer(num1, num2, op, user_answer):
        return user_answer == QuizLogic.calculate_correct_answer(num1, num2, op)

# === Timer Functions ===
def start_timer():
    Context.time_remaining = 30
    update_timer()

def update_timer():
    if Context.time_remaining >= 0:
        timer_label.config(
            text=f"⏰ TIME: {Context.time_remaining}s",
            fg="#FF0000" if Context.time_remaining <= 10 else "#FFA500"
        )
        Context.time_remaining -= 1
        Context.timer_id = root.after(1000, update_timer)
    else:
        time_up()

def stop_timer():
    if Context.timer_id:
        root.after_cancel(Context.timer_id)
        Context.timer_id = None

def time_up():
    num1, num2, op = Context.current_question
    correct = QuizLogic.calculate_correct_answer(num1, num2, op)
    feedback_label.config(text=f"⏰ TIME'S UP! ANSWER: {correct}", fg="red")
    disable_inputs()
    root.after(2000, next_question)

# === Question Display ===
def display_problem():
    num1, num2, op = QuizLogic.generate_problem(Context.difficulty)
    Context.current_question = (num1, num2, op)
    
    title_label.config(text=f"🎯 QUESTION {Context.question_count + 1}/10")
    question_label.config(text=f"{num1} {op} {num2} = ?")
    feedback_label.config(text="")
    answer_entry.delete(0, "end")
    answer_entry.focus_set()
    Context.attempts = 0
    start_timer()

# === Answer Checking ===
def check_answer():
    stop_timer()
    
    try:
        user_answer = int(answer_entry.get())
    except ValueError:
        feedback_label.config(text="❌ ENTER A VALID NUMBER!", fg="red")
        start_timer()
        return

    num1, num2, op = Context.current_question

    if QuizLogic.check_answer(num1, num2, op, user_answer):
        points = 10 if Context.attempts == 0 else 5
        Context.score += points
        feedback_label.config(text=f"✅ CORRECT! +{points} POINTS", fg="#00FF00")
        disable_inputs()
        root.after(1500, next_question)
    else:
        Context.attempts += 1
        if Context.attempts < 2:
            feedback_label.config(text="❌ INCORRECT! TRY AGAIN!", fg="#FF4500")
            answer_entry.delete(0, "end")
            start_timer()
        else:
            correct = QuizLogic.calculate_correct_answer(num1, num2, op)
            feedback_label.config(text=f"❌ INCORRECT! ANSWER: {correct}", fg="orange")
            disable_inputs()
            root.after(2000, next_question)

    score_label.config(text=f"🏆 SCORE: {Context.score}/100")

# === Input Control ===
def disable_inputs():
    answer_entry.config(state="disabled")
    submit_btn.config(state="disabled")

def enable_inputs():
    answer_entry.config(state="normal")
    submit_btn.config(state="normal")

# === Navigation ===
def next_question():
    stop_timer()
    Context.question_count += 1
    if Context.question_count < 10:  # 10 questions total
        enable_inputs()
        display_problem()
    else:
        display_results()

def start_quiz_with_difficulty(diff):
    Context.reset(diff)
    enable_inputs()
    score_label.config(text=f"🏆 SCORE: {Context.score}/100")
    show_frame(quiz_frame)
    
    # Update colors based on difficulty
    update_quiz_colors(diff)
    display_problem()

def update_quiz_colors(difficulty):
    """Update quiz frame colors based on difficulty"""
    primary = difficulty.primary_color
    secondary = difficulty.secondary_color
    
    # Update background and element colors
    quiz_frame.config(bg=primary)
    title_label.config(bg=primary)
    question_label.config(bg=primary)
    feedback_label.config(bg=primary)
    score_label.config(bg=primary)
    entry_frame.config(bg=secondary)
    answer_entry.config(bg=secondary)
    submit_btn.config(bg=secondary, activebackground=primary)

def display_results():
    stop_timer()
    score = Context.score

    # Calculate grade
    if score >= 90:
        grade = "A+ 🎉"
        message = "Outstanding! You're a maths genius!"
    elif score >= 80:
        grade = "A 🌟"
        message = "Excellent work! You've mastered this!"
    elif score >= 70:
        grade = "B 👍"
        message = "Great job! You're doing really well!"
    elif score >= 60:
        grade = "C 💪"
        message = "Good effort! Keep practicing!"
    elif score >= 50:
        grade = "D 📚"
        message = "Not bad! Try again to improve!"
    else:
        grade = "F 🎓"
        message = "Keep practicing! You'll get better!"

    result_text = f"FINAL SCORE: {score}/100\nGRADE: {grade}\n\n{message}\n\nPlay again?"

    if messagebox.askyesno("🎊 Quiz Complete!", result_text):
        show_frame(menu_frame)
    else:
        root.quit()

# === Frame Switching ===
def show_frame(frame):
    frame.tkraise()

# === Create Main Application ===
root = tk.Tk()
root.title("🎯 Maths Master - Quiz Game")
root.geometry("800x600")
root.resizable(False, False)

# Create frames
menu_frame = tk.Frame(root, bg="#2C3E50")  # Dark blue background
diff_frame = tk.Frame(root, bg="#34495E")  # Slightly lighter blue
quiz_frame = tk.Frame(root, bg=Difficulty.EASY.primary_color)

for f in (menu_frame, diff_frame, quiz_frame):
    f.place(relwidth=1, relheight=1)

# === Menu Frame ===
# Title
title_label_menu = tk.Label(menu_frame, text="🎯 MATHS MASTER", 
                           font=("Arial", 32, "bold"), 
                           bg="#2C3E50", fg="#FFD700")
title_label_menu.place(relx=0.5, rely=0.2, anchor="center")

subtitle_label = tk.Label(menu_frame, text="Test Your Arithmetic Skills!", 
                         font=("Arial", 16), 
                         bg="#2C3E50", fg="#ECF0F1")
subtitle_label.place(relx=0.5, rely=0.3, anchor="center")

# Start Button
start_btn = tk.Button(menu_frame, text="🚀 START QUIZ", 
                     font=("Arial", 18, "bold"),
                     bg="#27AE60", fg="white",
                     activebackground="#2ECC71",
                     relief="raised", bd=4,
                     cursor="hand2",
                     width=15, height=2,
                     command=lambda: show_frame(diff_frame))
start_btn.place(relx=0.5, rely=0.5, anchor="center")

# Quit Button
quit_btn = tk.Button(menu_frame, text="🚪 EXIT", 
                    font=("Arial", 14, "bold"),
                    bg="#E74C3C", fg="white",
                    activebackground="#C0392B",
                    relief="raised", bd=3,
                    cursor="hand2",
                    width=12, height=1,
                    command=root.quit)
quit_btn.place(relx=0.5, rely=0.75, anchor="center")

# === Difficulty Frame ===
# Title
diff_title = tk.Label(diff_frame, text="SELECT DIFFICULTY", 
                     font=("Arial", 28, "bold"), 
                     bg="#34495E", fg="#FFD700")
diff_title.place(relx=0.5, rely=0.15, anchor="center")

# Difficulty Buttons
difficulties = [
    ("🎯 EASY", "Single-digit numbers", Difficulty.EASY, "#27AE60"),
    ("🎯 MEDIUM", "Double-digit numbers", Difficulty.MEDIUM, "#F39C12"),
    ("🎯 HARD", "Three-digit numbers", Difficulty.HARD, "#E74C3C")
]

button_y = 0.35
for title, desc, diff, color in difficulties:
    btn_frame = tk.Frame(diff_frame, bg=color, relief="raised", bd=3)
    btn_frame.place(relx=0.5, rely=button_y, anchor="center", width=300, height=80)
    
    btn = tk.Button(btn_frame, text=f"{title}\n{desc}", 
                   font=("Arial", 12, "bold"),
                   bg=color, fg="white",
                   activebackground=color,
                   relief="flat",
                   cursor="hand2",
                   command=lambda d=diff: start_quiz_with_difficulty(d))
    btn.place(relwidth=1, relheight=1)
    
    button_y += 0.2

# Back Button
back_btn = tk.Button(diff_frame, text="🔙 BACK", 
                    font=("Arial", 14, "bold"),
                    bg="#95A5A6", fg="white",
                    activebackground="#7F8C8D",
                    relief="raised", bd=3,
                    cursor="hand2",
                    width=12, height=1,
                    command=lambda: show_frame(menu_frame))
back_btn.place(relx=0.5, rely=0.9, anchor="center")

# === Quiz Frame ===
# Back Button
quiz_back_btn = tk.Button(quiz_frame, text="🔙 BACK", 
                         font=("Arial", 12, "bold"),
                         bg="#95A5A6", fg="white",
                         activebackground="#7F8C8D",
                         relief="raised", bd=2,
                         cursor="hand2",
                         command=lambda: (stop_timer(), show_frame(diff_frame)))
quiz_back_btn.place(x=20, y=20)

# Title
title_label = tk.Label(quiz_frame, font=("Arial", 20, "bold"), 
                      fg="#FFD700", bg=Difficulty.EASY.primary_color)
title_label.place(relx=0.5, y=80, anchor="center")

# Timer
timer_label = tk.Label(quiz_frame, font=("Arial", 16, "bold"), 
                      bg=Difficulty.EASY.primary_color, fg="#FFA500")
timer_label.place(relx=0.5, y=140, anchor="center")

# Question
question_label = tk.Label(quiz_frame, font=("Arial", 24, "bold"), 
                         bg=Difficulty.EASY.primary_color, fg="#FFFFFF")
question_label.place(relx=0.5, y=200, anchor="center")

# Entry Frame
entry_frame = tk.Frame(quiz_frame, bg=Difficulty.EASY.secondary_color)
entry_frame.place(relx=0.5, y=280, anchor="center")

# Answer Entry
answer_entry = tk.Entry(entry_frame, font=("Arial", 20, "bold"), width=10,
                       bg=Difficulty.EASY.secondary_color, fg="#FFFFFF", 
                       insertbackground="#FFFFFF",
                       relief="solid", bd=4, justify="center")
answer_entry.pack(side="left", padx=10)
answer_entry.bind('<Return>', lambda e: check_answer())

# Submit Button
submit_btn = tk.Button(entry_frame, text="✓ SUBMIT", 
                      font=("Arial", 14, "bold"),
                      command=check_answer, 
                      bg=Difficulty.EASY.secondary_color, fg="#FFFFFF",
                      activebackground=Difficulty.EASY.primary_color,
                      relief="raised", bd=4,
                      cursor="hand2", padx=20)
submit_btn.pack(side="left", padx=10)

# Feedback
feedback_label = tk.Label(quiz_frame, font=("Arial", 16, "bold"), 
                         bg=Difficulty.EASY.primary_color, fg="#FFFFFF")
feedback_label.place(relx=0.5, y=350, anchor="center")

# Score
score_label = tk.Label(quiz_frame, font=("Arial", 16, "bold"), 
                      bg=Difficulty.EASY.primary_color, fg="#FFD700")
score_label.place(relx=0.5, y=400, anchor="center")

# === Start Application ===
show_frame(menu_frame)
root.mainloop()