import random
import string
import time
import requests
import threading
from colorama import Fore, Style, init
import customtkinter as ctk
import tkinter.messagebox as messagebox

init(autoreset=True)
ctk.set_appearance_mode("dark")

# ------------------ Nickname Generation ------------------
def generate_nick(length, first_letter="", charset="letters", use_underscore=False):
    allowed_chars = string.ascii_letters + string.digits + "_"

    if charset == "letters":
        chars = string.ascii_lowercase
    elif charset == "digits":
        chars = string.digits
    elif charset == "letters_digits":
        chars = string.ascii_lowercase + string.digits
    elif charset == "all":
        chars = string.ascii_letters + string.digits
    else:
        chars = string.ascii_lowercase

    if charset in ["letters_digits", "all"]:
        while True:
            if first_letter and first_letter != "0":
                base = first_letter.lower() + ''.join(random.choices(chars, k=length - 1))
            else:
                base = ''.join(random.choices(chars, k=length))

            if any(c.isalpha() for c in base) and any(c.isdigit() for c in base):
                break
    else:
        if first_letter and first_letter != "0":
            base = first_letter.lower() + ''.join(random.choices(chars, k=length - 1))
        else:
            base = ''.join(random.choices(chars, k=length))

    if use_underscore and length > 1:
        index = random.randint(0, length - 1)
        base = base[:index] + '_' + base[index + 1:] if index < len(base) - 1 else base[:index] + '_'

    return base

# ------------------ API Checks ------------------
def check_ashcon(nick):
    url = f"https://api.ashcon.app/mojang/v2/user/{nick}"
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 404
    except:
        return False

def check_mush(nick):
    url = f"https://mush.com.br/api/player/{nick}"
    try:
        response = requests.get(url)
        data = response.json()
        return not data.get("success", True) and data.get("error_code") == 404
    except:
        return False

# ------------------ Threaded Generation ------------------
running = False
seen_nicks = set()
current_generated_nicks = []

def safe_log(msg):
    def append_log():
        logbox.configure(state="normal")
        logbox.insert("end", msg + "\n")
        logbox.yview("end")
        logbox.configure(state="disabled")
    root.after(0, append_log)

def generate_and_check(length, amount, first_letter, charset, use_underscore):
    global running, seen_nicks, current_generated_nicks
    running = True
    generated = 0
    attempts = 0
    max_attempts = 1000

    current_generated_nicks = []

    safe_log("--- Starting nickname generation ---")

    output_file = {
        "letters": "valid_nicks_letters.txt",
        "digits": "valid_nicks_digits.txt",
        "letters_digits": "valid_nicks_letters_digits.txt",
        "all": "valid_nicks_all.txt"
    }.get(charset, "valid_nicks.txt")

    def worker():
        nonlocal generated, attempts
        while generated < amount and attempts < max_attempts and running:
            attempts += 1
            nick = generate_nick(length, first_letter, charset, use_underscore)

            if nick in seen_nicks:
                continue
            seen_nicks.add(nick)

            ashcon_available = check_ashcon(nick)
            mush_available = check_mush(nick)

            if ashcon_available and mush_available:
                with open(output_file, "a") as f:
                    f.write(nick + "\n")
                generated += 1
                current_generated_nicks.append(nick)

            safe_log(f"Generated: {nick}")
            safe_log(f"Mush: {'✅ Available' if mush_available else '❌ Taken'}")
            safe_log(f"Ashcon: {'✅ Available' if ashcon_available else '❌ Taken'}")
            safe_log("----------------------------------------")

            time.sleep(0.3)

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join()

    safe_log(f"\nFinished. {generated} valid nicknames saved to '{output_file}'.")

# ------------------ GUI Functions ------------------
def start_generation():
    global running, seen_nicks
    try:
        amount = int(amount_entry.get())
        length = int(length_entry.get())
        charset = charset_option.get()

        if length == 3:
            messagebox.showerror("Error", "The 3-character nickname option has been removed due to too many bugs.")
            return

        if length < 4 or length > 16:
            raise ValueError("Length must be between 4 and 16")

        first_letter = first_letter_entry.get()
        use_underscore = underscore_check.get()

        seen_nicks = set()

        logbox.configure(state="normal")
        logbox.delete("1.0", "end")
        logbox.configure(state="disabled")

        threading.Thread(target=generate_and_check, args=(length, amount, first_letter, charset, use_underscore), daemon=True).start()

    except Exception as e:
        messagebox.showerror("Input Error", str(e))

def stop_generation():
    global running
    running = False
    safe_log("\nGeneration stopped.")

def clear_logs():
    logbox.configure(state="normal")
    logbox.delete("1.0", "end")
    logbox.configure(state="disabled")

