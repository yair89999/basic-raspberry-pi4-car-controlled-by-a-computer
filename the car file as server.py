##############################################################################
# server.py
##############################################################################

import socket,select,time
import board
from adafruit_motorkit import MotorKit
from gpiozero import DistanceSensor

LENGTH_FIELD_LENGTH = 4   # Exact length of length field (in bytes)(the long of the 0009 numbers in there)
DELIMITER = "|"  # Delimiter character in protocol
DATA_DELIMITER = "#"  # Delimiter in the data part of the message

global messages_to_send
messages_to_send = [] # (client IP+port, message(LOGIN_ok        |0012|aaaa#bbbb))

ERROR_MSG = "Error! "
SERVER_PORT = 5680
SERVER_IP = "192.168.1.224"

login_code = "1234"

# Protocol Messages 
# In this dictionary we will have all the client and server command names

PROTOCOL_CLIENT = {
    "log in":"LOGIN_CODE",
    "throttle":"THROTTLE"
} # .. Add more commands if needed


PROTOCOL_SERVER = {
    "user logged in":"LOGGED_SUCCESSFULLY",
    "user couldnt login":"COULD_NOT_LOG",
    "invalid command":"INVALID_COMMAND"
} # ..  Add more commands if needed

kit = MotorKit(i2c = board.I2C())

# Below will provide the DC Motor maximum current available. This allows it to rotate at top speed clockwise
kit.motor1.throttle = 1
kit.motor2.throttle = 1
kit.motor3.throttle = 1
kit.motor4.throttle = 1

kit.motor1.throttle = 0
kit.motor2.throttle = 0
kit.motor3.throttle = 0
kit.motor4.throttle = 0

def move(left_throttle,right_throttle):
    if kit.motor1.throttle == 0 and left_throttle != 0 and right_throttle != 0:
        # reset the motors for being able to control them
        kit.motor1.throttle = 1
        kit.motor2.throttle = 1
        kit.motor3.throttle = 1
        kit.motor4.throttle = 1
    kit.motor1.throttle = left_throttle
    kit.motor2.throttle = left_throttle
    kit.motor3.throttle = right_throttle
    kit.motor4.throttle = right_throttle

def build_message(cmd, data):
    """
	Gets command name (str) and data field (str) and creates a valid protocol message
	Returns: str, or None if error occured
	example of the function:
	build_message("LOGIN", "aaaa#bbbb") will return "LOGIN           |0009|aaaa#bbbb"
	"""
    """get the command plus data and return the protocol message(what parse_message gets)"""

    protocol_message = ""
    num = len(data)
    spaces = ""
    if len(str(num)) < LENGTH_FIELD_LENGTH: # create the message spaces and the message long(009,0100)
        num1 = LENGTH_FIELD_LENGTH - len(str(num))
        num = "0"*num1 + str(num)
    protocol_message += str(cmd) + spaces + DELIMITER + num + DELIMITER + str(data) # implement everything you did in the function to the protocol that send   DELIMITER = |
    return protocol_message
#print(build_message("LOGIN", "aaaa#bbbb"))
#   return full_msg


def parse_message(data):
    """
	Parses protocol message and returns command name and data field
	Returns: cmd (str), data (str). If some error occured, returns None, None
	"""
    "get the message(what build_message returns) and need to return the command and the data"
    split_data = data.split("|")
    cmd = split_data[0]
    data = split_data[2]
    return cmd,data
#print(parse_message("LOGIN           |0009|aaaa#bbbb"))
#    return cmd, msg

def join_data(msg_fields):
    """
	Helper method. Gets a list, joins all of it's fields to one string divided by the data delimiter. 
	Returns: string that looks like cell1#cell2#cell3
	"""
    msg_fields = [str(word) for word in msg_fields]
    string = DATA_DELIMITER.join(msg_fields)
    return string




# HELPER SOCKET METHODS
def build_and_send_message(conn, code, msg):
    message = build_message(code,msg) # create the message( will look like this: LOGIN_OK        |0012|aaaa#bbbb)
    messages_to_send.append((conn, message))
    print(f"[SERVER] msg to{conn.getpeername()}: ",message)	  # Debug print

def recv_message_and_parse(conn):
    full_msg = conn.recv(1024).decode() # gets the message from the server   need to be something like this for example "LOGIN           |0009|aaaa#bbbb"
    if full_msg == "":
        return None, None
    cmd, data = parse_message(full_msg) # split it to a tuple with the command and the data
    print(f"[CLIENT] {conn.getpeername()} msg: ",full_msg)  # Debug print
    return cmd, data

def setup_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket,   socket.AF_INET = IP protocol,   socket.SOCK_STREAM = protocol TCP
    sock.bind((SERVER_IP,SERVER_PORT)) # 
    sock.listen() # listen to sockets
    return sock
	



def handle_client_message(conn, cmd, data):
    host, port = conn.getpeername()
    # need to make another protocol commands but flipped for the next if(invalid command)
    """if cmd not in PROTOCOL_CLIENT:
        build_and_send_message(conn,PROTOCOL_SERVER["invalid command"],"invalid command name received")
    else:"""
    if cmd == PROTOCOL_CLIENT["log in"]:
        if data == login_code:
            print(conn.getpeername(), "logged in successfully")
            build_and_send_message(conn,PROTOCOL_SERVER["user logged in"],"")
        else:
            build_and_send_message(conn,PROTOCOL_SERVER["user couldnt login"],"")
    elif cmd == PROTOCOL_CLIENT["throttle"]:
        split = data.split(",")
        try:
            left_throttle = split[0]
            right_throttle = split[1]
            move(float(left_throttle),float(right_throttle))
        except Exception as e:
            print("Error:",e)
    else:
        pass



def main():
    global messages_to_send,room1,room2
	
    print("server is up and running")
	
    server_socket = setup_socket()
    client_sockets = []
    
    # stops every 10 seconds to ask the user if want to continue
    while True:
        ready_to_read, ready_to_write, in_error = select.select([server_socket] + client_sockets, [],[])
        for current_socket in ready_to_read: # a loop that go over all of the sockets you can read from
            if current_socket is server_socket: # if the current socket is the server socket(if a new client arrived)
                (client_socket, client_address) = current_socket.accept() # get the client socket and the client IP/create a conaction with the client
                print("New client joined!",client_address)
                client_sockets.append(client_socket) # append to the sockets list new client socket
                
            else: # if the server got new message
                #print("New data from client")
                try:
                    cmd,data = recv_message_and_parse(current_socket) # gets the command+data
                    if cmd == None or cmd == "" and data == "": # closes the socket
                        client_sockets.remove(current_socket)
                        current_socket.close()
                        print(current_socket.getpeername(),"disconnect, socket closed")
                    handle_client_message(current_socket, cmd,data)
                except Exception as e: # if it got error (will be ConnectionResetError if the client closed the cmd window)
                    #print("Error user closed cmd window\n",e)
                    try: # trying to logout
                        # doing it because if the client just close the window it wont do the logout
                        client_sockets.remove(current_socket)
                        current_socket.close()
                        print(current_socket.getpeername(),"disconnect, socket closed")
                    except: # gives an error if the socket is already closed
                        pass
                    
        for message1 in messages_to_send:
            socket1 = message1[0]
            message = message1[1]
            try:
                socket1.send(message.encode())
            except:
                pass
        messages_to_send = []



if __name__ == '__main__':
    main()