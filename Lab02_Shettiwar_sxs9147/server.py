"""
SIDDHANT SHETTIWAR
1001879146
DISTRIBUTED SYSTEMS LAB ASSIGNMENT 2
"""

"""Video references used for this project :
   https://www.youtube.com/watch?v=l5WU7d49OGk&list=PLS1QulWo1RIZGSgRsn0b8w9uoWM1gHDpo
   https://www.youtube.com/watch?v=QYYiQjZLnfA
   https://www.youtube.com/watch?v=Lbfe3-v7yE0
   https://www.youtube.com/watch?v=pwfnejaWkLQ
   https://www.youtube.com/watch?v=6jteAOmdsYg
   https://www.youtube.com/watch?v=VMP1oQOxfM0
   https://www.youtube.com/watch?v=_lSNIrR1nZU
   https://www.youtube.com/watch?v=JoQLe8Ff3YE
   https://www.youtube.com/watch?v=Jl1xsH6MR1g
"""


import socket # to create socket and use various socket programming functions
import threading # to handle multi threading and polling
import tkinter as tk #for GUI
import time # to execute polling every 60 seconds
import json # for sending and receieving stored variables between server and client

#=================================================================================================================
"""Declaring global variables"""
#=================================================================================================================
IP = socket.gethostbyname(socket.gethostname()) # This handles the dynamic IP address, this function  returns IP address of the HOST. ref: https://pythontic.com/modules/socket/gethostbyname
PORT = 7530
ADDR = (IP, PORT) # IP and PORT are combined into a tuple for future references
SIZE = 1024
FORMAT = "utf-8"
clients = {}  # global list of clients to get updates everytime a new client is pushed into it.
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.bind(ADDR) # Binding the socket with a IP and PORT number.
PATH = "server/"
usernames = set()
#=================================================================================================================
#=================================================================================================================



"""Reading lexicon data and splitting it with respect to space for comparison, saving it into a global list: lex_words_list[]."""
lex_file = "server/lexicon.txt"
with open(lex_file, "r") as f:
    lex_data = f.read()
lex_words_list = lex_data.strip().split(" ")  # ref : https://pythonexamples.org/python-split-string-by-space/




def lexicon_check(data):
    """  This function takes the data from the client and compares it with the lexicon
    present in the lexicon.txt and returns the updated data"""
    global lex_words_list

    data = data.strip().split(" ")
    updated_data = []
    for d in data:
        """if small letters/words of the user input text is found in lex data, true is returned """
        if d.lower() in lex_words_list:
            updated_data.append(f"[{d}]")

            """if letters/word of the user input text is found in lex data, true is returned """
        elif d in lex_data:
            updated_data.append(f"[{d}]")

            """remaining text of the user input which wasnt found in lex returned and appended"""
        else:
            updated_data.append(d)

    updated_data = " ".join(updated_data)
    return updated_data


