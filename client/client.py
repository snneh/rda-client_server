#!/usr/bin/env python

import pyautogui as pg
import socket



host = input('Host: ')  
port = 12345  
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate
client_socket.connect((host, port))  # connect to the server


message = 'done'
while True:
    try:
        while message.lower().strip() != 'bye':
            client_socket.send(message.encode())  # send message
            data = client_socket.recv(1024).decode()  # receive response
            if data == 'lc':
                pg.click(x, y)
            elif data=='rc':
                pg.click(button='right')
            elif data=='dc':
                pg.click(clicks=2)
            elif data=='nl':
                pg.typewrite(['enter'])
            elif data == 'del':
                pg.typewrite(['backspace'])
            elif data.startswith('cde:'):
                pg.write(data.replace('cde:', ''))
            else:
                x = int(data.split(' ')[0])
                y = int(data.split(' ')[1])
                pg.moveTo(x, y)  # show in terminal
            message = 'done' # again take input

        client_socket.close()  # close the connection
    except Exception as e:
        print(f"Error: {e}")
        break  # To exit the loop on error and avoid a silent failure