from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import tkinter as tk
from tkinter import ttk, messagebox


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "A1 - Resources" / "studentMarks.txt"


@dataclass
class StudentRecord:
    student_id: int
    name: str
    coursework_marks: List[int]
    exam_mark: int

    @property
    def coursework_total(self) -> int:
        return sum(self.coursework_marks)

    @property
    def overall_total(self) -> int:
        return self.coursework_total + self.exam_mark

    @property
    def percentage(self) -> float:
        return (self.overall_total / 160) * 100

    @property
    def grade(self) -> str:
        pct = self.percentage
        if pct >= 70:
            return "A"
        if pct >= 60:
            return "B"
        if pct >= 50:
            return "C"
        if pct >= 40:
            return "D"
        return "F"


def load_students() -> List[StudentRecord]:
    """Load student records from the dataset."""
    students: List[StudentRecord] = []
    try:
        with DATA_PATH.open(encoding="utf-8") as dataset:
            lines = [line.strip() for line in dataset.readlines() if line.strip()]
    except FileNotFoundError:
        return students

    if not lines:
        return students

    for row in lines[1:]:
        parts = [part.strip() for part in row.split(",")]
        if len(parts) != 6:
            continue
        try:
            student_id = int(parts[0])
            name = parts[1]
            coursework = list(map(int, parts[2:5]))
            exam = int(parts[5])
        except ValueError:
            continue

        students.append(
            StudentRecord(
                student_id=student_id,
                name=name,
                coursework_marks=coursework,
                exam_mark=exam,
            )
        )

    return students


def format_record(record: StudentRecord) -> str:
    """Return a nicely structured textual representation."""
    return (
        f"Name: {record.name}\n"
        f"ID: {record.student_id}\n"
        f"Coursework Total: {record.coursework_total}/60\n"
        f"Exam Mark: {record.exam_mark}/100\n"
        f"Overall: {record.overall_total}/160 ({record.percentage:.1f}%)\n"
        f"Grade: {record.grade}\n"
    )


def class_summary(students: List[StudentRecord]) -> str:
    if not students:
        return "No student data available."
    average = sum(student.percentage for student in students) / len(students)
    return (
        f"Class size: {len(students)}\n"
        f"Average percentage: {average:.2f}%"
    )


def find_student(students: List[StudentRecord], query: str) -> Optional[StudentRecord]:
    """Find a student either by numerical id or name substring."""
    query = query.strip().lower()
    if not query:
        return None

    for student in students:
        if query.isdigit() and int(query) == student.student_id:
            return student
        if query in student.name.lower():
            return student

    return None


class StudentManagerApp(tk.Tk):
    """Tkinter GUI that exposes student statistics."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Student Manager - Exercise 3")
        self.geometry("900x640")
        self.configure(bg="#101820")

        self.students = load_students()
        self.search_var = tk.StringVar()

        self._build_layout()
        self.show_message(
            "Select an option to explore student results.\n"
            "Dataset loaded: "
            f"{len(self.students)} students."
        )

    def _build_layout(self) -> None:
        header = tk.Label(
            self,
            text="Student Performance Console",
            font=("Segoe UI", 24, "bold"),
            bg="#101820",
            fg="#FEE715",
        )
        header.pack(pady=(20, 10))

        menu_frame = tk.Frame(self, bg="#101820")
        menu_frame.pack(pady=10)

        button_specs = [
            ("View All Records", self.show_all_records),
            ("View Individual Record", self.show_individual_prompt),
            ("Show Highest Score", lambda: self.show_extreme(highest=True)),
            ("Show Lowest Score", lambda: self.show_extreme(highest=False)),
        ]

        for idx, (text, handler) in enumerate(button_specs):
            btn = tk.Button(
                menu_frame,
                text=text,
                command=handler,
                font=("Segoe UI", 12, "bold"),
                width=22,
                bg="#1F4287",
                fg="#FFFFFF",
                activebackground="#278EA5",
                cursor="hand2",
                relief=tk.RAISED,
                bd=3,
            )
            btn.grid(row=0, column=idx, padx=8, pady=5)

        search_frame = tk.Frame(self, bg="#101820")
        search_frame.pack(pady=(5, 10))

        tk.Label(
            search_frame,
            text="Student name or ID:",
            font=("Segoe UI", 12),
            bg="#101820",
            fg="#E0E0E0",
        ).pack(side=tk.LEFT, padx=(0, 8))

        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 12),
            width=30,
        )
        search_entry.pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            search_frame,
            text="Find",
            font=("Segoe UI", 12),
            command=self.show_individual_prompt,
            bg="#278EA5",
            fg="white",
            relief=tk.RAISED,
            bd=3,
            cursor="hand2",
        ).pack(side=tk.LEFT)

        self.output_text = tk.Text(
            self,
            font=("Consolas", 12),
            bg="#0D1B2A",
            fg="#E0E0E0",
            wrap="word",
            relief=tk.FLAT,
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=30, pady=(5, 20))

        scrollbar = ttk.Scrollbar(self.output_text, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def show_message(self, message: str) -> None:
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, message)
        self.output_text.config(state=tk.DISABLED)

    def show_all_records(self) -> None:
        if not self.students:
            self.show_message("No records to display.")
            return

        parts = []
        for idx, student in enumerate(self.students, start=1):
            parts.append(f"--- Student {idx} ---\n{format_record(student)}")

        parts.append("\n" + class_summary(self.students))
        self.show_message("\n".join(parts))

    def show_individual_prompt(self) -> None:
        query = self.search_var.get().strip()
        if not query:
            messagebox.showinfo(
                "Search Required", "Enter a student name or ID to view a record."
            )
            return

        student = find_student(self.students, query)
        if not student:
            messagebox.showwarning(
                "Not Found", f"No student matched '{query}'. Try ID or full name."
            )
            return

        result = format_record(student)
        self.show_message(result)

    def show_extreme(self, *, highest: bool) -> None:
        if not self.students:
            self.show_message("No student data available.")
            return

        target = max(self.students, key=lambda s: s.overall_total) if highest else min(
            self.students, key=lambda s: s.overall_total
        )
        title = "Highest Overall Score" if highest else "Lowest Overall Score"
        self.show_message(f"{title}\n\n{format_record(target)}")


if __name__ == "__main__":
    app = StudentManagerApp()
    app.mainloop()

