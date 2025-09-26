import tkinter as tk
import random
import time
import pygame
from PIL import Image, ImageTk
import subprocess
import threading
import customtkinter as ttk


pygame.mixer.init()

def play_background_music():
    pygame.mixer.music.load("tetris-theme.mp3") 
    pygame.mixer.music.set_volume(0.5)  
    pygame.mixer.music.play(loops=-1, start=0.0)  

def play_block_placed():
    block_placed_sound = pygame.mixer.Sound("block_placed.mp3") 
    block_placed_sound.set_volume(0.5) 
    block_placed_sound.play()  

def play_KO_sound():
    KO_sound = (pygame.mixer.Sound("KO.mp3"))
    KO_sound.set_volume(1.0) 
    KO_sound.play()

def play_sound_click():
    sound_click_on = pygame.mixer.Sound("sound_click.mp3")  # Replace with your sound file path (use .wav for better compatibility)
    sound_click_on.set_volume(0.5)  # Adjust volume (0.0 to 1.0)
    sound_click_on.play()

def play_block_explode():
    block_explode_sound = pygame.mixer.Sound("block_explode.mp3")  # Replace with your sound file path
    block_explode_sound.set_volume(0.5)  # Adjust volume (0.0 to 1.0)
    block_explode_sound.play()

play_background_music()


SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30 
BLACK = "#000000"
PENALTY_COLOR = "#FFFF00" 
COLOR_PASS = "#0FF0F00"

textures = {
    "#584366": Image.open("redstone.png").resize((BLOCK_SIZE, BLOCK_SIZE)),  
    "#7d6191": Image.open("iron.png").resize((BLOCK_SIZE, BLOCK_SIZE)), 
    "#807a6a": Image.open("gold.png").resize((BLOCK_SIZE, BLOCK_SIZE)),  
    "#fcba03": Image.open("diamond.png").resize((BLOCK_SIZE, BLOCK_SIZE)),
    "#FFF0FF": Image.open('emerald.png').resize((BLOCK_SIZE,BLOCK_SIZE)),
    "#FFF00F": Image.open('nether.png').resize((BLOCK_SIZE,BLOCK_SIZE)),
    "#000FFF": Image.open('copper.png').resize((BLOCK_SIZE,BLOCK_SIZE)),
    COLOR_PASS: Image.open('grass.png').resize((BLOCK_SIZE,BLOCK_SIZE)),
    PENALTY_COLOR: Image.open("bedrock.png").resize((BLOCK_SIZE, BLOCK_SIZE))  
}


# Resize textures to block size
for color, texture in textures.items():
    textures[color] = texture.resize((BLOCK_SIZE, BLOCK_SIZE))


# Shapes (Tetris pieces)
SHAPES = [
    [[1, 1, 1],  # T-shape
     [0, 1, 0]],

    [[1, 1],  # Square
     [1, 1]],

     [[1,0,0], # L-shape
      [1,1,1]],

     [[0,0,1], # Reverse L-shape
      [1,1,1]],

    [[1, 1, 0],   # Z-shape
     [0, 1, 1]],

    [[0, 1, 1],  # S-shapes
     [1, 1, 0]],

    [[1, 1, 1, 1]] # I-shape
]

color_choices = list(textures.keys())[:-1] 

# Initialize Game Variables for Player 1
shape1 = random.choice(SHAPES)
color1 = random.choice(color_choices) 
if color == PENALTY_COLOR:
    color1 == COLOR_PASS
