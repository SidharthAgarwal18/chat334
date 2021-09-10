import sys
import socket
import threading

def valid_username(username):

    for char in username:
        validity = ((ord(char) - 48 >=0) and (ord(char)-48<10)) or ((ord(char) - 65>=0) and (ord(char) - 122<=0))
        if not validity:
            return False
    return True


class Server:
    def __init__(self,port_num):
        self.start_server(port_num)

    def start_server(self,port_num):
        self.sok = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        
        host = socket.gethostbyname(socket.gethostname())
        port = port_num

        self.clients = []

        self.sok.bind((host,port))
        self.sok.listen(100)                        #Ask about this...
    
        print('Running server on host: '+str(host))
        print('Running server on port: '+str(port))

        self.username_lookup = {}
        self.socket_lookup = {}

        while True:
            c, addr = self.sok.accept()

            username = c.recv(1024).decode()

            if("REGISTER TOSEND" in username):
                username = username[16:(len(username)-3)]
                
            elif("REGISTER TORECV" in username):
                print('Design decision of making only one socket....')
                continue
            else:
                error_message = "ERROR 101 No user registered\n \n"
                c.send((error_message).encode())

            if(valid_username(username)):
                print('New connection. Username: '+str(username))

                self.username_lookup[c] = username
                self.socket_lookup[username] = c

                self.clients.append(c)
                c.send(("REGISTERED TOSEND "+username+"\n \n").encode())

                threading.Thread(target=self.handle_client,args=(c,addr,)).start()
            else:
                error_message = 'ERROR 100 Malformed username\n \n'
                c.send(error_message.encode())


    def broadcast(self,msg):
        for connection in self.clients:
            connection.send(msg.encode())

    def handle_client(self,c,addr):
        while True:
            try:
                msg = c.recv(1024)
            except:
                c.shutdown(socket.SHUT_RDWR)
                self.clients.remove(c)                
                print(str(self.username_lookup[c])+' left the room.')
                break

            if msg.decode() != '':
                message = msg.decode()

                if "SEND" not in message:
                    sender_username = message[9:(len(message)-2)]
                    ack_message = "SEND "+ self.username_lookup[c]+"\n\n"
                    self.socket_lookup[sender_username].send(ack_message.encode())
                    continue

                message = message[5:]

                rec_username = ""
                for char in message:
                    if char=='\n':
                        break
                    rec_username = rec_username + char

                if (rec_username not in (self.socket_lookup.keys()) and rec_username!="all"):
                    c.send(("ERROR 102 Unable to send\n\n").encode())
                    continue

                message = "FORWARD "+ self.username_lookup[c] +message[len(rec_username):]

                if rec_username!="all":
                    self.socket_lookup[rec_username].send(message.encode())
                else:
                    for username in self.socket_lookup.keys():
                        if username!=self.username_lookup[c]:
                            self.socket_lookup[username].send(message.encode())





if (len(sys.argv)!=2):
    print('Kindly please correctly enter the port number')
    sys.exit()

server = Server(int(sys.argv[1]))