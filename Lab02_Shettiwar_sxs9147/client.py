"""Video references used for this project :
   https://www.youtube.com/watch?v=9N6a-VLBa2I
   https://www.youtube.com/watch?v=T0rYSFPAR0A
   https://www.youtube.com/watch?v=T6uCFDRVoRE
"""

import socket # to create socket and use various socket programming functions
import threading #to handle multi threading and polling
import tkinter as tk #for GUI implementation
import os # to check if file provided by client doesnt exist.
import sys
import json # for sending and receieving stored variables between server and client
import time

#=================================================================================================================
"""Declaring global variables"""
#=================================================================================================================
IP = socket.gethostbyname(socket.gethostname()) # This handles the dynamic IP address, this function  returns IP address of the HOST. ref: https://pythontic.com/modules/socket/gethostbyname
PORT = 7530
SIZE = 1024
ADDR = (IP, PORT) # IP and PORT are combined into a tuple for future references
FORMAT= "utf-8"
CLIENT = socket.socket()
SEND_DIR = "client/send/"
RECV_DIR = "client/recv/"
wordsList = [] #global list to keep track of lexicon words entered by various clients
#=================================================================================================================
#=================================================================================================================


def send(CLIENT,file_name): #This function is used to open the text file entered by user and send to server for lexicon spell check.
    while True:
        filepath = SEND_DIR + file_name # complete file name used to access predefined text files in client directory

        if os.path.exists(filepath) == False: #if file doesnt exist
            msg.insert(tk.END, f"[ERROR] File not found: {filepath}")
        else:

            CLIENT.send("Y".encode('utf8')) #
            """ Reading the file text and sending it to the server. """
            f = open(filepath, "r") #opening in read mode
            data = f.read()
            msg.insert(tk.END,f"[SENDING] :{data}")
            CLIENT.send(data.encode(FORMAT))
            break

"""This function receives all messages sent from server and directs the thread accordingly."""
def receive(CLIENT):
    global entry_filename
    global entry_username

    user_name = str(entry_username.get())
    while True:
        try:
            data = CLIENT.recv(SIZE).decode('utf8')


            if data == "accept": # if username is accepted by the server then this part is executed.

                msg.insert(tk.END, f"[SUCCESS]: You are connected as {user_name}.\n")  # ref : https://www.python-course.eu/tkinter_message_widget.php


                connect_button.configure(text="Disconnect", fg="Black", command=lambda: dconclient(CLIENT)) #Disconnect button for client to disconnect.
                submit_button.configure(state=tk.NORMAL)

                if dconflag.get() == "Z":
                    dconflag.set("1")

                submit_button.configure(text = 'Submit Filename',fg="Black", command = lambda:getfile(CLIENT,entry_filename)) #monitors submit button and goes to getfile function on its execution


            elif data == "exists": # if username already exists error is thrown and client is asked to enter a different username.
                msg.insert(tk.END, f"[ERROR]: Username: {user_name} already exists, try a different name.\n")

            elif data[:5] == "check": # executes if server replies check, corrected data is being sent back to the client here.
                file_name = str(entry_filename.get())
                f = open(RECV_DIR  + "corrected_"+file_name, 'w+')

                while data:
                    f.write(data[5:])
                    if (len(data) <= SIZE):
                        break

                f.close()
                msg.insert(tk.END, f"[RECEIVED]: {file_name} with completed spell check sequence from the server. File available at {RECV_DIR} \n" )

            elif data == "PollingRequest": #if server requests for lexicon words this elif part is executed
                msg.insert(tk.END,f"[SERVER] says: {data}")
                if len(wordsList):# ref: https://www.geeksforgeeks.org/json-dump-in-python/
                    CLIENT.send(('poll'+json.dumps(wordsList)).encode()) #json helps in string conversion.
                    wordsList.clear()
                    list_box.delete(0, tk.END)# words are cleared from the gui display as soon as the server gets the response.

            elif data == "PollingSuccess":
                msg.insert(tk.END,"Polling was successful.")

        except:
            pass

def getfile(CLIENT,entry_filename): # this function is used to get file name from client and start the execution of send thread.
    file_name = str(entry_filename.get())
    threading.Thread(target=send, args=(CLIENT,file_name)).start()
    time.sleep(1)