x1, y1 = SCREEN_WIDTH // 2 - (len(shape1[0]) // 2) * BLOCK_SIZE, 0
fall_speed1 = 500
last_fall_time1 = time.time() * 1000
game_over1 = False
score1 = 0
level1 = 1
grid1 = [[BLACK for _ in range(SCREEN_WIDTH // BLOCK_SIZE)] for _ in range(SCREEN_HEIGHT // BLOCK_SIZE)]

# Initialize Game Variables for Player 2
shape2 = random.choice(SHAPES)
color2 = random.choice(color_choices) 
if color2 == PENALTY_COLOR:
    color2 = COLOR_PASS
x2, y2 = SCREEN_WIDTH // 2 - (len(shape2[0]) // 2) * BLOCK_SIZE, 0
fall_speed2 = 500
last_fall_time2 = time.time() * 1000
game_over2 = False
score2 = 0
level2 = 1
grid2 = [[BLACK for _ in range(SCREEN_WIDTH // BLOCK_SIZE)] for _ in range(SCREEN_HEIGHT // BLOCK_SIZE)]

 

# Common functions for both players
def draw_grid(canvas):
    """Draws the grid lines on the screen."""
    for x_pos in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        canvas.create_line(x_pos, 0, x_pos, SCREEN_HEIGHT, fill=BLACK)
    for y_pos in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
        canvas.create_line(0, y_pos, SCREEN_WIDTH, y_pos, fill=BLACK)

def draw_shape(canvas, shape, x, y, color):
    """Draws the current Tetris piece with texture."""
    if "textures" not in canvas.__dict__:
        canvas.textures = {}  # Initialize the texture storage
    texture = textures.get(color)  # Get the corresponding texture for the color
    if texture:
        if color not in canvas.textures:
            canvas.textures[color] = ImageTk.PhotoImage(texture)  # Store PhotoImage reference
        tk_texture = canvas.textures[color]
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    canvas.create_image(
                        x + j * BLOCK_SIZE, y + i * BLOCK_SIZE,
                        image=tk_texture,
                        anchor="nw"
                    )

def draw_locked_blocks(canvas, grid):
    """Draw all the locked blocks, including penalty blocks (bedrock)."""
    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            if cell != BLACK:  # Don't draw empty cells
                if cell == PENALTY_COLOR:  # This is where the penalty color logic happens
                    # Cache the penalty texture if not already cached
                    if "penalty_texture" not in canvas.__dict__:
                        canvas.penalty_texture = ImageTk.PhotoImage(textures["#FFFF00"])  # Use bedrock texture

                    # Use the cached penalty texture for drawing
                    tk_texture = canvas.penalty_texture
                    canvas.create_image(
                        j * BLOCK_SIZE, i * BLOCK_SIZE,
                        image=tk_texture,
                        anchor="nw"
                    )
                else:
                    # Draw other blocks (for normal blocks)
                    tk_texture = ImageTk.PhotoImage(textures[cell])  # Assuming block_texture is loaded elsewhere
                    canvas.create_image(
                        j * BLOCK_SIZE, i * BLOCK_SIZE,
                        image=tk_texture,
                        anchor="nw"
                    )

def is_valid_position(shape, x, y, grid):
    """Checks if the current position of the shape is valid."""
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                new_x = (x // BLOCK_SIZE) + j
                new_y = (y // BLOCK_SIZE) + i
                if new_x < 0 or new_x >= SCREEN_WIDTH // BLOCK_SIZE or new_y >= SCREEN_HEIGHT // BLOCK_SIZE:
                    return False
                if new_y >= 0 and grid[new_y][new_x] != BLACK:
                    return False
    return True

def lock_shape(shape, x, y, color, grid):
    play_block_placed()
    for row_index, row in enumerate(shape):
        for col_index, cell in enumerate(row):
            if cell:
                grid_row = (y + row_index * BLOCK_SIZE) // BLOCK_SIZE
                grid_col = (x + col_index * BLOCK_SIZE) // BLOCK_SIZE
                if 0 <= grid_row < len(grid) and 0 <= grid_col < len(grid[0]):
                    grid[grid_row][grid_col] = color  # Save the color or texture key

def clear_rows(grid, opponent_grid):
    new_grid = [row for row in grid if any(cell == BLACK for cell in row)]  # Keep non-full rows
    cleared_rows = len(grid) - len(new_grid)  # Number of cleared rows

    if cleared_rows > 0:
        grid[:] = [[BLACK for _ in range(SCREEN_WIDTH // BLOCK_SIZE)] for _ in range(cleared_rows)] + new_grid
        play_block_explode()
        for _ in range(cleared_rows):
            add_garbage_row(opponent_grid)
            
    return cleared_rows

def drop_to_bottom(shape, x, y, grid):
    """Drops the piece to the lowest valid position."""
    while is_valid_position(shape, x, y + BLOCK_SIZE, grid):
        y += BLOCK_SIZE
    return y

def draw_drop_indicator(canvas, shape, x, y, grid, color):
    """Draws a drop indicator showing where the piece will land."""
    drop_y = drop_to_bottom(shape, x, y, grid)
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                canvas.create_rectangle(
                    x + j * BLOCK_SIZE, drop_y + i * BLOCK_SIZE,
                    x + (j + 1) * BLOCK_SIZE, drop_y + (i + 1) * BLOCK_SIZE,
                    outline="#FFFFFF", width=1, fill="#9e9d9d"
                )

def on_key_press_player1(event):
    global x1, y1, shape1, game_over1
    if game_over1:
        return
    if event.keysym == 'a' and is_valid_position(shape1, x1 - BLOCK_SIZE, y1, grid1):
        x1 -= BLOCK_SIZE
    elif event.keysym == 'd' and is_valid_position(shape1, x1 + BLOCK_SIZE, y1, grid1):
        x1 += BLOCK_SIZE
    elif event.keysym == 's':
        if is_valid_position(shape1, x1, y1 + BLOCK_SIZE, grid1):
            y1 += BLOCK_SIZE
    elif event.keysym == 'w':
        rotated_shape = [list(row) for row in zip(*shape1[::-1])]
        if is_valid_position(rotated_shape, x1, y1, grid1):
            shape1 = rotated_shape
    elif event.keysym == 'q' or event.keysym =='r':
        y1 = drop_to_bottom(shape1, x1, y1, grid1)

def on_key_press_player2(event):
    global x2, y2, shape2, game_over2  

    if game_over2:
        return
    if event.keysym == 'Left' and is_valid_position(shape2, x2 - BLOCK_SIZE, y2, grid2):
        x2 -= BLOCK_SIZE
    elif event.keysym == 'Right' and is_valid_position(shape2, x2 + BLOCK_SIZE, y2, grid2):
        x2 += BLOCK_SIZE
    elif event.keysym == 'Down':
        # Smooth Drop: Piece falls at a normal rate
        if is_valid_position(shape2, x2, y2 + BLOCK_SIZE, grid2):
            y2 += BLOCK_SIZE
    elif event.keysym == 'Up':
        rotated_shape = [list(row) for row in zip(*shape2[::-1])]
        if is_valid_position(rotated_shape, x2, y2, grid2):
            shape2 = rotated_shape
    elif event.keysym == 'l' or event.keysym == '0':
        y2 = drop_to_bottom(shape2, x2, y2, grid2)

def player1_win():
    pygame.mixer.music.stop() 
    threading.Thread(target=lambda: subprocess.run(["python", "player1_win.py"])).start()
    ui.destroy()
 
    
def player2_win():
    pygame.mixer.music.stop() 
    threading.Thread(target=lambda: subprocess.run(["python", "player2_win.py"])).start()
    ui.destroy()

def game_loop_player1():
    global x1, y1, shape1, color1, last_fall_time1, game_over1, score1, grid1, grid2, player2_KO  # Include player2_KO as a global variable

    if game_over1:
        
        # Clear all shapes from the grids
        grid1 = [[BLACK for _ in range(SCREEN_WIDTH // BLOCK_SIZE)] for _ in range(SCREEN_HEIGHT // BLOCK_SIZE)]

        if player2_KO == 2:
            # Player 1 has won
            player2_KO += 1
            p1_KO.config(text=player2_KO)  # Update KO count for Player 1
            # Display "YOU WIN" for Player 1 on their canvas
            player2_win()
            
            # Display "YOU LOSE" for Player 2 on their canvaa
        else:
            play_KO_sound()
            player2_KO += 1
            p2_KO.config(text=player2_KO)
        # Reset Player 1's position and shape
        x1, y1 = SCREEN_WIDTH // 2 - (len(shape1[0]) // 2) * BLOCK_SIZE, 0
        shape1 = random.choice(SHAPES)  # New random shape for Player 1
        color1 = random.choice(list(textures.keys()))
        if color1 == PENALTY_COLOR:
            color1 = COLOR_PASS
        last_fall_time1 = time.time() * 1000  # Reset fall timer
        game_over1 = False  # Continue the game after resetting

        # Draw the new shape at the top of the grid
        draw_shape(canvas1, shape1, color1, x1, y1)

        # Continue the game loop by scheduling the next iteration
        ui.after(30, game_loop_player1)
        return
    # Continue the normal game loop if not game over
    current_time = time.time() * 1000  # Current time in milliseconds
    if current_time - last_fall_time1 > fall_speed1:  # Check if it's time to fall
        if is_valid_position(shape1, x1, y1 + BLOCK_SIZE, grid1):
            y1 += BLOCK_SIZE
        else:
            # Lock the shape when it hits the bottom or another shape
            lock_shape(shape1, x1, y1, color1, grid1)
            cleared_rows = clear_rows(grid1, grid2)  # Clear filled rows
            score1 += cleared_rows * 10  # Update Player 1's score
            shape1 = random.choice(SHAPES)  # Get a new random shape
            color1 = random.choice(list(textures.keys()))  # Get a new random color
            if color1 == PENALTY_COLOR:
                color1 = COLOR_PASS
            x1, y1 = SCREEN_WIDTH // 2 - (len(shape1[0]) // 2) * BLOCK_SIZE, 0  # Reset position

            # If the new shape can't be placed, the game is over
            if not is_valid_position(shape1, x1, y1, grid1):
                game_over1 = True

        last_fall_time1 = current_time  # Update the last fall time

    # Update score label
    p1_score.config(text=score1)

    # Redraw everything on the canvas
    canvas1.delete("all")
    draw_grid(canvas1)  # Draw the grid
    draw_drop_indicator(canvas1, shape1, x1, y1, grid1, color1)  # Drop indicator
    draw_shape(canvas1, shape1, x1, y1, color1)  # Draw current shape

    # Render locked blocks on the grid
    for i, row in enumerate(grid1):
        for j, cell in enumerate(row):
            if cell != BLACK:  # Skip empty cells
                if cell in textures:
                    tk_texture = canvas1.textures[cell]
                    canvas1.create_image(
                        j * BLOCK_SIZE, i * BLOCK_SIZE,
                        image=tk_texture,
                        anchor="nw"
                    )
                else:
                    canvas1.create_rectangle(
                        j * BLOCK_SIZE, i * BLOCK_SIZE,
                        (j + 1) * BLOCK_SIZE, (i + 1) * BLOCK_SIZE,
                        fill=cell, outline=BLACK)

    # Continue the game loop for Player 1
    ui.after(30, game_loop_player1)

def game_loop_player2():
    global x2, y2, shape2, color2, last_fall_time2, game_over2, score2, grid2, grid1, player1_KO # Include player1_KO as a global variable

    if game_over2:
        # If Player 2's game ends, update KO count for Player 1
        # and reset the game state
        # Clear all shapes from the grids
        grid2 = [[BLACK for _ in range(SCREEN_WIDTH // BLOCK_SIZE)] for _ in range(SCREEN_HEIGHT // BLOCK_SIZE)]
        if player1_KO == 2:
            # Player 1 has won
            player1_KO += 1
            p1_KO.config(text=player1_KO)  # Update KO count for Player 1        
            player1_win()
            
            # Display "YOU LOSE" for Player 2 on their canvaa
        else:
            play_KO_sound()
            player1_KO += 1
            p1_KO.config(text=player1_KO)
        x2, y2 = SCREEN_WIDTH // 2 - (len(shape2[0]) // 2) * BLOCK_SIZE, 0
        shape2 = random.choice(SHAPES)  # New random shape for Player 2
        color2 = random.choice(list(textures.keys()))  # Random color
        if color2 == PENALTY_COLOR:
            color2 = COLOR_PASS
        last_fall_time2 = time.time() * 1000  # Reset fall timer
        game_over2 = False  # Continue the game after resetting

        # Draw the new shape at the top of the grid
        draw_shape(canvas2, shape2, color2, x2, y2)

        # Continue the game loop by scheduling the next iteration
        ui.after(30, game_loop_player2)
        return

    # Continue the normal game loop if not game over
    current_time = time.time() * 1000  # Current time in milliseconds
    if current_time - last_fall_time2 > fall_speed2:  # Check if it's time to fall
        if is_valid_position(shape2, x2, y2 + BLOCK_SIZE, grid2):
            y2 += BLOCK_SIZE
        else:
            # Lock the shape when it hits the bottom or another shape
            lock_shape(shape2, x2, y2, color2, grid2)
            cleared_rows = clear_rows(grid2, grid1)  # Clear filled rows
            score2 += cleared_rows * 10  # Update Player 2's score
            shape2 = random.choice(SHAPES)  # Get a new random shape
            color2 = random.choice(list(textures.keys()))  # Get a new random color
            if color2 == PENALTY_COLOR:
                color2 = COLOR_PASS
            x2, y2 = SCREEN_WIDTH // 2 - (len(shape2[0]) // 2) * BLOCK_SIZE, 0  # Reset position

            # If the new shape can't be placed, the game is over
            if not is_valid_position(shape2, x2, y2, grid2):
                game_over2 = True

        last_fall_time2 = current_time  # Update the last fall time

    p2_score.config(text=score2)

    # Redraw everything on the canvas
    canvas2.delete("all")
    draw_grid(canvas2)  # Draw the grid
    draw_drop_indicator(canvas2, shape2, x2, y2, grid2, color2)  # Drop indicator
    draw_shape(canvas2, shape2, x2, y2, color2)  # Draw current shape

    for i, row in enumerate(grid2):
        for j, cell in enumerate(row):
            if cell != BLACK:  # Skip empty cells
                if cell in textures:
                    tk_texture = canvas2.textures[cell]
                    canvas2.create_image(
                        j * BLOCK_SIZE, i * BLOCK_SIZE,
                        image=tk_texture,
                        anchor="nw"
                    )
                else:
                    canvas2.create_rectangle(
                        j * BLOCK_SIZE, i * BLOCK_SIZE,
                        (j + 1) * BLOCK_SIZE, (i + 1) * BLOCK_SIZE,
                        fill=cell, outline=BLACK
                    )

    # Continue the game loop for Player 2
    ui.after(30, game_loop_player2)

def add_garbage_row(grid):
    """Adds a penalty row with one random empty spot at the bottom of the grid."""
    empty_spot = random.randint(0, SCREEN_WIDTH // BLOCK_SIZE - 1)  # Random empty spot
    garbage_row = [PENALTY_COLOR if i != empty_spot else BLACK for i in range(SCREEN_WIDTH // BLOCK_SIZE)]

    grid.pop(0)  # Remove the top row
    grid.append(garbage_row)  # Add the penalty row at the bottom

def exit_ui():
    play_sound_click()
    pygame.mixer.music.stop() 
    threading.Thread(target=lambda: subprocess.run(["python", "lobby.py"])).start()
    ui.destroy()


# Create Tkinter window
ui = tk.Tk()
ui.title("BLOX-BATTLE by: IT-2A")
ui.resizable(False,False)
ui.geometry("1300x759")
ui.config(bg="black")

screen_width = ui.winfo_screenwidth()
screen_height = ui.winfo_screenheight()
window_width = 1300
window_height = 759

x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2

# Apply geometry with position and size
ui.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

player1_KO = 0
player2_KO = 0
    
background_image = Image.open("canva_bg.jpg")  # Ensure your image is in the same directory or give the full path
background_photo = ImageTk.PhotoImage(background_image)

canvas_bg = tk.Canvas(ui,bg="black")
canvas_bg.pack(fill="both", expand=True)
canvas_bg.create_image(0, 0, image=background_photo, anchor="nw")

canvas1 = tk.Canvas(canvas_bg, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bg="grey")
canvas1.place(x=323, y=98)
canvas1.textures = {color: ImageTk.PhotoImage(textures[color]) for color in textures}

canvas2 = tk.Canvas(canvas_bg, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bg='grey')
canvas2.place(x=678,y=98)
canvas2.textures = {color: ImageTk.PhotoImage(textures[color]) for color in textures}

p1_score = tk.Label(ui,text="0", font=("Arial",40),bg="#1f97a3",fg="white")
p1_score.place(x=195,y=285,anchor="center")

p1_KO = tk.Label(canvas_bg,text="0", font=("Arial",40),fg="white",bg="#17abb9")
p1_KO.place(x=180,y=420)

p2_score = tk.Label(ui,text="0", font=("Arial",40),fg="white",bg="#a01616")
p2_score.place(x=1120,y=285,anchor="center")


p2_KO = tk.Label(canvas_bg,text="0", font=("Arial",40),fg="white",bg="#d50102")
p2_KO.place(x=1100,y=420)


exit_btn = ttk.CTkButton(
    canvas_bg,
    text=" EXIT ",
    command=exit_ui,
    height=50,
    width=70,
    font=("Terminal", 30),
    fg_color="red", 
    hover_color="#e2c421" 
)
exit_btn.place(x=1150, y=20)

game_loop_player1()
game_loop_player2()

ui.bind("<a>", on_key_press_player1)
ui.bind("<d>", on_key_press_player1)
ui.bind("<s>", on_key_press_player1)
ui.bind("<w>", on_key_press_player1)
ui.bind("<q>", on_key_press_player1)
ui.bind("<r>", on_key_press_player1)

ui.bind("<Left>", on_key_press_player2)
ui.bind("<Right>", on_key_press_player2)
ui.bind("<Down>", on_key_press_player2)
ui.bind("<Up>", on_key_press_player2)
ui.bind("<l>", on_key_press_player2)
ui.bind("0", on_key_press_player2)

ui.mainloop()


