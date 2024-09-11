import matplotlib.pyplot as plt

# Sanakirja, jossa maailmanennätysajat vuosilta 1900-2050 ja tekijät
world_record_100m = {
    1900: {'aika': 10.8, 'tekijä': 'Donald Lippincott'},
    1912: {'aika': 10.6, 'tekijä': 'Ralph Craig'},
    1920: {'aika': 10.4, 'tekijä': 'Charlie Paddock'},
    1936: {'aika': 10.3, 'tekijä': 'Jesse Owens'},
    1968: {'aika': 9.95, 'tekijä': 'Jim Hines'},
    1988: {'aika': 9.79, 'tekijä': 'Ben Johnson'},
    1996: {'aika': 9.84, 'tekijä': 'Donovan Bailey'},
    2009: {'aika': 9.58, 'tekijä': 'Usain Bolt'},
    2050: {'aika': 9.40, 'tekijä': 'Tuntematon juoksija'}
}

# Leijonien suorituskyky 100 metrin juoksussa
world_record_100m.update({
    'Simba': {'aika': 6.5},
    'Mufasa': {'aika': 7.0},
    'Nala': {'aika': 6.7},
    'Scar': {'aika': 7.5},
    'Sarabi': {'aika': 6.8},
    'Kiara': {'aika': 6.9},
    'Kovu': {'aika': 7.3},
    'Zazu': {'aika': 7.8},
    'Rafiki': {'aika': 7.1},
    'Timon': {'aika': 8.0}
})

# Graafin luonti
years = [1900, 1912, 1920, 1936, 1968, 1988, 1996, 2009, 2050]
times = [world_record_100m[year]['aika'] for year in years]

plt.plot(years, times, marker='o')
plt.title('100 metrin juoksun maailmanennätysajat (1900-2050)')
plt.xlabel('Vuosi')
plt.ylabel('Aika (sekunteina)')
plt.grid(True)
plt.show()

import tkinter as tk
import time
import random
import threading
from playsound import playsound

# Ernestin ja Kernestin ääniefektit (nämä täytyy olla äänenä .mp3 tai .wav-tiedostoina)
ernesti_sound = "klomps.mp3"  # Korvattava todellisella tiedostolla
kernesti_sound = "kips.mp3"   # Korvattava todellisella tiedostolla

def move_ernesti():
    # Arvioitu juoksuaika
    juoksuaika = random.uniform(12, 15)  # 12-15 sekuntia satunnaisesti

    # Liikuta Ernestiä radalla
    for i in range(0, 100, 10):  # 10 metrin välein
        time.sleep(juoksuaika / 10)  # Aika jaetaan 10 osaan, jokainen askel noin 1 sekunti
        canvas.move(ernesti, 10, 0)  # Liikuta 10 pikseliä oikealle
        playsound(ernesti_sound, block=False)  # Toista ääni

def move_kernesti():
    # Arvioitu juoksuaika
    juoksuaika = random.uniform(14, 18)  # 14-18 sekuntia satunnaisesti

    # Liikuta Kernestiä radalla
    for i in range(0, 100, 10):  # 10 metrin välein
        time.sleep(juoksuaika / 10)  # Aika jaetaan 10 osaan, jokainen askel noin 1 sekunti
        canvas.move(kernesti, 10, 0)  # Liikuta 10 pikseliä oikealle
        playsound(kernesti_sound, block=False)  # Toista ääni

# Avaa Tkinter-ikkuna
root = tk.Tk()
root.title("Ernesti ja Kernesti juoksuharjoitukset")

# Luo piirtoalusta juoksijoille
canvas = tk.Canvas(root, width=600, height=200)
canvas.pack()

# Luo juoksijoiden lähtöviiva ja maaliviiva
canvas.create_line(50, 100, 50, 150, fill="black", width=5)  # Lähtöviiva
canvas.create_line(550, 100, 550, 150, fill="red", width=5)  # Maaliviiva

# Luo Ernestin ja Kernestin kuvakkeet lähtöpaikalle
ernesti = canvas.create_oval(30, 110, 50, 130, fill="blue")  # Ernesti symbolinen kuvio
kernesti = canvas.create_oval(30, 140, 50, 160, fill="green")  # Kernesti symbolinen kuvio

# Luo painikkeet Ernestin ja Kernestin juoksuille
ernesti_button = tk.Button(root, text="Lähetä Ernesti juoksemaan", command=lambda: threading.Thread(target=move_ernesti).start())
ernesti_button.pack()

kernesti_button = tk.Button(root, text="Lähetä Kernesti juoksemaan", command=lambda: threading.Thread(target=move_kernesti).start())
kernesti_button.pack()

root.mainloop()