import tkinter as tk
import customtkinter as ttk
import subprocess
from PIL import Image, ImageTk
import pygame
import threading


pygame.mixer.init()

def play_sound_lobby():
    pygame.mixer.music.load("sound_lobby.mp3") 
    pygame.mixer.music.set_volume(0.5) 
    pygame.mixer.music.play(loops=-1, start=0.0)  

def play_sound_click():
    sound_click_on = pygame.mixer.Sound("sound_click.mp3")  
    sound_click_on.set_volume(0.5)  
    sound_click_on.play()
# Start background music
play_sound_lobby()

ui = tk.Tk()
ui.title("BLOX-BATTLE by: IT-2A")
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


ui.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

ui.config(bg="black")


def start():
    play_sound_click()
    pygame.mixer.music.stop()
    def count_down(ui):
        def update_label(value):
            if value > 0:
                play_sound_click()
                count.config(text=str(value))
                ui.after(1000, update_label, value - 1)
            else:
                play_sound_click()
                threading.Thread(target=lambda: subprocess.run(["python", "start_game.py"])).start()
                ui.destroy()
        count = tk.Label(canvas_bg, text="3", font=("Terminal", 60),bg=canvas_bg.cget("bg"),fg="white")
        count.place(x=610,y=40)
        play_sound_click()
        update_label(3)
    count_down(ui)

    
lobby_image = Image.open("lobby.png")  # Ensure your image is in the same directory or give the full path
lobby_photo = ImageTk.PhotoImage(lobby_image)

canvas_bg = tk.Canvas(ui, bg="black")
canvas_bg.pack(fill="both", expand=True)

canvas_bg.create_image(0, 0, image=lobby_photo, anchor="nw")

# Button with custom styling
start_btn = ttk.CTkButton(
    canvas_bg,
    text="START",
    command=start,
    height=100,
    width=300,
    font=("Terminal", 100),
    fg_color="#f56263",  # Corrected background color for customtkinter button
    hover_color="#e2c421"  # Color change on hover
)

start_btn.place(x=498, y=330)

ui.mainloop()
