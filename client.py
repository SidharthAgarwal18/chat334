import sys
import socket
import threading

def parse_sending(message):

    reciptent = ""
    for char in message[1:]:
        if char==" ":
            break
        reciptent = reciptent + char

    return reciptent,message[(2+len(reciptent)):]

class Client:
    def __init__(self,host_name,port_num,username):
        self.create_connection(host_name,port_num,username)

    def register(self,username,send_recv):
    	
        if send_recv=="TOSEND ":
            self.sokS.send(('REGISTER '+send_recv+username+'\n\n').encode()) 
        else:
            self.sokR.send(('REGISTER '+send_recv+username+'\n\n').encode())

        while (True):

            if send_recv=="TOSEND ":
                ack = self.sokS.recv(1024).decode()
            else:
                ack = self.sokR.recv(1024).decode()

            if ("ERROR 100 " in ack):
                print('ERROR 100 Malformed username\n\n')
                sys.exit()

            if ("ERROR 101 " in ack):
                print("ERROR 101 No user registered\n\n")
                break

            if ack == "REGISTERED "+send_recv+username+"\n\n":
                break

    def create_connection(self,host,port,username):
        self.sokR = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sokS = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                
        while (True):
            try:
                self.sokR.connect((host,int(port)))
                self.sokS.connect((host,int(port)))              
                break
            except:
                print("Couldn't connect to given host number and port number")  
                sys.exit()     

        self.username = username

        self.register(username,"TORECV ")
        self.register(username,"TOSEND ")        

        message_handler = threading.Thread(target=self.handle_messages,args=())
        message_handler.start()

        input_handler = threading.Thread(target=self.input_handler,args=())
        input_handler.start()

    def handle_messages(self):
        while True:
            rec_message = self.sokR.recv(1204).decode()

            if rec_message=="":
                continue   

            if rec_message[0:8] != "FORWARD ":
                self.sokR.send(("ERROR 103 Header Incomplete\n\n").encode())
                continue

            rec_message = rec_message[8:]
            sender = ""

            for char in rec_message:
                if char=='\n':
                    break
                sender = sender + char

            if rec_message[len(sender):(len(sender)+16)]!= "\nContent-length:":
                self.sokR.send(("ERROR 103 Header Incomplete\n\n").encode())
                continue

            rec_message = rec_message[(len(sender)+16):]
            len_message = ""

            validity = True

            for char in rec_message:
                if char=='\n':
                    break
                validity = ((ord(char) - 48 >=0) and (ord(char)-48<10))
                if not validity:
                    break
                len_message = len_message + char

            if sender=="" or len_message=="" or (not validity):
                self.sokR.send(("ERROR 103 Header Incomplete\n\n").encode())
                continue

            len_int = int(len_message,10)

            if rec_message[len(len_message):(len(len_message)+2)] != '\n\n':
                self.sokR.send(("ERROR 103 Header Incomplete\n\n").encode())
                continue

            rec_message = rec_message[(len(len_message)+2):]

            if len(rec_message)!= len_int:
                self.sokR.send(("ERROR 103 Header Incomplete\n\n").encode())
                continue

            ack_from_reciever = "RECEIVED "+sender+"\n\n"
            self.sokR.send(ack_from_reciever.encode())
            print(sender+'-> '+rec_message)



    def input_handler(self):
        while True:
            message = input()
            reciptent,text = parse_sending(message)

            if(message[0]!="@" or text==""):
                print('<Kindly please enter the message in the format @reciptent text, where text is non empty>\n')
                continue

            encoded_message = "SEND "+reciptent+"\nContent-length:"+str(len(text))+"\n\n"+text
            self.sokS.send(encoded_message.encode())

            while True:
                rec_message = self.sokS.recv(1204).decode()

                if rec_message=="":
                    continue

                if "ERROR 101 " in rec_message:
                    print("ERROR 101 No user registered\n\n")
                    break

                if "ERROR 102 " in rec_message:
                    print("ERROR 102 Unable to send\n\n")
                    break

                if "ERROR 103 " in rec_message:
                    print("ERROR 103 Header Incomplete\n\n")
                    print('Closing sockets..')
                    self.sokR.close()
                    self.sokS.close()
                    break

                if "SEND " in rec_message:
                    print("Message to "+ rec_message[5:(len(rec_message)-2)]+" successfully delivered")  
                    break 


if(len(sys.argv)!=4):
	print('Kindly please correctly enter arguments in the following order: host_name port_number username')
	sys.exit()
	

client = Client(sys.argv[1],int(sys.argv[2]),sys.argv[3])