def connect():
    #ref : https://stackoverflow.com/questions/34653875/python-how-to-send-data-over-tcp
    #ref : https://www.geeksforgeeks.org/socket-programming-python/
    CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        CLIENT.connect(ADDR)
    except socket.error:
        msg.insert(tk.END, "[ERROR]:connection error : make sure server is running, IP and port# are correct\n")
        sys.exit(0)

    user_name = str(entry_username.get())# getting username entered by client in GUI.
    CLIENT.send(user_name.encode(FORMAT))

    threading.Thread(target=receive, args=(CLIENT,)).start() #New thread is called parallely to actively listen for servers response.


def disconnect():

    if dconflag.get() == "1":
        dconflag.set("Y")

    CLIENT.close()

    connect_button.configure(text="Connect", fg="black", command=connect)
    msg.insert(tk.END, "[NOT CONNECTED] You are not connected to the server.\n")
    submit_button.configure(text="Submit", fg="black",state = tk.DISABLED)

def dconclient(CLIENT):# this function is executed when client uses the disconnect button

    msg.insert(tk.END, "[NOT CONNECTED] You are not connected to server\n")
    CLIENT.send("Disconnect_Client".encode(FORMAT))#Sends the Disconnect_Client message to serveer
    # set the disconnection flag
    dconflag.set("Z")
    CLIENT.close()


    connect_button.configure(text="Connect", fg="Black", command=connect)
    submit_button.configure(text="Submit", fg="Black",state = tk.DISABLED)

def add_words(): #this function is used to add all words entered by various clients to a list.
    global entry_lwords
    global wordsList

    word = str(entry_lwords.get())
    wordsList.append(word) #appending the words to the wordsList
    list_box.insert(list_box.size(),word) #inserting the list to the GUI display
    entry_lwords.delete(0,tk.END)



"""GUI for client code"""
window = tk.Tk() # ref: https://www.foxinfotech.in/2018/09/how-to-create-window-in-python-using-tkinter.html
window.title("CLIENT GRAPHICAL USER INTERFACE")
frame = tk.Frame(window)


dconflag = tk.StringVar()
dconflag.set("Z")

input1 = tk.Label(text="Enter a user Name")#Username input GUI part
input1.pack(side=tk.TOP)
input1.configure(bg="pink")
entry_username = tk.Entry(window)
entry_username.pack(side=tk.TOP)
connect_button = tk.Button(window)
connect_button.pack() # ref : https://pythonguides.com/python-tkinter-button/


input2 = tk.Label(text="Enter a File Name")# FileName input GUI part
input2.pack(side=tk.TOP)
input2.configure(bg="pink")
entry_filename = tk.Entry(window)
entry_filename.pack(side=tk.TOP)
submit_button = tk.Button(window, width = 14)
submit_button.pack(side=tk.TOP)

submit_button.configure(text="Submit Filename", fg="Black",state = tk.DISABLED)


input3 = tk.Label(text="Enter words to added to the lexicon") # Lexicon words input GUI part
input3.pack(side=tk.TOP)# ref : https://www.geeksforgeeks.org/how-to-get-the-input-from-tkinter-text-box/
input3.configure(bg="pink")
entry_lwords = tk.Entry(window)
entry_lwords.pack(side=tk.TOP)
submitl = tk.Button(window, width = 14)
submitl.pack(side=tk.TOP)

submitl.configure(text="Submit Lexwords", fg="Black",command=add_words)


list_box = tk.Listbox(window, width=10)
list_box.pack(side=tk.LEFT, fill=tk.BOTH)
list_box.pack()

scrollbar = tk.Scrollbar(frame)  # ref : https://www.geeksforgeeks.org/python-tkinter-scrollbar/
msg = tk.Listbox(frame, height=30, width=50, yscrollcommand=scrollbar.set)
msg.configure(bg="turquoise")
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
msg.pack(side=tk.LEFT, fill=tk.BOTH)
msg.pack()
frame.pack()

msg.insert(tk.END, "[WAITING FOR INPUT] CLIENT has started...\n")

threading.Thread(target=disconnect).start()

tk.mainloop() # ref : https://stackoverflow.com/questions/29158220/tkinter-understanding-mainloop
