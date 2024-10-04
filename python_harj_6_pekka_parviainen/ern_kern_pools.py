import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
import random
import threading
import sounddevice as sd 
import time

def play_sound(frequency, duration):
    sample_rate = 44100 
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = 0.5 * np.sin(frequency * 2 * np.pi * t)
    audio = np.int16(wave * 32767)
    sd.play(audio, sample_rate)
    sd.wait()

def resize_image(image_path, width, height):
    image = Image.open(image_path)
    image = image.resize((width, height))
    return ImageTk.PhotoImage(image)

root = tk.Tk()
root.title("Pools")

canvas_width = 2560
canvas_height = 1440
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
canvas.configure(bg="#4192c3")
canvas.pack()

pool = np.zeros((20, 60))
ern_trench = np.ones((100, 1))
kern_trench = np.ones((100, 1))
island = canvas.create_rectangle(220, 20, 2340, 1330, fill="#f2d2a9")
forest = canvas.create_rectangle(320, 800, 800, 1240, fill="green")
monkey = resize_image("monke.png", 100, 100)
monkey_showel = resize_image("monkeshowel.png", 100, 100)
monkeys = []
cell_size = 10
pool_width = pool.shape[1] * cell_size
pool_height = pool.shape[0] * cell_size
ern_monkey_positions = {}
kern_monkey_positions = {}
ern_trench_texts = {}
kern_trench_texts = {}
ern_last_start_position = ern_trench.shape[0] - 1
kern_last_start_position = kern_trench.shape[0] - 1
center_x = canvas_width / 2
center_y = canvas_height / 2
start_x = center_x - pool_width / 2
start_y = center_y - pool_height / 2 +400
trench_start_y = start_y - 1000
stop_event = threading.Event()
ern_first_monkey = True
kern_first_monkey = True

def draw_pool():
    bool_water = False
    for i in range(pool.shape[0]):
        for j in range(pool.shape[1]):
            x = start_x + j * cell_size + cell_size // 2
            y = start_y + i * cell_size + cell_size // 2
            canvas.create_text(x, y, text="0" if not bool_water else "3", fill="black", font=("Arial", 6))

def draw_ern_trench():
    for i in range(ern_trench.shape[0]):
        x = start_x + 10
        y = trench_start_y + i * cell_size + cell_size // 2
        text_item = canvas.create_text(x, y, text="1", fill="black", font=("Arial", 6))
        ern_trench_texts[i] = text_item

def draw_kern_trench():
    for i in range(kern_trench.shape[0]):
        x = start_x + pool_width -10
        y = trench_start_y + i * cell_size + cell_size // 2
        kern_text_item = canvas.create_text(x, y, text="1", fill="black", font=("Arial", 6))
        kern_trench_texts[i] = kern_text_item

def iddle_monkeys():
    for i in range (20):
        monke = canvas.create_image(400 + i * 20, 850 + i * 20, image = monkey)
        monkeys.append(monke)    

def ern_get_monkey():
    global monkeys, ern_last_start_position, ern_first_monkey
    if len(monkeys) > 0:
        monkey = monkeys.pop()
        if ern_first_monkey:
            ern_last_start_position = random.randint(0, ern_trench.shape[0] - 1)
            ern_first_monkey = False
        if ern_last_start_position < 2:
            ern_last_start_position = ern_trench.shape[0] - 1
        x = start_x + 10
        y = trench_start_y + ern_last_start_position * cell_size + cell_size // 2
        canvas.coords(monkey, x, y)
        canvas.itemconfig(monkey, image=monkey_showel)
        ern_monkey_positions[monkey] = ern_last_start_position
        ern_last_start_position -= 10
        threading.Thread(target=ern_monkey_dig, args=(monkey,), daemon=True).start()

def kern_get_monkey():
    global monkeys, kern_last_start_position, kern_first_monkey
    if len(monkeys) > 0:
        monkey = monkeys.pop()
        if kern_first_monkey:
            kern_last_start_position = random.randint(0, kern_trench.shape[0] - 1)
            kern_first_monkey = False
        if kern_last_start_position < 2:
            kern_last_start_position = kern_trench.shape[0] - 1
        x = start_x + pool_width - 10
        y = trench_start_y + kern_last_start_position * cell_size + cell_size // 2
        canvas.coords(monkey, x, y)
        canvas.itemconfig(monkey, image=monkey_showel)
        kern_monkey_positions[monkey] = kern_last_start_position
        kern_last_start_position -= 10 
        threading.Thread(target=kern_monkey_dig, args=(monkey,), daemon=True).start()

def ern_get_monkey_thread():
    stop_event.clear()  
    threading.Thread(target=ern_get_monkey, daemon=True).start()

def kern_get_monkey_thread():
    stop_event.clear()  
    threading.Thread(target=kern_get_monkey, daemon=True).start()

def ern_monkey_dig(monkey):
    fatigue = 1
    while any(ern_trench[:, 0] == 1):
            if stop_event.is_set():
                break
            position = ern_monkey_positions[monkey]
            if position < ern_trench.shape[0]:  
                full_sleep = fatigue
                check_interval = 0.1  
                while full_sleep > 0:
                    if stop_event.is_set():  
                        return  
                    time.sleep(min(check_interval, full_sleep))  
                    full_sleep -= check_interval
                if ern_trench[position, 0] == 3:
                    break
                else:            
                    ern_trench[position, 0] = 0
                    current_text = canvas.itemcget(ern_trench_texts[position], "text")
                    new_text = str(int(current_text) - 1)
                    canvas.itemconfig(ern_trench_texts[position], text=new_text)
                    new_position = position - 1
                    if new_position >= 0:  
                        x = start_x + 10
                        y = trench_start_y + new_position * cell_size + cell_size // 2
                        canvas.coords(monkey, x, y)
                        ern_monkey_positions[monkey] = new_position
                        play_sound(440, 0.2)
                        fatigue += 2
                        print(fatigue)   
    root.update()  
    root.after(100) 

