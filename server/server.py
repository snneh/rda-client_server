import socket
import tkinter as tk
from tkinter import messagebox
import threading
import pyautogui
import requests

pyautogui.FAILSAFE = False


def type_box():
    pop_window = tk.Tk()
    pop_window.title("Remote Keyboard")
    text_entered = tk.Entry(pop_window, width=100)
    text_entered.pack()
    send_but = tk.Button(
        pop_window,
        text="Type Text",
        command=lambda: conn.send(("cde:" + text_entered.get()).encode()),
    )
    del_but = tk.Button(
        pop_window, text="Delete", command=lambda: conn.send(("del".encode()))
    )
    nl_but = tk.Button(
        pop_window, text="Enter", command=lambda: conn.send(("nl".encode()))
    )
    del_but.pack()
    send_but.pack()
    nl_but.pack()
    pop_window.mainloop()


host = "0.0.0.0"

url = "http://localhost:42069/server"

payload = {"flag": "True"}
response = requests.post(url, json=payload, verify=False)


response_data = response.json()
if "code" in response_data and "port" in response_data:
    code = response_data["code"]
    port = response_data["port"]
    print(f"{code}\n{port}")


def show_details_and_wait():
    details = f"Code: {code}\nPort: {port}"
    messagebox.showinfo("Network Details", details)


def setup_connection():
    global conn, address
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    conn, address = server_socket.accept()
    print("Connection from: " + str(address))

    root = tk.Tk()
    root.title("Remote Trackpad")
    root.geometry("1000x600")

    global x, y, data
    x = 10
    y = 10

    def motion(event):
        x, y = event.x, event.y
        data = conn.recv(1024).decode()

        data = str(int(x * 2)) + " " + str(int(y * 2))
        conn.send(data.encode())

    root.bind("<Motion>", motion)

    cde = ""

    def l(o):
        conn.send("lc".encode())

    def r(o):
        conn.send("rc".encode())

    def d(o):
        conn.send("dc".encode())

    root.bind("<Button-1>", l)
    root.bind("<Button-3>", r)
    root.bind("<Button-2>", d)

    menubar = tk.Menu(root)
    menubar.add_command(label="Type", command=type_box)
    root.config(menu=menubar)

    root.mainloop()


threading.Thread(target=setup_connection).start()

show_details_and_wait()
