import random
import threading
import tkinter as tk
from pathlib import Path

try:
    import pyttsx3  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    pyttsx3 = None


BASE_DIR = Path(__file__).resolve().parent.parent
JOKES_PATH = BASE_DIR / "A1 - Resources" / "randomJokes.txt"


def load_jokes():
    """Load jokes as (setup, punchline) tuples."""
    jokes = []
    try:
        with JOKES_PATH.open(encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or "?" not in line:
                    continue
                setup, punchline = line.split("?", 1)
                setup = setup.strip()
                punchline = punchline.strip()
                if setup and punchline:
                    jokes.append((setup + "?", punchline))
    except FileNotFoundError:
        pass
    return jokes


class JokeAssistant(tk.Tk):
    """Simple Tkinter app that emulates a joke-telling assistant."""

    def __init__(self):
        super().__init__()
        self.title("Alexa - Tell me a Joke")
        self.geometry("640x420")
        self.configure(bg="#0A1F33")

        self.jokes = load_jokes()
        self.current_joke = None
        self.voice_supported = False
        self.voice_ready = False
        self.voice_rate = 170
        self.voice_message = ""

        self._init_voice()

        self._build_ui()

    def _init_voice(self):
        """Prepare text-to-speech engine if pyttsx3 is available."""
        if pyttsx3 is None:
            self.voice_message = "Install pyttsx3 for voice playback."
            return

        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", self.voice_rate)
            engine.stop()
            self.voice_supported = True
            self.voice_ready = True
            self.voice_message = "Voice assistant ready."
        except Exception:
            self.voice_supported = False
            self.voice_ready = False
            self.voice_message = "Voice unavailable (initialisation failed)."

    def _build_ui(self):
        header = tk.Label(
            self,
            text="Need a laugh? Ask Alexa!",
            font=("Segoe UI", 22, "bold"),
            bg="#0A1F33",
            fg="#4FC3F7",
        )
        header.pack(pady=(25, 10))

        self.setup_label = tk.Label(
            self,
            text="Tap the button to hear a joke.",
            font=("Segoe UI", 16, "bold"),
            wraplength=520,
            justify="center",
            bg="#0A1F33",
            fg="#FFFFFF",
            pady=20,
        )
        self.setup_label.pack(pady=(5, 5))

        self.punchline_label = tk.Label(
            self,
            text="",
            font=("Segoe UI", 15),
            wraplength=520,
            justify="center",
            bg="#0A1F33",
            fg="#FFEB3B",
        )
        self.punchline_label.pack(pady=(0, 20))

        button_frame = tk.Frame(self, bg="#0A1F33")
        button_frame.pack(pady=10)

        main_btn = tk.Button(
            button_frame,
            text="Alexa, tell me a Joke",
            font=("Segoe UI", 12, "bold"),
            width=20,
            bg="#1E88E5",
            fg="white",
            activebackground="#1565C0",
            cursor="hand2",
            command=self.deliver_joke,
        )
        main_btn.grid(row=0, column=0, padx=10, pady=5)

        self.punchline_btn = tk.Button(
            button_frame,
            text="Show Punchline",
            font=("Segoe UI", 12, "bold"),
            width=20,
            bg="#F4511E",
            fg="white",
            activebackground="#D84315",
            cursor="hand2",
            state=tk.DISABLED,
            command=self.reveal_punchline,
        )
        self.punchline_btn.grid(row=0, column=1, padx=10, pady=5)

        next_btn = tk.Button(
            button_frame,
            text="Next Joke",
            font=("Segoe UI", 12, "bold"),
            width=20,
            bg="#43A047",
            fg="white",
            activebackground="#2E7D32",
            cursor="hand2",
            command=self.deliver_joke,
        )
        next_btn.grid(row=1, column=0, padx=10, pady=5)

        quit_btn = tk.Button(
            button_frame,
            text="Quit",
            font=("Segoe UI", 12, "bold"),
            width=20,
            bg="#B71C1C",
            fg="white",
            activebackground="#8E0000",
            cursor="hand2",
            command=self.destroy,
        )
        quit_btn.grid(row=1, column=1, padx=10, pady=5)

        self.status_label = tk.Label(
            self,
            text=self._status_text(),
            font=("Segoe UI", 10),
            bg="#0A1F33",
            fg="#B0BEC5",
        )
        self.status_label.pack(pady=(10, 0))

    def _status_text(self):
        jokes_text = (
            f"Loaded {len(self.jokes)} jokes." if self.jokes else "No jokes available."
        )
        return f"{jokes_text} {self.voice_message}"

    def deliver_joke(self):
        if not self.jokes:
            self.setup_label.config(text="Oops! I couldn't find any jokes.")
            self.punchline_label.config(text="")
            self.punchline_btn.config(state=tk.DISABLED)
            return

        self.current_joke = random.choice(self.jokes)
        setup, _ = self.current_joke
        self.setup_label.config(text=setup)
        self.punchline_label.config(text="(Tap 'Show Punchline' to reveal)")
        self.punchline_btn.config(state=tk.NORMAL)
        self.speak_text(setup)

    def reveal_punchline(self):
        if self.current_joke:
            _, punchline = self.current_joke
            self.punchline_label.config(text=punchline)
            self.punchline_btn.config(state=tk.DISABLED)
            self.speak_text(punchline)

    def speak_text(self, text):
        """Speak text asynchronously if voice support is available."""
        if not self.voice_supported or not text:
            return

        def _worker(message, rate):
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", rate)
                engine.say(message)
                engine.runAndWait()
                engine.stop()
            except Exception:
                pass

        threading.Thread(
            target=_worker, args=(text, self.voice_rate), daemon=True
        ).start()


if __name__ == "__main__":
    app = JokeAssistant()
    app.mainloop()

