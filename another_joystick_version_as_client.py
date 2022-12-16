import pygame,socket,os,time,random
from win32api import GetSystemMetrics

screen_x,screen_y = 800,800
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (GetSystemMetrics(0)//2 - screen_x//2,GetSystemMetrics(1)//2-screen_y//2) # place the window in the screen( in this example 300 from the left side of the screen and 50 from the top of the screen)
pygame.init()
window = pygame.display.set_mode((screen_x,screen_y))
pygame.display.set_caption("rpi4 joystick controller, client 2.0")
font = pygame.font.SysFont('Corbel', 30)

SERVER_IP = "192.168.1.224"  # the raspberry pi IP
SERVER_PORT = 5680


LENGTH_FIELD_LENGTH = 4   # Exact length of length field (in bytes)(the long of the 0009 numbers in there)
DELIMITER = "|"  # Delimiter character in protocol
DATA_DELIMITER = "#"  # Delimiter in the data part of the message

# Protocol Messages 
# In this dictionary we will have all the client and server command names

PROTOCOL_CLIENT = {
    "log in":"LOGIN_CODE",
    "throttle":"THROTTLE"
} # .. Add more commands if needed


PROTOCOL_SERVER = {
    "user logged in":"LOGGED_SUCCESSFULLY",
    "user couldnt login":"COULD_NOT_LOG",
    "invalid command":"INVALID_COMMAND",
} # ..  Add more commands if needed


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
    if len(str(num)) < LENGTH_FIELD_LENGTH: # create the message spaces and the message long(009,0100)
        num1 = LENGTH_FIELD_LENGTH - len(str(num))
        num = "0"*num1 + str(num)
    protocol_message += str(cmd) +DELIMITER + num + DELIMITER + str(data) # implement everything you did in the function to the protocol that send   DELIMITER = |
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



def build_and_send_message(conn, code, data): # code = command

	message = build_message(code,data) # create the message( will look like this: LOGIN           |0009|aaaa#bbbb)
	conn.send(message.encode()) # send to the server the message in the right format
	

def recv_message_and_parse(conn):
	full_msg = conn.recv(1024).decode() # gets the message from the server   need to be something like this for example "LOGIN           |0009|aaaa#bbbb"
	cmd, data = parse_message(full_msg) # split it to a tuple with the command and the data
	return cmd, data
	

def connect():
    """create a socket and connect to it(to receive and send messages)"""
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket,   socket.AF_INET = IP protocol,   socket.SOCK_STREAM = protocol TCP
    my_socket.connect((SERVER_IP,SERVER_PORT)) # connect to the socket(make it able to send messages in the socket)
    return my_socket


def error_and_exit(error_msg):
    print(error_msg)
    time.sleep(10)
    exit()


def build_send_recv_parse(conn,cmd,data):
	"""send the data it received(send the data,cmd(you need to put them when you call the function) with build_and_send_message
	receive data with recv_message_and_parse and returns the data,msg_code that it received"""
	build_and_send_message(conn,cmd,data) # build+send the message to the server
	msg_code,data2 = recv_message_and_parse(conn) # get the message from the server and parse it and put it in 2 variables
	return data2,msg_code



class Joystick():
    def __init__(self):
        self.button_size = (150,150)
        self.buttons = [
            movement_cube(screen_x//2-self.button_size[0]//2,screen_y//2-self.button_size[1]//2-screen_y//4,"forward",0.5,0.5,self.button_size),
            movement_cube(screen_x//2-self.button_size[0]//2,screen_y//2-self.button_size[1]//2+screen_y//4,"backward",-0.5,-0.5,self.button_size),

            movement_cube(screen_x//2-self.button_size[0]//2-screen_x//4,screen_y//2-self.button_size[1]//2,"left",-0.7,0.7,self.button_size),
            movement_cube(screen_x//2-self.button_size[0]//2+screen_x//4,screen_y//2-self.button_size[1]//2,"right",0.7,-0.7,self.button_size)
        ]
        self.right_wheels_throttle = 0
        self.left_wheels_throttle = 0

    def draw(self):
        for button in self.buttons:
            button.draw()
    def check_for_press(self):
        mouse = pygame.mouse.get_pos()
        pressed_mouse = pygame.mouse.get_pressed()
        pressed_on_one = False
        if pressed_mouse[0] == True:
            for button in self.buttons:
                if button.check_for_press(mouse):
                    self.left_wheels_throttle = button.left_wheels_throttle
                    self.right_wheels_throttle = button.right_wheels_throttle
                    pressed_on_one = True
                    break
        if pressed_on_one == False:
            self.right_wheels_throttle = 0
            self.left_wheels_throttle = 0

class movement_cube():
    def __init__(self,x,y,direction,left_throttle,right_throttle,size):
        self.x,self.y = x,y
        self.width,self.height = size
        self.button_rect = pygame.Rect(x,y,size[0],size[1])

        self.direction = direction
        self.left_wheels_throttle = left_throttle
        self.right_wheels_throttle = right_throttle
    def draw(self):
        pygame.draw.rect(window,(100,100,100),[self.x,self.y,self.width,self.height])
    def check_for_press(self,mouse):
        if self.button_rect.collidepoint(mouse):
            return True
        return False

joystick = Joystick()

def main():
    using_socket = connect()
    i = 0
    logged_in = False
    while i < 100:
        build_and_send_message(using_socket,"LOGIN_CODE","1234")
        command,data = recv_message_and_parse(using_socket)
        if command == PROTOCOL_SERVER["user logged in"]:
            logged_in = True
            break
        elif command == PROTOCOL_SERVER["user couldnt login"]:
            pass
        i += 1
    if logged_in == True:
        print("Connected to the server successfully")
    else:
        print(f"Couldn't connect to the server(tries:{i})")
        print("Possible problems:\nwrong code sent in a login message\nthe server is too busy\ninvalid protocol")
        exit()
    
    game_on = True
    clock = pygame.time.Clock()

    while game_on:
        clock.tick(60)
        window.fill((255,255,255))
        
        joystick.draw()
        joystick.check_for_press()
        #print(joystick.left_wheels_throttle,joystick.right_wheels_throttle)
        
        build_and_send_message(using_socket,PROTOCOL_CLIENT["throttle"],str(joystick.left_wheels_throttle)+","+str(joystick.right_wheels_throttle))
        #build_and_send_message(using_socket,PROTOCOL_CLIENT["left wheel throttle"],str(joystick.left_wheels_throttle))
        #build_and_send_message(using_socket,PROTOCOL_CLIENT["right wheel throttle"],str(joystick.right_wheels_throttle))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                game_on = False

        pygame.display.update()
if __name__ == '__main__':
    try:
        main()
    except ConnectionRefusedError: # error that raise when it cant speak/send_messages to the server because the server closed(closed = end the program)
        error_and_exit("An Error raised\nthe server closed before closing the client") # printing the error and exit() the program
    except ConnectionResetError:
        error_and_exit("An Error raised\nthe server closed before closing the client") # printing the error and exit() the program