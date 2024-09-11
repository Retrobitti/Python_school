import tkinter as tk
import time
import random
import threading
import numpy as np
import sounddevice as sd
import queue
import logging
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.DEBUG)

TIME_SCALE = 1000

training_data = {
    "ernesti": {"initial_time": 10.0, "current_time": 10.0},
    "kernesti": {"initial_time": 12.0, "current_time": 12.0}
}


ernesti_times = [training_data["ernesti"]["initial_time"]]
kernesti_times = [training_data["kernesti"]["initial_time"]]
training_durations = [0]

def play_sound(frequency, duration):
    try:
        logging.debug(f"Playing sound with frequency: {frequency}, duration: {duration}")
        sample_rate = 44100 
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = 0.5 * np.sin(frequency * 2 * np.pi * t)
        audio = np.int16(wave * 32767)
        sd.play(audio, sample_rate)
        sd.wait()
        logging.debug("Sound playback finished")
    except Exception as e:
        logging.error(f"Error in play_sound: {e}")

def process_audio_queue():
    while True:
        try:
            frequency, duration = audio_queue.get()
            logging.debug(f"Processing audio queue with frequency: {frequency}, duration: {duration}")
            play_sound(frequency, duration)
            audio_queue.task_done()
        except Exception as e:
            logging.error(f"Error in process_audio_queue: {e}")

def move_ernesti():
    logging.debug("Ernesti started running")
    start_time = time.time()
    juoksuaika = random.uniform(8, 10) 
    while True:
        rest_time = random.uniform(0.05, 0.2) 
        spurt_distance = random.uniform(10, 20) 
        time.sleep(juoksuaika / 10 + rest_time)
        canvas.move(ernesti, spurt_distance, 0)
        root.update()  
        audio_queue.put((100, 0.2))  
        if canvas.coords(ernesti)[2] >= 550:
            end_time = time.time()
            ernesti_time = end_time - start_time
            logging.debug(f"Ernesti reached the finish line in {ernesti_time:.2f} seconds")
            results_queue.put(('Ernesti', ernesti_time))
            break
    logging.debug("Ernesti finished running")

def move_kernesti():
    logging.debug("Kernesti started running")
    start_time = time.time()
    juoksuaika = random.uniform(9, 11) 
    while True:
        rest_time = random.uniform(0.05, 0.2) 
        spurt_distance = random.uniform(10, 20)  
        time.sleep(juoksuaika / 10 + rest_time)
        canvas.move(kernesti, spurt_distance, 0)
        root.update()  
        audio_queue.put((100, 0.2))  
        if canvas.coords(kernesti)[2] >= 550:
            end_time = time.time()
            kernesti_time = end_time - start_time
            logging.debug(f"Kernesti reached the finish line in {kernesti_time:.2f} seconds")
            results_queue.put(('Kernesti', kernesti_time))
            break
    logging.debug("Kernesti finished running")

def train_one_day():
    for _ in range(10):
        move_ernesti()
        move_kernesti()
        time.sleep(1 / TIME_SCALE) 

def train_one_month():
    for _ in range(30):  
        train_one_day()

def train_one_year():
    for _ in range(12):  
        train_one_month()

def improve_performance(duration):
   
    if duration == "day":
        factor = 1 / 365
    elif duration == "month":
        factor = 1 / 12
    elif duration == "year":
        factor = 1
    training_data["ernesti"]["current_time"] -= factor
    training_data["kernesti"]["current_time"] -= factor
    
    ernesti_times.append(training_data["ernesti"]["current_time"])
    kernesti_times.append(training_data["kernesti"]["current_time"])
    training_durations.append(training_durations[-1] + 1)

def start_training(duration):
    if duration == "day":
        train_one_day()
    elif duration == "month":
        train_one_month()
    elif duration == "year":
        train_one_year()
    improve_performance(duration)
    winner_label.config(text=f"Ernesti: {training_data['ernesti']['current_time']:.2f}s, Kernesti: {training_data['kernesti']['current_time']:.2f}s")

def plot_graph():
    plt.figure()
    plt.plot(training_durations, ernesti_times, label='Ernesti')
    plt.plot(training_durations, kernesti_times, label='Kernesti')
    plt.xlabel('Training Duration (days)')
    plt.ylabel('100m Time (seconds)')
    plt.title('Improvement in 100m Time with Training')
    plt.legend()
    plt.show()

def yhteislahto():
    threading.Thread(target=move_ernesti).start()
    threading.Thread(target=move_kernesti).start()

root = tk.Tk()
root.title("Ernesti ja Kernesti juoksuharjoitukset")

canvas = tk.Canvas(root, width=600, height=200)
canvas.pack()

canvas.create_line(50, 100, 50, 150, fill="black", width=10)
canvas.create_line(550, 100, 550, 150, fill="red", width=10)

ernesti = canvas.create_rectangle(30, 110, 50, 130, fill="orange")
kernesti = canvas.create_oval(30, 140, 50, 160, fill="gray")

audio_queue = queue.Queue()
results_queue = queue.Queue()

ernesti_button = tk.Button(root, text="Lähetä Ernesti juoksemaan", command=lambda: threading.Thread(target=move_ernesti).start())
ernesti_button.pack()

kernesti_button = tk.Button(root, text="Lähetä Kernesti juoksemaan", command=lambda: threading.Thread(target=move_kernesti).start())
kernesti_button.pack()

yhteislahto_button = tk.Button(root, text="Yhteislähtö", command=yhteislahto)
yhteislahto_button.pack()

train_day_button = tk.Button(root, text="Harjoittele 1 päivä", command=lambda: start_training("day"))
train_day_button.pack()

train_month_button = tk.Button(root, text="Harjoittele 1 kuukausi", command=lambda: start_training("month"))
train_month_button.pack()

train_year_button = tk.Button(root, text="Harjoittele 1 vuosi", command=lambda: start_training("year"))
train_year_button.pack()

plot_graph_button = tk.Button(root, text="Näytä graafi", command=plot_graph)
plot_graph_button.pack()

winner_label = tk.Label(root, text="")
winner_label.pack()

audio_thread = threading.Thread(target=process_audio_queue, daemon=True)
audio_thread.start()

root.mainloop()