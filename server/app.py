import socket
import threading
import json
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Controller as KeyboardController, Key
import mss
import cv2
import numpy as np
import pickle
import struct
import pyautogui
from tkinter import messagebox, Tk
import requests

PORT = MOUSE_PORT = KEYBOARD_PORT = SCREENSHARE_PORT = 0

url = "http://localhost:42069/server"

payload = {"flag": "True"}
response = requests.post(url, json=payload, verify=False)


response_data = response.json()
if "code" in response_data and "port" in response_data:
    code = response_data["code"]
    PORT = response_data["port"]
    MOUSE_PORT = response_data["mouse_port"]
    KEYBOARD_PORT = response_data["keyboard_port"]
    SCREENSHARE_PORT = response_data["screenshare_port"]
    print(f"Code : {code}")


def handle_mouse(client_socket):
    mouse = MouseController()
    buffer = ""

    while True:
        try:
            buffer += client_socket.recv(1024).decode()
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                data = json.loads(line)
                action, x, y = data["type"], int(data["x"]), int(data["y"])

                if action == "move":
                    mouse.position = (x, y)
                elif action == "click":
                    mouse.position = (x, y)
                    mouse.click(Button.left, 1)
                    print(f"Left clicked at ({x}, {y})")
                elif action == "rightclick":
                    mouse.position = (x, y)
                    mouse.click(Button.right, 1)
                    print(f"Right clicked at ({x}, {y})")
        except Exception as e:
            print(f"Mouse socket error: {e}")
            break


SPECIAL_KEYS = {
    "enter": Key.enter,
    "shift": Key.shift,
    "ctrl": Key.ctrl_l,
    "ctrl": Key.ctrl_r,
    "alt": Key.alt,
    "tab": Key.tab,
    "esc": Key.esc,
    "backspace": Key.backspace,
    "caps_lock": Key.caps_lock,
    "cmd": Key.cmd,
    "delete": Key.delete,
    "space": Key.space,
    "up": Key.up,
    "down": Key.down,
    "left": Key.left,
    "right": Key.right,
}


def handle_keyboard(client_socket):
    keyboard = KeyboardController()
    buffer = ""

    while True:
        try:
            buffer += client_socket.recv(1024).decode()
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)

                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    print(f"Invalid JSON: {line}")
                    continue

                # Accept either a string or a list of keys
                keys = data.get("key")
                if not keys:
                    continue

                # Normalize input
                if isinstance(keys, str):
                    keys = [keys]

                key_objects = []
                for k in keys:
                    k = k.lower()
                    key_objects.append(
                        SPECIAL_KEYS.get(k, k)
                    )  # fallback to literal key if not special

                # Press and release keys (for combinations, hold modifiers)
                if len(key_objects) == 1:
                    key = key_objects[0]
                    if isinstance(key, Key):
                        keyboard.press(key)
                        keyboard.release(key)
                    else:
                        keyboard.type(str(key))
                else:
                    try:
                        for key in key_objects:
                            keyboard.press(key)
                        for key in reversed(key_objects):
                            keyboard.release(key)
                    except Exception as e:
                        print(f"Failed to press combo: {keys} -> {e}")

        except Exception as e:
            print(f"Keyboard socket error: {e}")
            break


def handle_screenshare(client_socket, client_addr):
    while True:
        try:
            sct = mss.mss()
            monitor = sct.monitors[1]

            # Continuous screen sharing
            while True:
                # Capture screen
                sct_img = sct.grab(monitor)
                img = np.array(sct_img)

                # Get cursor position
                cursor_x, cursor_y = pyautogui.position()
                cursor_x = min(
                    max(cursor_x, monitor["left"]),
                    monitor["left"] + monitor["width"] - 1,
                )
                cursor_y = min(
                    max(cursor_y, monitor["top"]),
                    monitor["top"] + monitor["height"] - 1,
                )
                cv2.circle(
                    img,
                    (cursor_x - monitor["left"], cursor_y - monitor["top"]),
                    7,
                    (0, 0, 255),
                    -1,
                )

                # Convert image to BGR format
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                # Compress the image
                _, compressed_frame = cv2.imencode(
                    ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80]
                )

                # Serialize frame
                data = pickle.dumps(compressed_frame)

                # Send frame size
                client_socket.sendall(struct.pack("L", len(data)) + data)

                # Control frame rate
                # cv2.waitKey(30)

        except Exception as e:
            print(f"Screenshare socket error: {e}")
            break


def main():
    # Create TCP socket for main connection
    main_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_server.bind(("0.0.0.0", PORT))
    main_server.listen(5)
    print(f"Server IP: {socket.gethostbyname(socket.gethostname())}")

    mouse_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    keyboard_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    screenshare_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    mouse_socket.bind(("0.0.0.0", MOUSE_PORT))
    keyboard_socket.bind(("0.0.0.0", KEYBOARD_PORT))
    screenshare_socket.bind(("0.0.0.0", SCREENSHARE_PORT))

    print("Main server listening.")
    mouse_socket.listen(5)
    keyboard_socket.listen(5)
    screenshare_socket.listen(5)

    mouse_conn, mouse_addr = mouse_socket.accept()
    keyboard_conn, keyboard_addr = keyboard_socket.accept()
    screenshare_conn, screenshare_addr = screenshare_socket.accept()

    threading.Thread(target=handle_mouse, args=(mouse_conn,), daemon=True).start()
    threading.Thread(target=handle_keyboard, args=(keyboard_conn,), daemon=True).start()

    threading.Thread(
        target=handle_screenshare, args=(screenshare_conn, None), daemon=True
    ).start()

    while True:
        try:
            conn, addr = main_server.accept()
            print(f"Client connected from {addr}")
            # You can handle the main connection here if needed
        except KeyboardInterrupt:
            mouse_socket.close()
            keyboard_socket.close()
            main_server.close()
            screenshare_socket.close()
            return


if __name__ == "__main__":
    main()
