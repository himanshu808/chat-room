import sys
import socket
import select

HOST = 'localhost'
# HOST = ''
PORT = 10101
SOCKET_LIST = {}  # Dictionary socket addresses as keys and socket objects as values
RECV_BUFFER = 4096


def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)

    # Server socket has the key 'Host'
    SOCKET_LIST['Host'] = server_socket

    print("\nChat running on " + HOST + " on port: " + str(PORT))

    while 1:
        try:
            all_sockets = get_all_sockets()
            ready_to_read, ready_to_write, in_error = select.select(all_sockets, [], [], 0)

            for sock in ready_to_read:
                if sock == server_socket:
                    add_user(server_socket)
                else:
                    recv_msg(server_socket, sock)
        except KeyboardInterrupt:
            print("Keyboard interrupt")
            sys.exit()
        except Exception:
            print("Server Error")
            sys.exit()


# Function to get all connected socket objects
def get_all_sockets():
    all_sockets = [sys.stdin]

    for addr, sock in SOCKET_LIST.items():
        all_sockets.append(sock)
    return all_sockets


# Function to add a new user
def add_user(server_socket):
    new_socket, new_addr = server_socket.accept()
    new_socket.settimeout(30)
    SOCKET_LIST[new_addr] = new_socket

    all_users = ""
    for addr, sock in SOCKET_LIST.items():
        # Separate each user address by '@'
        all_users += "@" + str(addr)
    new_socket.send(bytes(all_users, 'UTF-8'))

    msg = str(new_addr) + " entered."
    print("\n"+msg)
    print_users()

    send_to_all(server_socket, new_socket, str(new_addr), msg)


def recv_msg(server_socket, sock):
    str_addr = ""
    addr = ""
    try:
        data = sock.recv(RECV_BUFFER).decode()
        # str_addr: address tuple as a string
        str_addr, addr = get_addr(sock)
        if data:
            msg = str_addr + " :: " + data
            print(msg)
            send_to_all(server_socket, sock, addr, msg)
        # broken socket
        else:
            print("removing user", addr)
            remove_user(addr)
    except Exception:
        msg = str_addr + " disconnected"
        print("\n"+msg)
        send_to_all(server_socket, sock, addr, msg)


# Function to send message to all connected sockets
def send_to_all(server_socket, sender_socket, sender_addr, msg):
    for addr, sock in SOCKET_LIST.items():
        if sock != server_socket and sock != sender_socket:
            try:
                sock.send(bytes(msg, 'UTF-8'))
            except Exception:
                sock.close()
               

# Function to remove a socket
def remove_user(user_addr):
    try:
        SOCKET_LIST[user_addr].close()
        del SOCKET_LIST[user_addr]

        msg = str(user_addr) + " exited."
        print("\n"+msg)
        print_users()
        send_to_all(SOCKET_LIST['Host'], SOCKET_LIST['Host'], 'Host', msg)
    except Exception:
        print("\nNo such address in list")


# Function to get the address of the socket
def get_addr(user):
    user_addr = ''
    temp_addr = ''
    for addr, sock in SOCKET_LIST.items():
        if sock == user:
            user_addr = str(addr)
            temp_addr = addr
    
    return user_addr, temp_addr
    

# Function to print all connected users
def print_users():
    all_users = "\nUSERS: ["
    for user, sock in SOCKET_LIST.items():
        all_users += str(user)+","
    print(all_users[:-1]+"]")


# Execute only when this file is run explicitly
if __name__ == "__main__":
    server()
