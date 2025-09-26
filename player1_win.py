import tkinter as tk
import customtkinter as ttk
import subprocess
from PIL import Image, ImageTk
import pygame
import threading
import time

# Initialize pygame mixer
pygame.mixer.init()

def play_win():
    pygame.mixer.music.load("win.mp3")  # Replace with your music file path
    pygame.mixer.music.set_volume(0.5)  # Adjust volume (0.0 to 1.0)
    pygame.mixer.music.play(loops=1, start=0.0)  # Loops indefinitely

def play_sound_click():
    sound_click_on = pygame.mixer.Sound("sound_click.mp3")  # Replace with your sound file path (use .wav for better compatibility)
    sound_click_on.set_volume(0.5)  # Adjust volume (0.0 to 1.0)
    sound_click_on.play()

# Start background music
play_win()

ui = tk.Tk()
ui.title("Tetris")
ui.resizable(False, False)
ui.geometry("1300x759")  # Set the window size

# Center the window on the screen
screen_width = ui.winfo_screenwidth()
screen_height = ui.winfo_screenheight()
window_width = 1300
window_height = 759

# Calculate position for centering
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2

# Apply geometry with position and size
ui.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

ui.config(bg="black")

def start():
    play_sound_click()
    threading.Thread(target=lambda: subprocess.run(["python", "lobby.py"])).start()
    ui.destroy()

lobby_image = Image.open("p1_win.png")  # Ensure your image is in the same directory or give the full path
lobby_photo = ImageTk.PhotoImage(lobby_image)

canvas_bg = tk.Canvas(ui, bg="black")
canvas_bg.pack(fill="both", expand=True)

canvas_bg.create_image(0, 0, image=lobby_photo, anchor="nw")

# Button with custom styling
again_btn = ttk.CTkButton(
    canvas_bg,
    text=" BACK TO LOBBY ",
    command=start,
    height=100,
    width=300,
    font=("Terminal", 100),
    fg_color="#f56263",  # Corrected background color for customtkinter button
    hover_color="#e2c421"  # Color change on hover
)

again_btn.place(x=260, y=600)

ui.mainloop()
