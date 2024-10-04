import tkinter as tk
import random
from PIL import Image, ImageTk
import sounddevice as sd
import numpy as np
import queue
import threading

root = tk.Tk()
root.title("Island Rescue")


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

def clear_audio_queue():
    with audio_queue.mutex:
        audio_queue.queue.clear()

def move_monkey(monkey_id, target_pos, word, sender, steps=10, delay=400):
    monkey_pos = canvas.coords(monkey_id)
    dx = (target_pos[0] - monkey_pos[0]) / steps
    dy = (target_pos[1] - monkey_pos[1]) / steps
    propability_for_shark = 1 - (0.5 **(1 / steps))

    def single_step(count):
        if count < steps:
            if random.random() < propability_for_shark:
                threading.Thread(target=play_sound, args=(600, 0.5)).start()
                canvas.delete(monkey_id)
                print("Shark!")   
                clear_audio_queue()
            else:
                canvas.move(monkey_id, dx, dy)
                audio_queue.put((100, 0.2))
                canvas.after(delay, single_step, count + 1)
        else:
            canvas.coords(monkey_id, target_pos[0], target_pos[1])
            clear_audio_queue()
            if sender == "Ernesti":
                eteteri_word_queue.put(word)
            elif sender == "Kernesti":
                pohteri_word_queue.put(word)

    single_step(0)


def ernesti_send_monkey():
    global ernesti_id, monkey_id, words, ern_word_num 
    x, y = canvas.coords(ernesti_id)
    word = words[ern_word_num]
    print(word)
    monkey_id = canvas.create_image(x-30, y-30, image=monkey)
    target_pos = canvas.coords(eteteri_id)
    move_monkey(monkey_id, target_pos, word, sender="Ernesti")
    ern_word_num = ern_word_num + 1 if ern_word_num < len(words) - 1 else 0
    
def kernesti_send_monkey():
    global kernesti_id, monkey_id, kern_word_num, words 
    x, y = canvas.coords(kernesti_id)
    word = words[kern_word_num]
    print(word)
    monkey_id = canvas.create_image(x-30, y-30, image=monkey)
    target_pos = canvas.coords(pohteri_id)
    move_monkey(monkey_id, target_pos, word, sender="Kernesti")
    kern_word_num = kern_word_num + 1 if kern_word_num < len(words) - 1 else 0

def thread_ernesti_send_monkey():
    threading.Thread(target=ernesti_send_monkey).start()

def thread_kernesti_send_monkey():
    threading.Thread(target=kernesti_send_monkey).start()

def pohteri_receive_word():
    global kern_monkey_num
    while True:
        word = pohteri_word_queue.get()
        kern_monkey_num += 1
        pohteri_received_words.append(word)
        unique_words = set(pohteri_received_words)
        print(unique_words)
        if len(unique_words) == 10:
            print("Pohteri got the message")
            send_rescueship()
            canvas.create_text(1000, 600, text="Kernesti sent a message. Let's rescue them!", font=("Arial", 12), fill="black")
            canvas.create_text(200, 400, text="Well well, semms like my message got there first!", font=("Arial", 12), fill="black")
        pohteri_word_queue.task_done()  

def eteteri_receive_word():
    global ern_monkey_num
    while True:
        ern_monkey_num += 1
        word = eteteri_word_queue.get() 
        eteteri_received_words.append(word)
        unique_words = set(eteteri_received_words)
        print(unique_words)
        if len(unique_words) == 10:
            print("Eteteri got the message")
            send_rescueship()
            canvas.create_text(1000, 400, text="Ernesti sent a message. Let's rescue them!", font=("Arial", 12), fill="black")
            canvas.create_text(400, 100, text="Ofcourse my message saved us!", font=("Arial", 12), fill="black")
        eteteri_word_queue.task_done()  

def send_rescueship():
    print("Rescue ship is on the way!")
    global rescueship_id, ernesti_id, island_id
    steps = 10
    delay = 400
    ship_pos = canvas.coords(rescueship_id)
    target_pos = canvas.coords(island_id)
    dx = (target_pos[0] - ship_pos[0]) / steps
    dy = (target_pos[1] - ship_pos[1]) / steps
    def single_step(count):
        if count < steps:
            canvas.move(rescueship_id, dx, dy)
            canvas.after(delay, single_step, count + 1)
        else:
            canvas.coords(rescueship_id, target_pos[0], target_pos[1])
            party()
    single_step(0)

def party():
    global ern_monkey_num, kern_monkey_num
    ern_people_fed = ern_monkey_num * 4
    kern_people_fed = kern_monkey_num * 4

    if(ern_people_fed > kern_people_fed):
        print("Ernesti's party was bigger")
        canvas.create_text(700, 250, text="Ernesti's party was bigger", font=("Arial", 12), fill="black")
    else:
        print("Kernesti's party was bigger")
        canvas.create_text(700, 250, text="Kernesti's party was bigger", font=("Arial", 12), fill="black")
    amount_of_black_pepper = (ern_monkey_num + kern_monkey_num) * 2
    print(f"Amount of black pepper used: {amount_of_black_pepper} tl")
    canvas.create_text(700, 270, text=f"Amount of black pepper used: {amount_of_black_pepper} tl", font=("Arial", 12), fill="black")
    


island = resize_image("island.png", 400, 400)
dock = resize_image("dock.png", 400, 400)
ernesti = resize_image("ernesti.png", 400, 400)
kernesti = resize_image("kernesti.png", 400, 400)
monkey = resize_image("monke.png", 400, 400)
dock_worker = resize_image("dock_worker.png", 400, 400)
rescueship= resize_image("rescueship.png", 400, 400)
emergency_message = "Ernesti ja Kernesti tässä terve! Olemme autiolla saarella, voisiko joku tulla sieltä sivistyneestä maailmasta hakemaan meidät pois! Kiitos"
words = emergency_message.split()
ern_word_num = 0
kern_word_num = 0
ern_monkey_num = 0
kern_monkey_num = 0
lock = threading.Lock()

canvas = tk.Canvas(width=1280, height=720)
canvas.configure(bg="#4192c3")
canvas.pack()

island_id = canvas.create_image(200, 200, image=island)
canvas.create_image(1100, 550, image=dock)

ernesti_id=canvas.create_image(400, 100, image=ernesti)
kernesti_id=canvas.create_image(200, 400, image=kernesti)
pohteri_id=canvas.create_image(1000, 600, image=dock_worker)
eteteri_id=canvas.create_image(1200, 400, image=dock_worker)
rescueship_id=canvas.create_image(700, 650, image=rescueship)

rescueship_button = tk.Button(text="Rescue Ship", command=send_rescueship)
rescueship_button.pack()

ernesti_send_monkey_button = tk.Button(text="Ernesti Sends Monkey", command=thread_ernesti_send_monkey)
ernesti_send_monkey_button.pack()

kernesti_send_monkey_button = tk.Button(text="Kernesti Sends Monkey", command=thread_kernesti_send_monkey)
kernesti_send_monkey_button.pack()

audio_queue = queue.Queue()
audio_thread = threading.Thread(target=process_audio_queue, daemon=True)
audio_thread.start()

pohteri_word_queue = queue.Queue()
eteteri_word_queue = queue.Queue()
pohteri_received_words = []
eteteri_received_words = []
pohteri_receive_word_thread = threading.Thread(target=pohteri_receive_word, daemon=True)
pohteri_receive_word_thread.start()
eteteri_receive_word_thread = threading.Thread(target=eteteri_receive_word, daemon=True)
eteteri_receive_word_thread.start()

root.mainloop()