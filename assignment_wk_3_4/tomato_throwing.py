import tkinter as tk
import random
from PIL import Image, ImageTk
import sounddevice as sd
import numpy as np
import queue
import threading
import time

root = tk.Tk()
root.title("Tomato Throwing")
does_ernesti_exist = False
ernesti_id = None
kernesti_id = None
target_id = None
ernesti_skill = 4
kernesti_skill = 4
score = {"Ernesti": 0, "Kernesti": 0}
lock = threading.Lock()

def resize_image(image_path, width, height):
    image = Image.open(image_path)
    image = image.resize((width, height))
    return ImageTk.PhotoImage(image)

def play_sound(frequency, duration):
    sample_rate = 44100 
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = 0.5 * np.sin(frequency * 2 * np.pi * t)
    audio = np.int16(wave * 32767)
    sd.play(audio, sample_rate)
    sd.wait()

def process_audio_queue():
    while True:
        frequency, duration = audio_queue.get()
        play_sound(frequency, duration)
        audio_queue.task_done()

def update_scoreboard():
    canvas.itemconfig(scoreboard, text=f"Kernesti: {score['Kernesti']} Ernesti: {score['Ernesti']}")

def reset_scoreboard():
    global score
    score = {"Ernesti": 0, "Kernesti": 0}
    update_scoreboard()

def add_ernesti():
    global does_ernesti_exist, ernesti_id
    if not does_ernesti_exist:
        ernesti_id = canvas.create_image(random.randint(450, 550), 300, image=ernesti)
        does_ernesti_exist = True

def move_tomato(tomato_id, target_pos):
    tomato_pos = canvas.coords(tomato_id)
    dx = (target_pos[0] - tomato_pos[0]) / 10
    dy = (target_pos[1] - tomato_pos[1]) / 10
        
    if abs(dx) < 1 and abs(dy) < 1:
        canvas.coords(tomato_id, target_pos[0], target_pos[1])
        canvas.delete(tomato_id)
        hit_effect = canvas.create_image(target_pos[0], target_pos[1], image=splat)
        audio_queue.put((200, 0.5))
        root.after(500, lambda: canvas.delete(hit_effect))
        update_scoreboard()
        sd.stop()
    else:
        canvas.move(tomato_id, dx, dy)
        root.after(50, lambda: move_tomato(tomato_id, target_pos))

def ernesti_throw():
    global does_ernesti_exist, ernesti_id, ernesti_skill, kernesti_id 
    if does_ernesti_exist:
        x, y = canvas.coords(ernesti_id)
        tomato_id = canvas.create_image(x-30, y-30, image=tomato)  # tomato isn't directly on top of ernesti to make it look more like they are throwing the tomato
        audio_queue.put((100, 0.2))
        does_tomato_hit_target = random.randint(0, 10)
        with lock:
            if score["Ernesti"] - score["Kernesti"] == 2:
                target_pos = canvas.coords(kernesti_id)
                if does_tomato_hit_target < ernesti_skill:
                    win_text = canvas.create_text(300, 100, text="Ernesti wins!", font=("Arial", 20))
                    root.after(1000, lambda: canvas.delete(win_text))
                    reset_scoreboard()
            else:
                if does_tomato_hit_target < ernesti_skill:
                    target_pos = canvas.coords(target_id)
                    score["Ernesti"] += 1
                    if ernesti_skill < 8:
                        ernesti_skill += 1
                else:
                    target_pos = (random.randint(300, 400), random.randint(100, 300))  # Random miss position
        move_tomato(tomato_id, target_pos)
        update_scoreboard()

def kernesti_throw():
    global does_ernesti_exist, kernesti_id, kernesti_skill, ernesti_id 
    x, y = canvas.coords(kernesti_id)
    tomato_id = canvas.create_image(x+30, y-30, image=tomato)  # tomato isn't directly on top of kernesti to make it look more like they are throwing the tomato
    audio_queue.put((400, 0.2))
    does_tomato_hit_target = random.randint(0, 10)
    with lock:
        if score["Kernesti"] - score["Ernesti"] == 2:
            target_pos = canvas.coords(ernesti_id)
            if does_tomato_hit_target < kernesti_skill:
                win_text = canvas.create_text(300, 100, text="Kernesti wins!", font=("Arial", 20))
                root.after(1000, lambda: canvas.delete(win_text))
                reset_scoreboard()
        else:
            if does_tomato_hit_target < kernesti_skill:
                target_pos = canvas.coords(target_id)
                score["Kernesti"] += 1
                if kernesti_skill < 8:
                    kernesti_skill += 1
                if kernesti_skill == 6 and ernesti_id is None:
                    add_ernesti()
            else:
                target_pos = (random.randint(300, 400), random.randint(100, 300))  # Random miss position
    move_tomato(tomato_id, target_pos)
    update_scoreboard()

def simultaneous_throw():
    threading.Thread(target=ernesti_throw).start()
    threading.Thread(target=kernesti_throw).start()

def reset_scoreboard():
    global score
    score = {"Ernesti": 0, "Kernesti": 0}
    update_scoreboard()

tomato = resize_image("C:/School/Python/assignment_wk_3_4/tomato.png", 50, 50)
kernesti = resize_image("C:/School/Python/assignment_wk_3_4/kernesti.png", 100, 100)
ernesti = resize_image("C:/School/Python/assignment_wk_3_4/ernesti.png", 100, 100)
target = resize_image("C:/School/Python/assignment_wk_3_4/target.png", 80, 80)
splat = resize_image("C:/School/Python/assignment_wk_3_4/splat.png", 50, 50)

canvas = tk.Canvas(width=600, height=400)
canvas.configure(bg="white")
canvas.pack()

audio_queue = queue.Queue()
audio_thread = threading.Thread(target=process_audio_queue, daemon=True)
audio_thread.start()

target_id = canvas.create_image(300, 200, image=target)
kernesti_id = canvas.create_image(random.randint(50, 150), 300, image=kernesti)

ernesti_button = tk.Button(root, text="Add Ernesti", command=lambda: add_ernesti())
ernesti_button.pack()

ernesti_throw_button = tk.Button(root, text="Ernesti throws tomato", command=lambda: threading.Thread(target=ernesti_throw).start())
ernesti_throw_button.pack()

kernesti_throw_button = tk.Button(root, text="Kernesti throws tomato", command=lambda: kernesti_throw())
kernesti_throw_button.pack()

throw_button = tk.Button(root, text="Throw Tomatoes", command=simultaneous_throw)
throw_button.pack()

scoreboard = canvas.create_text(300, 50, text=f"Kernesti: {score['Kernesti']} Ernesti: {score['Ernesti']}", font=("Arial", 20))

reset_button = tk.Button(root, text="Reset Scoreboard", command=lambda: reset_scoreboard())
reset_button.pack()

root.mainloop()