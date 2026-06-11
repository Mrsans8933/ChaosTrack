import pygame
import random
import os
import time
import shutil
from mutagen.mp3 import MP3


try:
    with open("path.txt", "r") as f:
        mus_dir = f.read().strip()
        if not mus_dir:
            raise ValueError("Путь пуст")
except FileNotFoundError or ValueError:
    print("Файл path.txt не найден или пуст.")
    mus_dir = input("Введите путь к папке с музыкой: ").strip()
    with open("path.txt", "w") as f:
        f.write(mus_dir)
    print(f"Путь сохранён в path.txt: {mus_dir}")

if not os.path.isdir(mus_dir):
    print(f"Папка '{mus_dir}' не существует. Проверьте путь в path.txt")
    exit()

music_files = [f for f in os.listdir(mus_dir) if f.endswith(".mp3")]
if not music_files:
    print(f"В папке '{mus_dir}' нет .mp3 файлов")
    exit()


while True:
    terminal_width = shutil.get_terminal_size().columns
    if terminal_width <= 85:
        print("⚠️ Окно терминала слишком маленькое (нужно ≥86).")
        if input("Введите 'q' чтобы продолжить с риском ошибок: ").strip().lower() == "q":
            break
    else:
        break

pygame.mixer.init()
max_bar_size = 30
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
            percent = timer / duration
            bars_count = int(percent * max_bar_size)

            print(
                f"\r🎵 {track[:35]:35} | {timer // 60:02d}:{timer % 60:02d}/{minutes:02d}:{seconds:02d} | {'█' * bars_count}{'░' * (max_bar_size - bars_count)} |",
                end=""
            )
            time.sleep(1)
            timer += 1

except KeyboardInterrupt:
    print("\nПлеер остановлен.")
