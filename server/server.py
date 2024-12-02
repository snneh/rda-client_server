#!/usr/bin/env python

import socket 
import tkinter as tk 

def type_box():
    tp_fr = tk.Tk()
    tp_fr.title('Python Remote Keyboard')
    bx_txt = tk.Entry(tp_fr, width=100)
    bx_txt.pack()
    send_but =tk.Button(tp_fr, text="Type Text", command=lambda:conn.send(('cde:'+bx_txt.get()).encode()))
    del_but =tk.Button(tp_fr, text="Delete", command=lambda:conn.send(('del'.encode())))
    nl_but =tk.Button(tp_fr, text="Enter", command=lambda:conn.send(('nl'.encode())))
    del_but.pack()
    send_but.pack()
    nl_but.pack()
    tp_fr.mainloop()


print('Host = '+socket.gethostbyname(socket.gethostname())+'\nPort = 12346')
host = ''
port = 12346
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(5)
conn, address = server_socket.accept()
print("Connection from: " + str(address))


root = tk.Tk()
root.title('Python Remote Trackpad')
root.geometry('960x540')
global x, y, data
x = 10
y = 10
def motion(event):
    x, y = event.x, event.y
    data = conn.recv(1024).decode()
    data = str(x*2)+' '+str(y*2)
    conn.send(data.encode())
root.bind('<Motion>', motion)
print(10)
cde = ''

def a(o):
    conn.send('c'.encode())
    print("Click button pressed")
def r(o):
    conn.send('r'.encode())
    print("Right Click Pressed")
def d(o):
    conn.send('d'.encode())
root.bind('<Control-l>', a)
root.bind('<Control-r>', r)
root.bind('<Control-d>', d)

menubar = tk.Menu(root)
menubar.add_command(label="Type", command=type_box)
root.config(menu = menubar)

root.mainloop()