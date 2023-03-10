from tkinter import *
from gui import *
import socket
import os
import sys
import select
import connection

# '''
# Database:login
# Tables: users (USERNAME varchar(100), PASSWORD varchar(100))
# 		messages (ID int primary key not nullable, MESSAGES varchar(300), TIMEST timestamp default:CURRENT_TIMESTAMP)
# '''

RECV_BUFFER = 4096
SOCKET = []  # list of connected sockets


# Function to connect socket to server
def connect_to_server(gui_obj, server_ip, server_port, username, password):
	# #Object to connect to database
	# conObj = connection.Connection()
	#
	# #query to check if entered username and password are correct
	# try:
	# 	query = "SELECT * FROM users WHERE USERNAME='%s' AND PASSWORD='%s';" % (username,password)
	# 	stat = conObj.cur.execute(query)
	#
	# except:
	# 	print("Query failed")
	#
	# #stat = 1 if query is successful, otherwise 0
	# conObj.conn.close()
	
	try:
		# Connect the client socket to server
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket.connect((server_ip, server_port))

		SOCKET.append(client_socket)
		return [1, client_socket]
	except Exception:
		# Server is offline
		return[-1, 0]


# Function to receive messages and also modifies userlist
def recv_msg(gui_obj, sock):
	data = sock.recv(RECV_BUFFER)
	if not data:
		# Broken socket
		gui_obj.disconnect()
	else:
		data = data.decode()
		gui_obj.display("\n" + data)

		# New user
		if "entered" in data:
			print(data.split(" "))
			gui_obj.add_user(data.split(" ")[0:2])

		# User exited
		if "exited" in data:
			gui_obj.remove_user(tuple(data.split(" ")[0:2]))


# Function runs on a separate thread. Processes active socket.
def socket_handler(gui_obj, sock):
	try:
		while 1:
			socket_list = [sock]

			read, write, error = select.select(socket_list, [], [], 0)

			for s in read:
				if s == sock:
					recv_msg(gui_obj, s)

	except KeyboardInterrupt:
		sys.exit()
	except Exception:
		gui_obj.display("\nDisconnected.\n")


def send_msg(server_socket, msg):
	server_socket.send(bytes(msg, 'UTF-8'))
	# conObj = connection.Connection()
	#
	# #query to enter messages into table. only 10 messages can be stored in the table
	# try:
	# 	query = "REPLACE INTO messages(ID,MESSAGES,TIMEST) SELECT MOD(ID+1,10),'%s',NOW() FROM messages ORDER BY TIMEST DESC LIMIT 1;" % (msg)
	# 	stat = conObj.cur.execute(query)
	# 	print("msg insert:",stat)
	# 	conObj.conn.commit()
	#
	# except:
	# 	print("Message query failed")
	#
	# #stat = 1 if query is successful, otherwise 0
	# conObj.conn.close()


# Executes only when the current file is run explicitly and not when imported.
if __name__ == "__main__":

	root = Tk()
	chat = ChatGui(root)
	# conObj = connection.Connection()
	#
	# #default message stored in messages table when user enters
	# try:
	# 	query = "REPLACE INTO messages(ID,MESSAGES,TIMEST) VALUES(1,'DEFAULT MESSAGE',NOW());"
	# 	stat = conObj.cur.execute(query)
	# 	print("msg insert:",stat)
	# 	conObj.conn.commit()
	#
	# except:
	# 	print("Message query failed")
	#
	# conObj.conn.close()
	chat.mainloop()

	
