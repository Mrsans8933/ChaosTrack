# P.S коментарии написаны ИИ
# ============================================================
# 0. ВСЁ, ЧТО НУЖНО ДЛЯ РАБОТЫ (подключаем библиотеки)
# ============================================================
import json  # чтобы читать и сохранять настройки
import customtkinter as ctk  # красивые окошки
import os  # проверка, есть ли папка
import threading  # чтобы музыка не тормозила интерфейс
import time  # для таймера
import pygame  # для звука
import random  # для рандома
from mutagen.mp3 import MP3  # длительность трека
from mutagen.id3 import ID3, APIC  # обложка
from PIL import Image, ImageTk  # картинки
import io  # работа с картинками в памяти
from tkinter import filedialog  # чтобы открыть проводник

# ============================================================
# 1. ПЕРЕМЕННЫЕ, КОТОРЫЕ ЖИВУТ ВСЮ ПРОГРАММУ
# ============================================================
config = {}  # сюда сохраним путь к музыке и другие настройки
is_paused = False  # играет или стоит? (пауза)
current_track = None  # имя трека, который играет сейчас
current_duration = 0  # сколько длится этот трек (в секундах)
cover_cache = {}  # сюда складываем обложки, чтобы не грузить их заново

# ============================================================
# 2. ЗАГРУЗКА НАСТРОЕК (если есть)
# ============================================================
def load_config():
    global config
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        return True  # всё хорошо, настройки есть
    except:
        return False  # файла нет — будем создавать

# ============================================================
# 3. ОКНО ДЛЯ ПЕРВОЙ НАСТРОЙКИ
# ============================================================
def show_config_window():
    global config
    config_app = ctk.CTk()
    config_app.geometry("500x350")
    config_app.resizable(False, False)
    ctk.set_default_color_theme("blue")

    # выбираем папку через проводник
    def choose_folder():
        folder = filedialog.askdirectory()
        if folder:
            path_entry.delete(0, ctk.END)
            path_entry.insert(0, folder)

    # сохраняем путь в конфиг
    def save_text():
        path = path_entry.get().strip()
        if not os.path.exists(path):
            error_text = ctk.CTkLabel(config_app, text="❌ Папка не найдена", text_color="red")
            error_text.place(relx=0.5, y=220, anchor="center")
        else:
            config["path"] = path.replace("\\", "/")
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            config_app.destroy()

    # рисуем окошко
    info_text = ctk.CTkLabel(config_app, text="Введите путь к папке с музыкой", font=("Arial", 23))
    info_text.place(relx=0.5, y=40, anchor="center")

    path_entry = ctk.CTkEntry(config_app, placeholder_text="Введите путь к папке", width=300)
    path_entry.place(relx=0.5, y=120, anchor="center")

    folder_btn = ctk.CTkButton(config_app, text="📂 Выбрать папку", command=choose_folder, width=150)
    folder_btn.place(relx=0.5, y=180, anchor="center")

    btn = ctk.CTkButton(config_app, text="✅ Сохранить", command=save_text, width=150)
    btn.place(relx=0.5, y=250, anchor="center")

    config_app.mainloop()

# ============================================================
# 4. ЗАГРУЗАЕМ МУЗЫКУ И ГОТОВИМ ПЛЕЕР
# ============================================================
if not load_config():  # если конфига нет — показываем окошко
    show_config_window()

print(f"Конфиг загружен: {''.join(config)}, запускаем плеер...")
music_files = [f for f in os.listdir(config.get("path")) if f.endswith(".mp3")]
pygame.mixer.init()

# ============================================================
# 5. ВСЁ ПРО ОБЛОЖКИ (загрузка, кеш, отображение)
# ============================================================
def get_cover_data(file_path):
    """достаём картинку из mp3 (если есть)"""
    try:
        tags = ID3(file_path)
        for tag in tags.values():
            if isinstance(tag, APIC):
                return tag.data
    except:
        pass
    return None

def load_cover_to_photo(cover_data, size=(220, 220)):
    """превращаем байты в картинку для интерфейса"""
    if not cover_data:
        return None
    try:
        img = Image.open(io.BytesIO(cover_data))
        img = img.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except:
        return None

def update_cover(file_path, label):
    """показываем обложку на виджете (с кешем)"""
    global cover_cache
    if file_path in cover_cache:
        photo = cover_cache[file_path]
        label.configure(image=photo)
        label.image = photo
        return

    cover_data = get_cover_data(file_path)
    photo = load_cover_to_photo(cover_data)
    if photo:
        cover_cache[file_path] = photo
        label.configure(image=photo)
        label.image = photo
    else:
        label.configure(image=None, text="🎵 Нет обложки")