"""This function handles the multiple clients and the process of lexicon spell check"""
def handle_client(conn,addr):
        global lex_words_list
        # This function is used to handle the client thread.

        cname = conn.recv(SIZE).decode(FORMAT)
        username = cname # username is sent for client to server

        """if username collision happens server sends exists to client and asks to enter a different username """
        if username in usernames :
                    conn.send("exists".encode(FORMAT))

                    """If username is unique, user is accepted."""
        else :
                msg.insert(tk.END,f"[CONNECTED]: {username} has connected.\n")
                usernames.add(username)
                active_users.insert(active_users.size(),username) #to show active users on server side
                clients[conn] = username # connection is matched to its corresponding thread(client)
                try :
                    conn.send("accept".encode(FORMAT)) #server sends accept to user to indicate that user has been accepted.
                except socket.error  :
                    msg.insert(tk.END,"[ERROR]: Please check the port number and address again.\n")
                    exit(0)

                while clients :  #runs till client is connected to server
                    data = conn.recv(SIZE).decode(FORMAT)

                    try:
                        if data == "Disconnect_Client": # if client used disconnect button while loop is broken and client is removed from connected usernames
                            break
                        elif data[:4] == "poll": # excutes when polling data is sent from client
                            poll_list = json.loads(data[4:]) #https://pynative.com/python-json-load-and-loads-to-parse-json/
                            for lex in poll_list:
                                if lex not in lex_words_list:# if client given words are not in lexicon then they appended to lexicon data
                                    lex_words_list.append(lex.lower())
                            msg.insert(tk.END, f"[RECEIVED LEX WORDS]: {data[4:]}")
                            conn.send("PollingSuccess".encode(FORMAT))


                        if(data[:1]) == "Y" :#if client sends Y then file to be corrected is going to transferred to server.
                            msg.insert(tk.END,f"[NEW FILE]: {data[1:]} uploaded by username: {username}\n")

                            while True :
                                data = str(conn.recv(SIZE).decode(FORMAT))

                                msg.insert(tk.END,f"[RECEIVED DATA]: {data}")
                                if (len(data) <= SIZE):
                                    break

                            updated_data = lexicon_check(data[:]) # calling lexicon check function with data to be corrected being as a variable

                            for client in clients:
                                if clients[client] == username: #checks for client global list for the specific thread/username client which sent the data and sends the data back to it.

                                    updated_data = "check" + updated_data
                                    client.send(updated_data.encode(FORMAT))
                                    break


                    except:
                        break


                msg.insert(tk.END,f"[DISCONNECTED]: {username} has disconnected.\n")
                usernames.remove(username) # this is executed after while loop breaks when client uses disconnect button to disconnect. The client thread is then removed from

                for i, listbox_entry in enumerate(active_users.get(0, tk.END)): # Displaying active clients.
                    if listbox_entry == username: #matches index of listbox with active clients list, so the specific client which leaves is removed from the display
                        active_users.delete(i)

                del clients[conn] # Deletes the specific thread client from clients global list after the client disconnects.


def connect():
    SERVER.listen(5)
    while True:
        conn,addr = SERVER.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr)) # thread to handle_client funcction
        thread.start()
    SERVER.close()

def poll():# is called through polling thread for polling function
    while True:
        time.sleep(5) #Polling is done every 60 seconds.
        for cli in clients:
            cli.sendall("PollingRequest".encode(FORMAT)) # Send a request message to all connected clients


window = tk.Tk()
window.title("SERVER GRAPHIC USER INTERFACE")

frame=tk.Frame(window)
scrollbar = tk.Scrollbar(frame)

active_users = tk.Listbox(frame,height=20, width = 20,yscrollcommand=scrollbar.set) # Using the same listbox to display as the whole server listbox.
active_users.pack(side=tk.LEFT, fill=tk.BOTH) # To display active clients
active_users.pack()

msg = tk.Listbox(frame,height= 30, width = 50,yscrollcommand=scrollbar.set) #ref : https://stackoverflow.com/questions/4318103/resize-tkinter-listbox-widget-when-window-resizes
msg.configure(bg="pink")

scrollbar.pack(side=tk.RIGHT,fill=tk.Y) # adding scrollbar to scroll through old messages
msg.pack(side=tk.RIGHT, fill=tk.BOTH) # ref : https://www.educba.com/tkinter-scrollbar/
msg.pack()
frame.pack()

msg.insert(tk.END, f"[LISTENING] Server is listening on {IP}:{PORT}.")



connect_thread = threading.Thread(target=connect) #Thread to handle multiple clients, lexicon check process.
connect_thread.start()

poll_thread = threading.Thread(target=poll) #Thread to handle polling in parallel to lexicon check process.
poll_thread.start()

tk.mainloop()  # Starts GUI execution.
SERVER.close()

"""Writing the new lexicon words provided by the clients into the lexicon file."""
with open(lex_file,'w+') as f: # open lexicon file
    write_to_file = ''
    for lex_word in lex_words_list:
        write_to_file = write_to_file + lex_word + ' '
    f.write(write_to_file) # write, the data to the file
