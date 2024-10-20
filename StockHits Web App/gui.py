import tkinter as tk
import subprocess
import threading
import webbrowser
import os
import sys

def start_server():
    script_path = os.path.join(os.path.dirname(__file__), 'start.py')
    subprocess.run([sys.executable, script_path])

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5001/")

def start_app():
    threading.Thread(target=start_server).start()
    threading.Timer(1, open_browser).start()

app = tk.Tk()
app.title("Stock Data Viewer")

start_button = tk.Button(app, text="Start Server and Open Browser", command=start_app)
start_button.pack(pady=20)

app.mainloop()
