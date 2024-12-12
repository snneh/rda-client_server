import pyautogui as pg
import socket
import tkinter as tk
from PIL import Image, ImageTk
import io
import threading
import time
import requests

pg.FAILSAFE = False


host = "localhost"
port = 12345

code = input("Code: ")
url = "http://localhost:6969/client"

payload = {"code": code}
response = requests.post(url, json=payload)


try:
    response_data = response.json()
    if "localIP" in response_data and "port" in response_data:
        host = response_data["localIP"]
        port = response_data["port"]
    else:
        print("Invalid response data")
except ValueError:
    print("Invalid JSON response")

message = "done"


def setup_connection():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    while True:
        client_socket.send(message.encode())
        data = client_socket.recv(1024).decode()

        if data == "lc":
            pg.click(x, y)
            time.sleep(0.1)
        elif data == "rc":
            pg.click(button="right")
            time.sleep(0.1)
        elif data == "dc":
            pg.click(clicks=2)
            time.sleep(0.1)
        elif data == "nl":
            pg.typewrite(["enter"])
        elif data == "del":
            pg.typewrite(["backspace"])
        elif data.startswith("cde:"):
            pg.write(data.replace("cde:", ""))
        else:
            x = int(data.split(" ")[0])
            y = int(data.split(" ")[1])
            pg.moveTo(x, y)


setup_connection()
