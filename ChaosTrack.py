import pygame
import random
import os
import time
from mutagen.mp3 import MP3

mus_dir = "music"
try:
    music_files = [f for f in os.listdir(mus_dir) if f.endswith(".mp3")]
    if not music_files:
        print(f"Файлов .mp3 нету в папке {mus_dir}")
except FileNotFoundError:
    os.mkdir(mus_dir)
    music_files = [f for f in os.listdir(mus_dir) if f.endswith(".mp3")]
    if not music_files:
        print(f"Файлов .mp3 нету в папке {mus_dir}")

pygame.mixer.init()

print("Плеер запущен")

try:
    while True:
        time.sleep(2)
        timer = 0

        track = random.choice(music_files)
        full_path = os.path.join(mus_dir, track)
        duration = MP3(full_path).info.length

        minutes = int(duration // 60)
        seconds = int(duration % 60)

        pygame.mixer.music.load(full_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            print(f"\rИграет: {track} | {timer // 60:02d}:{timer % 60:02d} | {minutes:02d}:{seconds:02d} | ", end="")
            time.sleep(1)
            timer += 1


except KeyboardInterrupt:
    print("\nПлеер остановлен.")
except IndexError:
    print(f"Папка {mus_dir} пуста, добавьте .mp3 файлы") fdfd