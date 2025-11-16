import tkinter as tk
from tkinter import messagebox
import random

class MathsQuiz:
    def __init__(self, root):
        self.root = root
        self.root.title("Maths Quiz")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Quiz variables
        self.difficulty = None
        self.score = 0
        self.current_question = 0
        self.total_questions = 10
        self.attempts = 0
        self.num1 = 0
        self.num2 = 0
        self.operation = ''
        self.correct_answer = 0
        
        # Create main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Start with the menu
        self.displayMenu()
    
    def displayMenu(self):
        """Display the difficulty level menu"""
        # Clear the frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Title
        title_label = tk.Label(self.main_frame, text="DIFFICULTY LEVEL", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Difficulty options
        easy_button = tk.Button(self.main_frame, text="1. Easy", 
                               font=("Arial", 12), width=20,
                               command=lambda: self.startQuiz("easy"))
        easy_button.pack(pady=10)
        
        moderate_button = tk.Button(self.main_frame, text="2. Moderate", 
                                   font=("Arial", 12), width=20,
                                   command=lambda: self.startQuiz("moderate"))
        moderate_button.pack(pady=10)
        
        advanced_button = tk.Button(self.main_frame, text="3. Advanced", 
                                   font=("Arial", 12), width=20,
                                   command=lambda: self.startQuiz("advanced"))
        advanced_button.pack(pady=10)
    
    def startQuiz(self, difficulty):
        """Start the quiz with the selected difficulty"""
        self.difficulty = difficulty
        self.score = 0
        self.current_question = 0
        self.attempts = 0
        
        # Generate first question
        self.generateQuestion()
        self.displayProblem()
    
    def randomInt(self):
        """Generate random numbers based on difficulty level"""
        if self.difficulty == "easy":
            return random.randint(0, 9)
        elif self.difficulty == "moderate":
            return random.randint(10, 99)
        else:  # advanced
            return random.randint(1000, 9999)
    
    def decideOperation(self):
        """Randomly decide whether to use addition or subtraction"""
        return random.choice(['+', '-'])
    
    def generateQuestion(self):
        """Generate a new question"""
        self.num1 = self.randomInt()
        self.num2 = self.randomInt()
        self.operation = self.decideOperation()
        
        # Ensure subtraction doesn't result in negative numbers for easier levels
        if self.operation == '-' and self.num1 < self.num2:
            self.num1, self.num2 = self.num2, self.num1
        
        # Calculate correct answer
        if self.operation == '+':
            self.correct_answer = self.num1 + self.num2
        else:
            self.correct_answer = self.num1 - self.num2
    
    def displayProblem(self):
        """Display the current problem"""
        # Clear the frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Display question number and score
        info_text = f"Question {self.current_question + 1}/{self.total_questions} | Score: {self.score}"
        info_label = tk.Label(self.main_frame, text=info_text, font=("Arial", 12))
        info_label.pack(pady=10)
        
        # Display the problem
        problem_text = f"{self.num1} {self.operation} {self.num2} = "
        problem_label = tk.Label(self.main_frame, text=problem_text, font=("Arial", 16, "bold"))
        problem_label.pack(pady=20)
        
        # Entry for answer
        self.answer_entry = tk.Entry(self.main_frame, font=("Arial", 14), width=10)
        self.answer_entry.pack(pady=10)
        self.answer_entry.focus()
        
        # Submit button
        submit_button = tk.Button(self.main_frame, text="Submit Answer", 
                                 font=("Arial", 12), command=self.checkAnswer)
        submit_button.pack(pady=10)
        
        # Bind Enter key to submit
        self.root.bind('<Return>', lambda event: self.checkAnswer())
    
    def checkAnswer(self):
        """Check if the user's answer is correct"""
        try:
            user_answer = int(self.answer_entry.get())
            self.attempts += 1
            
            if user_answer == self.correct_answer:
                if self.attempts == 1:
                    self.score += 10
                    messagebox.showinfo("Correct!", "Well done! +10 points")
                else:
                    self.score += 5
                    messagebox.showinfo("Correct!", "Good job! +5 points")
                
                self.nextQuestion()
            else:
                if self.attempts < 2:
                    messagebox.showerror("Incorrect", "Try again!")
                    self.answer_entry.delete(0, tk.END)
                    self.answer_entry.focus()
                else:
                    messagebox.showerror("Incorrect", 
                                        f"Wrong! The correct answer is {self.correct_answer}")
                    self.nextQuestion()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number!")
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.focus()
    
    def nextQuestion(self):
        """Move to the next question or end the quiz"""
        self.current_question += 1
        self.attempts = 0
        
        if self.current_question < self.total_questions:
            self.generateQuestion()
            self.displayProblem()
        else:
            self.displayResults()
    
    def displayResults(self):
        """Display the final results"""
        # Clear the frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Unbind Enter key
        self.root.unbind('<Return>')
        
        # Display final score
        score_text = f"Your final score: {self.score}/100"
        score_label = tk.Label(self.main_frame, text=score_text, font=("Arial", 16, "bold"))
        score_label.pack(pady=20)
        
        # Determine grade
        grade = self.calculateGrade()
        grade_label = tk.Label(self.main_frame, text=f"Grade: {grade}", 
                              font=("Arial", 14))
        grade_label.pack(pady=10)
        
        # Play again button
        play_again_button = tk.Button(self.main_frame, text="Play Again", 
                                     font=("Arial", 12), command=self.displayMenu)
        play_again_button.pack(pady=20)
    
    def calculateGrade(self):
        """Calculate the grade based on score"""
        if self.score >= 90:
            return "A+"
        elif self.score >= 80:
            return "A"
        elif self.score >= 70:
            return "B"
        elif self.score >= 60:
            return "C"
        elif self.score >= 50:
            return "D"
        else:
            return "F"

# Create the main window and run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = MathsQuiz(root)
    root.mainloop()