from PIL import Image, ImageTk, ImageSequence
import tkinter as tk

from config.settings import *

class AnimationManager:
    _active_animations = []

    def __init__(self, display_label, animation_path, width, height):
        self.display = display_label
        self.animation_frames = []
        self.current_frame_index = 0
        self.animation_task = None
        self.is_playing = False

        # Load animation frames
        try:
            animation = Image.open(animation_path)
            for frame in ImageSequence.Iterator(animation):
                adjusted_frame = frame.copy().resize((width, height), Image.LANCZOS)
                self.animation_frames.append(ImageTk.PhotoImage(adjusted_frame))
        except Exception as e:
            print(f"Error loading animation: {e}")
            # Create a fallback colored frame
            fallback_image = Image.new('RGB', (width, height), color='lightblue')
            self.animation_frames.append(ImageTk.PhotoImage(fallback_image))

        AnimationManager._active_animations.append(self)

    def start_animation(self):
        """Start the animation from the beginning"""
        self.stop_animation()
        self.current_frame_index = 0
        self.is_playing = True
        self.animate_sequence()

    def play(self):
        """Alias for start_animation - fixes the AttributeError"""
        self.start_animation()

    def animate_sequence(self):
        """Continue animating frames"""
        if self.is_playing and self.animation_frames:
            self.display.config(image=self.animation_frames[self.current_frame_index])
            self.display.image = self.animation_frames[self.current_frame_index]
            self.current_frame_index = (self.current_frame_index + 1) % len(self.animation_frames)
            self.animation_task = self.display.after(45, self.animate_sequence)

    def pause(self):
        """Pause the animation"""
        self.is_playing = False
        self.stop_animation()

    def resume(self):
        """Resume the animation from current frame"""
        if not self.is_playing:
            self.is_playing = True
            self.animate_sequence()

    def stop_animation(self):
        """Stop the animation completely"""
        self.is_playing = False
        if self.animation_task:
            self.display.after_cancel(self.animation_task)
            self.animation_task = None

    def set_frame_rate(self, delay_ms):
        """Change animation speed"""
        self.stop_animation()
        if self.is_playing:
            self.animation_task = self.display.after(delay_ms, self.animate_sequence)

    def get_frame_count(self):
        """Get total number of frames"""
        return len(self.animation_frames)

    def get_current_frame(self):
        """Get current frame number"""
        return self.current_frame_index

    def goto_frame(self, frame_index):
        """Jump to specific frame"""
        if 0 <= frame_index < len(self.animation_frames):
            self.current_frame_index = frame_index
            if self.is_playing:
                self.display.config(image=self.animation_frames[self.current_frame_index])
                self.display.image = self.animation_frames[self.current_frame_index]

    @classmethod
    def stop_all_animations(cls):
        """Stop all active animations"""
        for anim in cls._active_animations:
            anim.stop_animation()

    @classmethod
    def pause_all_animations(cls):
        """Pause all active animations"""
        for anim in cls._active_animations:
            anim.pause()

    @classmethod
    def resume_all_animations(cls):
        """Resume all paused animations"""
        for anim in cls._active_animations:
            if anim.animation_frames:
                anim.resume()


class ScreenManager:
    _screen_cache = {}

    def __init__(self, parent_screen, game_level):
        self.background = tk.Label(parent_screen)
        self.background.place(x=0, y=0, relwidth=1, relheight=1)
        self.screen_color = game_level.theme_color
        self.animation = AnimationManager(
            self.background, 
            game_level.background_path, 
            APP_WIDTH, 
            APP_HEIGHT
        )
        # Start animation immediately
        self.animation.play()

    @classmethod
    def get_screen_background(cls, parent_screen, game_level):
        """Get or create screen background with caching"""
        if game_level not in cls._screen_cache:
            cls._screen_cache[game_level] = cls(parent_screen, game_level)
        return cls._screen_cache[game_level]

    def play_background(self):
        """Start background animation"""
        self.animation.play()

    def stop_background(self):
        """Stop background animation"""
        self.animation.stop_animation()

    def pause_background(self):
        """Pause background animation"""
        self.animation.pause()

    def activate(self):
        """Activate this screen"""
        self.background.tkraise()
        self.play_background()

    def set_background_color(self, color):
        """Set fallback background color"""
        self.background.config(bg=color)
        self.screen_color = color

    def destroy(self):
        """Clean up resources"""
        self.animation.stop_animation()
        self.background.destroy()