def copy_current_nicks():
    if not current_generated_nicks:
        messagebox.showinfo("Info", "No nicknames generated yet.")
        return
    clipboard_text = "\n".join(current_generated_nicks)
    root.clipboard_clear()
    root.clipboard_append(clipboard_text)
    messagebox.showinfo("Copied", f"Copied {len(current_generated_nicks)} nicknames.")

def save_to_txt():
    messagebox.showinfo("Info", "Files are automatically saved based on charset type!")

def show_files_info():
    messagebox.showinfo("Info", "Check the generated .txt files in your directory!")

# ------------------ CustomTkinter GUI ------------------
root = ctk.CTk()
root.title("Minecraft Nick Generator")
root.geometry("500x690")
root.configure(fg_color="#0a0a0a")

comic_font = ctk.CTkFont(family="Comic Sans MS", size=13)
comic_font_large = ctk.CTkFont(family="Comic Sans MS", size=20, weight="bold")

frame = ctk.CTkFrame(root, fg_color="#1a1a1a", border_color="#cc0000", border_width=2)
frame.pack(padx=15, pady=15, fill="both", expand=True)

title = ctk.CTkLabel(frame, text="Nick Generator - by pxzy", font=comic_font_large, text_color="#ffffff")
title.pack(pady=(15, 20))

input_frame = ctk.CTkFrame(frame, fg_color="#2a2a2a", border_color="#cc0000", border_width=1)
input_frame.pack(pady=10, padx=15, fill="x")

ctk.CTkLabel(input_frame, text="Number of Nicks:", font=comic_font, text_color="#ffffff").pack(pady=(10, 0))
amount_entry = ctk.CTkEntry(input_frame, placeholder_text="Ex: 2", font=comic_font,
                           fg_color="#333333", border_color="#cc0000", text_color="#ffffff")
amount_entry.pack(pady=(0, 10), padx=15, fill="x")

ctk.CTkLabel(input_frame, text="Nick Length (4-16):", font=comic_font, text_color="#ffffff").pack()
length_entry = ctk.CTkEntry(input_frame, placeholder_text="Ex: 6", font=comic_font,
                           fg_color="#333333", border_color="#cc0000", text_color="#ffffff")
length_entry.pack(pady=(0, 10), padx=15, fill="x")

ctk.CTkLabel(input_frame, text="First Character (optional):", font=comic_font, text_color="#ffffff").pack()
first_letter_entry = ctk.CTkEntry(input_frame, placeholder_text="Ex: a or A", font=comic_font,
                                 fg_color="#333333", border_color="#cc0000", text_color="#ffffff")
first_letter_entry.pack(pady=(0, 10), padx=15, fill="x")

ctk.CTkLabel(input_frame, text="Character Set:", font=comic_font, text_color="#ffffff").pack()
charset_option = ctk.CTkOptionMenu(input_frame,
                                  values=["letters", "digits", "letters_digits", "all"],
                                  font=comic_font, fg_color="#cc0000", button_color="#cc0000",
                                  button_hover_color="#ff1a1a")
charset_option.set("letters")
charset_option.pack(pady=(0, 10), padx=15, fill="x")

underscore_check = ctk.CTkCheckBox(input_frame, text="Use Underscore (_)", font=comic_font, text_color="#ffffff")
underscore_check.pack(pady=(0, 15), padx=15)

button_frame = ctk.CTkFrame(frame, fg_color="#2a2a2a", border_color="#cc0000", border_width=1)
button_frame.pack(padx=15, pady=5, fill="x")
button_frame.grid_columnconfigure(0, weight=1)
button_frame.grid_columnconfigure(1, weight=1)

start_button = ctk.CTkButton(button_frame, text="Start Generation", command=start_generation,
                             font=comic_font, fg_color="#cc0000", hover_color="#ff1a1a")
start_button.grid(row=0, column=0, padx=5, pady=10, sticky="ew")

stop_button = ctk.CTkButton(button_frame, text="Stop Generation", command=stop_generation,
                            font=comic_font, fg_color="#cc0000", hover_color="#ff1a1a")
stop_button.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

clear_button = ctk.CTkButton(button_frame, text="Clear Logs", command=clear_logs,
                             font=comic_font, fg_color="#cc0000", hover_color="#ff1a1a")
clear_button.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="ew")

copy_button = ctk.CTkButton(button_frame, text="Copy Generated Nicks", command=copy_current_nicks,
                            font=comic_font, fg_color="#cc0000", hover_color="#ff1a1a")
copy_button.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="ew")

logbox = ctk.CTkTextbox(frame, height=180, state="disabled",
                        fg_color="#1a1a1a", border_color="#cc0000", text_color="#ffffff",
                        font=comic_font)
logbox.pack(padx=15, pady=(10, 15), fill="both", expand=True)

root.mainloop()