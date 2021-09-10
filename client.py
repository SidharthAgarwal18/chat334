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
    	socket_registered = False

    	while not socket_registered:
    		self.sok.send(('REGISTER '+send_recv+username+'\n \n').encode()) 

    		while True:
    			ack = self.sok.recv(1024).decode()
    			if ("ERROR 100" in ack):
    				print('ERROR 100 Malformed username\n \n')
    				sys.exit()
    				break
    			if ack == "REGISTERED "+send_recv+username+"\n \n":
    				socket_registered = True
    				break

    def create_connection(self,host,port,username):
        self.sok = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        
        while (True):
            try:
                self.sok.connect((host,int(port)))                
                break
            except:
                print("Couldn't connect to given host number and port number")  
                sys.exit()     

        self.username = username
        self.register(username,"TOSEND ")
        self.register(username,"TORECV ")

        message_handler = threading.Thread(target=self.handle_messages,args=())
        message_handler.start()

        input_handler = threading.Thread(target=self.input_handler,args=())
        input_handler.start()

    def handle_messages(self):
        while True:
            rec_message = self.sok.recv(1204).decode()

            if rec_message=="":
                continue
                
            rec_message = rec_message[8:]
            sender = ""

            for char in rec_message:
                if char=='\n':
                    break
                sender = sender + char

            rec_message = rec_message[(len(sender)+16):]
            len_message = ""

            for char in rec_message:
                if char=='\n':
                    break
                len_message = len_message + char

            if sender=="" or len_message=="":
                self.sok.send(("ERROR 103 Header Incomplete\n\n").encode())
                continue

            len_int = int(len_message,10)
            rec_message = rec_message[(len(len_message)+2):]

            if len(rec_message)!= len_int:
                self.sok.send(("ERROR 103 Header Incomplete\n\n").encode())
                continue

            ack_from_reciever = "RECEIVED "+sender+"\n\n"
            self.sok.send(ack_from_reciever.encode())
            print(sender+'-> '+rec_message)



    def input_handler(self):
        while True:
            message = input()
            reciptent,text = parse_sending(message)

            if(message[0]!="@" or text==""):
                print('<Kindly please enter the message in the format @reciptent text, where text is non empty>\n')
                continue
            if(reciptent==self.username):
                print('You cannot send a message to yourself')
                continue

            encoded_message = "SEND "+reciptent+"\nContent-length:"+str(len(text))+"\n\n"+text
            self.sok.send(encoded_message.encode())

            message_succ_delivered = False
            while not message_succ_delivered:
                ack = self.sok.recv(1204).decode()
                print(ack)

                if "ERROR 102" in ack:
                    print("ERROR 102 Unable to send\n\n")
                    break

                if "ERROR 103" in ack:
                    print("ERROR 103 Header Incomplete\n\n")
                    break

                if ack == "SEND "+reciptent+"\n\n":
                    message_succ_delivered = True
            
            if(message_succ_delivered):
                print("Message <"+text+"> to "+ reciptent+" successfully delivered")



if(len(sys.argv)!=4):
	print('Kindly please correctly enter arguments in the following order: host_name port_number username')
	sys.exit()
	

client = Client(sys.argv[1],int(sys.argv[2]),sys.argv[3])



