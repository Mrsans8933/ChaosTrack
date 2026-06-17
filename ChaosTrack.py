# ========== Импорт ==========
import json
import pygame
import random
import os
import time
import shutil
import threading
import keyboard
from mutagen.mp3 import MP3

# ========== Проверка и создание файла config.json ==========
script_dir = os.path.dirname(os.path.abspath(__file__))

try:
    with open(os.path.join(script_dir, "config.json"), "r", encoding="utf-8") as f:
        config = json.load(f)
    mus_dir = config.get("music_path")
    if not mus_dir:
        raise KeyError("music_path not found")
except (FileNotFoundError, KeyError):
    while True:
        print("Здравствуйте, давайте настроим управление под вас")
        path = input("Введите путь к папке с музыкой: ").strip()
        if not os.path.isdir(path):
            input(f"'{path}' не найден. Проверьте существование этого пути.\nНажмите Enter для перезапуска")
            os.system("clear")
            continue

        volume_up_key = input(
            "Введите клавишу для увеличения громкости звука или название и нажмите Enter\n(По умолчанию: 'up'): "
        )
        if not volume_up_key:
            volume_up_key = "up"

        volume_down_key = input(
            "Введите клавишу для понижения громкости звука или название клавиши и нажмите Enter\n(По умолчанию: 'down'): "
        )
        if not volume_down_key:
            volume_down_key = "down"

        pause_key = input(
            "Введите клавишу для паузы или название клавиши и нажмите Enter\n(По умолчанию: 'right_shift'): "
        )
        if not pause_key:
            pause_key = "right_shift"

        print(f"""
          Ваш конфиг:
          Путь к музыке: {path}
          Повышение громкости: {volume_up_key}
          Понижение громкости: {volume_down_key}
          Пауза: {pause_key}
          """)

        choose = input("Вас устраивает такой конфиг? [Y/N] ").lower()
        if choose == "y" or not choose:
            config = {
                "music_path": path,
                "volume_up_key": volume_up_key,
                "volume_down_key": volume_down_key,
                "pause_key": pause_key,
                "volume": 50
            }
            print("Конфиг сохранён ✅")
            break

    config_path = os.path.join(script_dir, "config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

# ========== Забираем значения из конфига ==========
volume_up_key = config.get("volume_up_key")
volume_down_key = config.get("volume_down_key")
pause_key = config.get("pause_key")
mus_dir = config.get("music_path")
volume = config.get("volume", 50)

# ========== Проверка существования папки ==========
if not os.path.isdir(mus_dir):
    print(f"❌ Папка '{mus_dir}' не существует. Проверьте путь в config.json")
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
print(f"""
╔══════════════════════════════════════════════════╗
║              ChaosTrack v1.0                     ║
║      Случайный аудиоплеер                        ║                          
║      Ctrl+C   - выход                            ║
╚══════════════════════════════════════════════════╝
""")

print("Плеер запущен")
is_paused = False

# ========== Обьявляем главные функции для потоков ==========

def pause_control():
    global is_paused
    last_p = False
    while True:
        p = keyboard.is_pressed(pause_key)
        if p and not last_p:
            if is_paused:
                pygame.mixer.music.unpause()
                is_paused = False
            else:
                pygame.mixer.music.pause()
                is_paused = True
        last_p = p
        time.sleep(0.05)
def volume_control():
    global volume, config
    last_up = False
    last_down = False
    while True:
        up = keyboard.is_pressed(volume_up_key)
        down = keyboard.is_pressed(volume_down_key)

        if up and not last_up:
            volume = min(100, volume + 5)
            pygame.mixer.music.set_volume(volume / 100)
            config["volume"] = volume
            with open(os.path.join(script_dir, "config.json"), "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)

        if down and not last_down:
            volume = max(0, volume - 5)
            pygame.mixer.music.set_volume(volume / 100)
            config["volume"] = volume
            with open(os.path.join(script_dir, "config.json"), "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)

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
