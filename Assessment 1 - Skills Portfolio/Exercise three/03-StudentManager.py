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


def save_students(students: List[StudentRecord]) -> None:
    """Persist records back to the dataset file."""
    lines = [str(len(students))]
    for student in students:
        coursework = ",".join(map(str, student.coursework_marks))
        lines.append(
            f"{student.student_id},{student.name},{coursework},{student.exam_mark}"
        )

    DATA_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


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
        self.geometry("980x720")
        self.configure(bg="#101820")

        self.students = load_students()
        self.search_var = tk.StringVar()

        self._build_layout()
        self.show_message(
            "Select an option to explore student results.\n"
            "Dataset loaded: "
            f"{len(self.students)} students."
        )
        self.refresh_status("Ready")

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

        primary_buttons = [
            ("View All Records", self.show_all_records),
            ("View Individual Record", self.show_individual_prompt),
            ("Show Highest Score", lambda: self.show_extreme(highest=True)),
            ("Show Lowest Score", lambda: self.show_extreme(highest=False)),
        ]

        extension_buttons = [
            ("Sort Records", self.open_sort_dialog),
            ("Add Student", self.open_add_dialog),
            ("Delete Student", self.open_delete_dialog),
            ("Update Student", self.open_update_dialog),
        ]

        for idx, (text, handler) in enumerate(primary_buttons):
            btn = self._menu_button(menu_frame, text, handler)
            btn.grid(row=0, column=idx, padx=6, pady=5)

        for idx, (text, handler) in enumerate(extension_buttons):
            btn = self._menu_button(menu_frame, text, handler)
            btn.grid(row=1, column=idx, padx=6, pady=5)

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

        self.status_label = tk.Label(
            self,
            text="",
            font=("Segoe UI", 10),
            bg="#101820",
            fg="#B0BEC5",
        )
        self.status_label.pack(pady=(0, 10))

    def _menu_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 11, "bold"),
            width=20,
            bg="#1F4287",
            fg="#FFFFFF",
            activebackground="#278EA5",
            cursor="hand2",
            relief=tk.RAISED,
            bd=3,
        )

    def show_message(self, message: str) -> None:
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, message)
        self.output_text.config(state=tk.DISABLED)
        self.refresh_status("Display updated")

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

    def refresh_status(self, note: str) -> None:
        self.status_label.config(
            text=f"Dataset size: {len(self.students)} | {note}"
        )

    def persist_and_refresh(self, note: str) -> None:
        save_students(self.students)
        self.students = load_students()
        self.refresh_status(note)

    # === Extension Features ===
    def open_sort_dialog(self) -> None:
        if not self.students:
            messagebox.showinfo("No Data", "No student records available to sort.")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Sort Records")
        dialog.configure(bg="#101820")
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Choose sorting order for overall score:",
            font=("Segoe UI", 12, "bold"),
            bg="#101820",
            fg="#FEE715",
            pady=10,
        ).pack()

        tk.Button(
            dialog,
            text="Ascending (Lowest → Highest)",
            font=("Segoe UI", 11, "bold"),
            width=28,
            command=lambda: (self.sort_records(False), dialog.destroy()),
            bg="#1F4287",
            fg="white",
            pady=8,
        ).pack(pady=5)

        tk.Button(
            dialog,
            text="Descending (Highest → Lowest)",
            font=("Segoe UI", 11, "bold"),
            width=28,
            command=lambda: (self.sort_records(True), dialog.destroy()),
            bg="#1F4287",
            fg="white",
            pady=8,
        ).pack(pady=5)

    def sort_records(self, descending: bool) -> None:
        ordered = sorted(
            self.students, key=lambda s: s.overall_total, reverse=descending
        )
        order_text = "descending" if descending else "ascending"
        parts = [
            f"Records sorted in {order_text} order by total score.\n"
        ]
        for idx, student in enumerate(ordered, start=1):
            parts.append(f"Rank {idx}\n{format_record(student)}")
        self.show_message("\n".join(parts))

    def open_add_dialog(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Add Student")
        dialog.configure(bg="#101820")
        dialog.grab_set()

        fields = [
            ("Student ID", "id"),
            ("Full Name", "name"),
            ("Coursework 1", "cw1"),
            ("Coursework 2", "cw2"),
            ("Coursework 3", "cw3"),
            ("Exam Mark", "exam"),
        ]

        entries = {}
        for idx, (label, key) in enumerate(fields):
            tk.Label(
                dialog, text=label, bg="#101820", fg="#E0E0E0", font=("Segoe UI", 11)
            ).grid(row=idx, column=0, sticky="w", padx=10, pady=4)
            entry = tk.Entry(dialog, font=("Segoe UI", 11), width=25)
            entry.grid(row=idx, column=1, padx=10, pady=4)
            entries[key] = entry

        def submit():
            try:
                student_id = int(entries["id"].get())
                name = entries["name"].get().strip()
                coursework = [
                    int(entries["cw1"].get()),
                    int(entries["cw2"].get()),
                    int(entries["cw3"].get()),
                ]
                exam = int(entries["exam"].get())
            except ValueError:
                messagebox.showerror("Invalid Input", "All numeric fields must be valid integers.")
                return

            if not name:
                messagebox.showerror("Invalid Input", "Student name cannot be empty.")
                return

            if any(s.student_id == student_id for s in self.students):
                messagebox.showerror("Duplicate ID", "A student with this ID already exists.")
                return

            new_record = StudentRecord(
                student_id=student_id,
                name=name,
                coursework_marks=coursework,
                exam_mark=exam,
            )
            self.students.append(new_record)
            self.persist_and_refresh("Student added")
            self.show_message(f"New student added successfully.\n\n{format_record(new_record)}")
            dialog.destroy()

        tk.Button(
            dialog,
            text="Add Student",
            font=("Segoe UI", 11, "bold"),
            bg="#278EA5",
            fg="white",
            width=20,
            command=submit,
        ).grid(row=len(fields), column=0, columnspan=2, pady=12)

    def open_delete_dialog(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Delete Student")
        dialog.configure(bg="#101820")
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Enter student ID or name to delete:",
            font=("Segoe UI", 11),
            bg="#101820",
            fg="#E0E0E0",
        ).pack(padx=10, pady=8)

        entry = tk.Entry(dialog, font=("Segoe UI", 11), width=30)
        entry.pack(padx=10, pady=5)

        def delete_record():
            query = entry.get().strip()
            student = find_student(self.students, query)
            if not student:
                messagebox.showwarning("Not Found", "No matching student found.")
                return

            if not messagebox.askyesno(
                "Confirm Delete", f"Delete record for {student.name}?"
            ):
                return

            self.students = [s for s in self.students if s.student_id != student.student_id]
            self.persist_and_refresh("Student removed")
            self.show_message(f"Record removed:\n\n{format_record(student)}")
            dialog.destroy()

        tk.Button(
            dialog,
            text="Delete",
            font=("Segoe UI", 11, "bold"),
            bg="#B71C1C",
            fg="white",
            width=18,
            command=delete_record,
        ).pack(pady=10)

    def open_update_dialog(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Update Student")
        dialog.configure(bg="#101820")
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Enter student ID or name to update:",
            font=("Segoe UI", 11),
            bg="#101820",
            fg="#E0E0E0",
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=6)

        search_var = tk.StringVar()
        tk.Entry(dialog, textvariable=search_var, font=("Segoe UI", 11), width=30).grid(
            row=1, column=0, columnspan=2, padx=10, pady=4
        )

        fields = ["name", "cw1", "cw2", "cw3", "exam"]
        entry_widgets = {}

        def populate_fields(student: StudentRecord):
            entry_widgets["name"].delete(0, tk.END)
            entry_widgets["name"].insert(0, student.name)
            for idx in range(3):
                field = f"cw{idx+1}"
                entry_widgets[field].delete(0, tk.END)
                entry_widgets[field].insert(0, str(student.coursework_marks[idx]))
            entry_widgets["exam"].delete(0, tk.END)
            entry_widgets["exam"].insert(0, str(student.exam_mark))

        def load_student():
            student = find_student(self.students, search_var.get())
            if not student:
                messagebox.showwarning("Not Found", "Student not found.")
                return
            dialog.selected_student = student
            populate_fields(student)

        tk.Button(
            dialog,
            text="Load Student",
            font=("Segoe UI", 10, "bold"),
            bg="#278EA5",
            fg="white",
            command=load_student,
        ).grid(row=2, column=0, columnspan=2, pady=6)

        labels = [
            ("Full Name", "name"),
            ("Coursework 1", "cw1"),
            ("Coursework 2", "cw2"),
            ("Coursework 3", "cw3"),
            ("Exam Mark", "exam"),
        ]

        for idx, (label, key) in enumerate(labels, start=3):
            tk.Label(
                dialog, text=label, bg="#101820", fg="#E0E0E0", font=("Segoe UI", 11)
            ).grid(row=idx, column=0, sticky="w", padx=10, pady=4)
            entry = tk.Entry(dialog, font=("Segoe UI", 11), width=25)
            entry.grid(row=idx, column=1, padx=10, pady=4)
            entry_widgets[key] = entry

        dialog.selected_student = None

        def save_updates():
            student = getattr(dialog, "selected_student", None)
            if student is None:
                messagebox.showinfo("Load Required", "Load a student before saving.")
                return
            try:
                new_name = entry_widgets["name"].get().strip()
                coursework = [
                    int(entry_widgets["cw1"].get()),
                    int(entry_widgets["cw2"].get()),
                    int(entry_widgets["cw3"].get()),
                ]
                exam = int(entry_widgets["exam"].get())
            except ValueError:
                messagebox.showerror("Invalid Input", "Marks must be valid integers.")
                return
            if not new_name:
                messagebox.showerror("Invalid Input", "Name cannot be empty.")
                return

            student.name = new_name
            student.coursework_marks = coursework
            student.exam_mark = exam
            self.persist_and_refresh("Student updated")
            self.show_message(f"Record updated successfully.\n\n{format_record(student)}")
            dialog.destroy()

        tk.Button(
            dialog,
            text="Save Changes",
            font=("Segoe UI", 11, "bold"),
            bg="#00A86B",
            fg="white",
            width=20,
            command=save_updates,
        ).grid(row=len(labels) + 3, column=0, columnspan=2, pady=12)


if __name__ == "__main__":
    app = StudentManagerApp()
    app.mainloop()