# ============================================================
# 6. ПОТОК, КОТОРЫЙ КРУТИТ МУЗЫКУ (бесконечно)
# ============================================================
def play_music():
    global is_paused, current_track, current_duration

    while True:
        if not music_files:
            time.sleep(1)
            continue

        # случайный трек
        current_track = random.choice(music_files)
        full_path = os.path.join(config.get("path"), current_track)
        current_duration = MP3(full_path).info.length

        # обновляем заголовок окна
        title.configure(text=f"🎵 {current_track[:30]}")

        # показываем обложку
        update_cover(full_path, cover_label)

        # загружаем и играем
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.play()

        timer = 0
        last_time = time.time()

        # пока трек не закончился
        while True:
            # если трек кончился и не на паузе — выходим
            if not pygame.mixer.music.get_busy() and not is_paused:
                break

            # если пауза — ждём
            if is_paused:
                time.sleep(0.1)
                continue

            # обновляем прогресс каждую секунду
            if time.time() - last_time >= 1:
                timer += 1
                last_time = time.time()

                if current_duration > 0:
                    progress.set(timer / current_duration)
                    time_left.configure(text=f"{int(timer // 60):02d}:{int(timer % 60):02d}")
                    time_right.configure(
                        text=f"{int(current_duration // 60):02d}:{int(current_duration % 60):02d}"
                    )

                # если время вышло — выходим
                if timer >= current_duration:
                    break

            time.sleep(0.05)

# ============================================================
# 7. ГЛАВНОЕ ОКНО (GUI)
# ============================================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("ChaosTrack")
app.geometry("800x500")
app.resizable(False, False)

BG = "#262626"
FG = "white"
app.configure(fg_color=BG)

# ============================================================
# 8. РИСУЕМ КНОПКИ, ПОЛОСКИ, ВРЕМЯ
# ============================================================

# заголовок
title = ctk.CTkLabel(
    app,
    text="ChaosTrack",
    font=("Arial", 28, "bold"),
    text_color=FG
)
title.place(relx=0.5, y=40, anchor="center")

# режим
mode_label = ctk.CTkLabel(
    app,
    text="Режим: Chaos",
    font=("Arial", 14, "bold"),
    text_color=FG
)
mode_label.place(relx=0.5, y=80, anchor="center")

# кнопка настроек
settings_btn = ctk.CTkButton(
    app,
    text="⚙️",
    width=40,
    height=40,
    command=show_config_window,
    fg_color="transparent",
    hover_color="#333333",
    corner_radius=8,
    text_color=FG
)
settings_btn.place(x=740, y=20)

# рамка для обложки
cover_frame = ctk.CTkFrame(
    app,
    width=220,
    height=220,
    fg_color=BG,
    border_width=3,
    border_color=FG,
    corner_radius=0
)
cover_frame.place(relx=0.5, y=250, anchor="center")

cover_label = ctk.CTkLabel(
    cover_frame,
    text="🎵",
    font=("Arial", 40),
    text_color=FG
)
cover_label.place(relx=0.5, rely=0.5, anchor="center")

# прогресс-бар
progress = ctk.CTkProgressBar(
    app,
    width=400,
    height=3,
    progress_color=FG,
    fg_color="#2a2a2a"
)
progress.set(0)
progress.place(relx=0.5, y=400, anchor="center")

# время слева (сколько прошло)
time_left = ctk.CTkLabel(
    app,
    text="00:00",
    font=("Arial", 14, "bold"),
    text_color=FG
)
time_left.place(x=180, y=420)

# время справа (сколько всего)
time_right = ctk.CTkLabel(
    app,
    text="00:00",
    font=("Arial", 14, "bold"),
    text_color=FG
)
time_right.place(x=590, y=420)

# кнопка паузы
def toggle_play():
    global is_paused
    if is_paused:
        pygame.mixer.music.unpause()
        play_btn.configure(text="⏸")
        is_paused = False
    else:
        pygame.mixer.music.pause()
        play_btn.configure(text="▶")
        is_paused = True

play_btn = ctk.CTkButton(
    app,
    text="⏸",
    width=70,
    height=70,
    fg_color=FG,
    hover_color="#cccccc",
    corner_radius=35,
    font=("Arial", 30),
    text_color=BG,
    command=toggle_play
)
play_btn.place(relx=0.5, y=460, anchor="center")

# громкость
volume_slider = ctk.CTkSlider(
    app,
    from_=0,
    to=100,
    width=120,
    height=6,
    progress_color=FG,
    fg_color="#2a2a2a",
    button_color=FG,
    button_hover_color="#cccccc",
    button_corner_radius=100
)
volume_slider.set(50)
volume_slider.place(x=620, y=470)

def change_volume(value):
    pygame.mixer.music.set_volume(float(value) / 100)

volume_slider.configure(command=change_volume)

# иконка громкости
volume_label = ctk.CTkLabel(
    app,
    text="🔊",
    font=("Arial", 14),
    text_color=FG
)
volume_label.place(x=590, y=458)

# версия
version_text = ctk.CTkLabel(
    app,
    text="V3.0.0",
    font=("Arial", 14),
    text_color=FG
)
version_text.place(x=1, y=478)

# ============================================================
# 9. ЗАПУСК (поток + приложение)
# ============================================================
music_thread = threading.Thread(target=play_music, daemon=True)
music_thread.start()

app.mainloop()
