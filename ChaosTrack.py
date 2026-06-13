# ========== Импорт ==========
import pygame
import random
import os
import time
import shutil
import threading
import keyboard
from mutagen.mp3 import MP3

# ========== Проверка и создание файла path.txt ==========
try:
    with open("path.txt", "r") as f:
        mus_dir = f.read().strip()      #
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
# ========== Проверка ширины терминала для корректного отображения
while True:
    terminal_width = shutil.get_terminal_size().columns
    if terminal_width <= 105:
        print("⚠️ Окно терминала слишком маленькое (нужно 105 символов по ширине. Увеличьте окно окно) Для перепроверки нажмите Enter.")
        if input("Введите 'q' чтобы продолжить с риском ошибок: ").strip().lower() == "q":
            break
    else:
        break
# ========== Инициализируем и задаем переменные ==========
pygame.mixer.init()
max_bar_size = 30
print("""
╔══════════════════════════════════════════════════╗
║              ChaosTrack v1.0                     ║
║      Случайный аудиоплеер                        ║
║                                                  ║
║  Управление:                                     ║
║    ↑/↓      - громкость                          ║
║    right_shift - пауза                           ║
║    Ctrl+C   - выход                              ║
╚══════════════════════════════════════════════════╝
""")

print("Плеер запущен")
volume = 100
is_paused = False

# ========== Обьявляем главные функции для потоков ==========

def pause_control():
    global is_paused
    last_p = False
    while True:
        p = keyboard.is_pressed("right_shift")
        if p and not last_p:
            if is_paused:
                pygame.mixer.music.unpause()
                is_paused = False
            else:
                pygame.mixer.music.pause()
                is_paused = True
        last_p = p
        time.sleep(0.05)
def volume_control(): # Для контроля громкости звука
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

# ========== Создаем потоки ==========
volume_thread = threading.Thread(target=volume_control, daemon=True)
pause_thread = threading.Thread(target=pause_control, daemon=True)

# ========== Запускаем потоки ==========
volume_thread.start()
pause_thread.start()

# ========== Задаем обычную громкость звука
pygame.mixer.music.set_volume(1)

# ========== Запускаем главный цикл ==========
try:
    while True:
        time.sleep(2)
        timer = 0
# ========== Выбираем рандомный трек и составляем полный путь к музыке и определяем длину трека ==========
        track = random.choice(music_files)
        full_path = os.path.join(mus_dir, track)
        duration = MP3(full_path).info.length

        minutes = int(duration // 60)
        seconds = int(duration % 60)
        # ========== Загружаем и запускаем музыку ==========
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.play()
        last_time = time.time()
        # ========== Запускаем команды которые будут выполнятся во время произведения трека ========
        while pygame.mixer.music.get_busy() or is_paused:
            if is_paused:
                time.sleep(0.05)
                continue

            percent = timer / duration   # Вычисляем процент проигравшего трека
            bars_count = int(percent * max_bar_size) # Определяет количество линий относительно отыгранного трека
            # ========== Основной вывод информации
            print(
                f"\r🎵 {track[:35]:35} | {timer // 60:02d}:{timer % 60:02d}/{minutes:02d}:{seconds:02d} | {'█' * bars_count}{'░' * (max_bar_size - bars_count)} | 🔊 Громкость:{volume}% | ",
                end=""
            )
            # ========== Подсчет секунд ==========
            if time.time() - last_time >= 1:
                timer += 1
                last_time = time.time()

            time.sleep(0.05)

except KeyboardInterrupt:
    print("\nПлеер остановлен.")
