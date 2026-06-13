import pygame
import random
import os
import time
import shutil
import threading
import keyboard
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
    if terminal_width <= 105:
        print("⚠️ Окно терминала слишком маленькое (нужно 105 символов по ширене увеличте окно) Для перепроверки нажмите Enter.")
        if input("Введите 'q' чтобы продолжить с риском ошибок: ").strip().lower() == "q":
            break
    else:
        break

pygame.mixer.init()
max_bar_size = 30
print("Плеер запущен")

volume = 100

def volume_control():
    global volume
    last_up = False
    last_down = False
    while True:
        up = keyboard.is_pressed("up")
        down = keyboard.is_pressed("down")

        if up and not last_up:
            volume = min(100, volume + 5)
            pygame.mixer.music.set_volume(volume / 100)

        if down and not last_down:
            volume = max(0, volume - 5)
            pygame.mixer.music.set_volume(volume / 100)

        last_up = up
        last_down = down
        time.sleep(0.05)


volume_thread = threading.Thread(target=volume_control, daemon=True)
volume_thread.start()
pygame.mixer.music.set_volume(1)

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
        last_time = time.time()

        while pygame.mixer.music.get_busy():
            percent = timer / duration
            bars_count = int(percent * max_bar_size)

            print(
                f"\r🎵 {track[:35]:35} | {timer // 60:02d}:{timer % 60:02d}/{minutes:02d}:{seconds:02d} | {'█' * bars_count}{'░' * (max_bar_size - bars_count)} | 🔊 Громкость:{volume}% | ",
                end=""
            )

            if time.time() - last_time >= 1:
                timer += 1
                last_time = time.time()

            time.sleep(0.05)
except KeyboardInterrupt:
    print("\nПлеер остановлен.")