def kern_monkey_dig(monkey):
    fatigue = 1
    while any(kern_trench[:, 0] == 1):
            if stop_event.is_set():
                break
            position = kern_monkey_positions[monkey]
            if position < kern_trench.shape[0]:  
                full_sleep = fatigue
                check_interval = 0.1  
                while full_sleep > 0:
                    if stop_event.is_set():  
                        return  
                    time.sleep(min(check_interval, full_sleep))  
                    full_sleep -= check_interval
                if kern_trench[position, 0] == 3:
                    break
                else:            
                    kern_trench[position, 0] = 0
                    current_text = canvas.itemcget(kern_trench_texts[position], "text")
                    new_text = str(int(current_text) - 1)
                    canvas.itemconfig(kern_trench_texts[position], text=new_text)
                    new_position = position - 1
                    if new_position >= 0:  
                        x = start_x + pool_width - 10
                        y = trench_start_y + new_position * cell_size + cell_size // 2
                        canvas.coords(monkey, x, y)
                        kern_monkey_positions[monkey] = new_position
                        play_sound(440, 0.2)
                        fatigue += 2
                        print(fatigue)   
    root.update()  
    root.after(100) 

def reset_monkeys_and_trenches():
    global ern_last_start_position, kern_last_start_position, ern_first_monkey, kern_first_monkey
    stop_event.set()
    for each in ern_monkey_positions:
        canvas.delete(each)
    for each in kern_monkey_positions:
        canvas.delete(each)
    for i in range(ern_trench.shape[0]):
        canvas.itemconfig(ern_trench_texts[i], text="1")
    for i in range(kern_trench.shape[0]):
        canvas.itemconfig(kern_trench_texts[i], text="1")
    ern_trench.fill(1)
    kern_trench.fill(1)
    ern_first_monkey = True
    kern_first_monkey = True
    iddle_monkeys()
    
    
    ern_last_start_position = ern_trench.shape[0] - 1
    kern_last_start_position = kern_trench.shape[0] - 1

def ern_put_monkeys_to_work():
    stop_event.clear()  # Clear the stop event
    threading.Thread(target=lambda: [(ern_get_monkey_thread(), time.sleep(1)) for _ in range(10) if not stop_event.is_set()], daemon=True).start()
  
def kern_put_monkeys_to_work():
    stop_event.clear()
    threading.Thread(target=lambda: [(kern_get_monkey_thread(), time.sleep(1)) for _ in range(10) if not stop_event.is_set()], daemon=True).start()

def ocean_fill_trench():
    ern_latest_checked_index = 0
    kern_latest_checked_index = 0
    stop_event.clear()
    while not stop_event.is_set():
        if ern_latest_checked_index < ern_trench.shape[0]:
            if ern_trench[ern_latest_checked_index, 0] <= 0:
                ern_trench[ern_latest_checked_index, 0] = 3
                canvas.itemconfig(ern_trench_texts[ern_latest_checked_index], text="3")
                ern_latest_checked_index += 1
                play_sound(100, 0.2)
            else:
                time.sleep(0.1)
        if kern_latest_checked_index < kern_trench.shape[0]:
            if kern_trench[kern_latest_checked_index, 0] <= 0:
                kern_trench[kern_latest_checked_index, 0] = 3
                canvas.itemconfig(kern_trench_texts[kern_latest_checked_index], text="3")
                kern_latest_checked_index += 1
                play_sound(100, 0.2)
            else:
                time.sleep(0.1)
        else:
            time.sleep(0.1)

def fill_pool():
    while not stop_event.is_set():
        if all(ern_trench == 3):
            pool[:, :] = 3 
            for i in range(pool.shape[0]):
                for j in range(pool.shape[1]):
                    x = start_x + j * cell_size + cell_size // 2
                    y = start_y + i * cell_size + cell_size // 2
                    canvas.create_text(x, y, text="3", fill="black", font=("Arial", 6))
            play_sound(200, 10)
            break
        if all(kern_trench == 3):
            pool[:, :] = 3  
            for i in range(pool.shape[0]):
                for j in range(pool.shape[1]):
                    x = start_x + j * cell_size + cell_size // 2
                    y = start_y + i * cell_size + cell_size // 2
                    canvas.create_text(x, y, text="3", fill="black", font=("Arial", 6))
            play_sound(700, 10) 
            break
        else:
            time.sleep(0.5)

threading.Thread(target=ocean_fill_trench, daemon=True).start()
threading.Thread(target=fill_pool, daemon=True).start() 
draw_pool()
draw_ern_trench()
draw_kern_trench()
iddle_monkeys()

button = tk.Button(root, text="Get a monkey", command=ern_get_monkey_thread)
button.place(x=100, y=100)

button = tk.Button(root, text="Monkeys to work", command=lambda: threading.Thread(target=ern_put_monkeys_to_work, daemon=True).start())
button.place(x=100, y=200)

button = tk.Button(root, text="Get a monkey", command=kern_get_monkey_thread)
button.place(x=2400, y=100)

button = tk.Button(root, text="Monkeys to work", command=lambda: threading.Thread(target=kern_put_monkeys_to_work, daemon=True).start())
button.place(x=2400, y=200)

button_reset = tk.Button(root, text="Reset", command=reset_monkeys_and_trenches)
button_reset.place(x=300, y=100)
root.mainloop()
