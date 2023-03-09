from tkinter import *
from _thread import start_new_thread
import client as user
from client import *

HOST = 'localhost'
PORT = 10101
LARGE_FONT = ("VERDANA", 12)
NORM_FONT = ("VERDANA", 8)


class ChatGui(Frame):
	def __init__(self, master):

		#Frame has to be initialized explicitly
		Frame.__init__(self, master)
		self.grid(sticky=W+E+N+S)
		self.master.title("Chat")

		self.Frame1 = Frame(master)
		self.Frame1.grid(row=0, column=0, rowspan=3, columnspan=1, sticky=W+E+N+S)
		self.Frame2 = Frame(master)
		self.Frame2.grid(row=3, column=0, rowspan=3, columnspan=1, sticky=W+E+N+S)
		self.Frame3 = Frame(master)
		self.Frame3.grid(row=0, column=1, rowspan=5, columnspan=3, sticky=W+E+N+S)
		self.Frame4 = Frame(master)
		self.Frame4.grid(row=5, column=1, rowspan=1, columnspan=3, sticky=W+E+N+S)

		self.init_window()

	def init_window(self):
		# Frame for list of users
		self.gui_userlist = Listbox(self.Frame1)
		self.gui_userlist.pack(side="left", expand=1, fill="both")
		self.userlist_scrollbar = Scrollbar(self.Frame1, orient="vertical")
		self.userlist_scrollbar.config(command=self.gui_userlist.yview)
		self.userlist_scrollbar.pack(side="left", fill="both")
		self.gui_userlist.config(yscrollcommand=self.userlist_scrollbar.set)

		# Frame for login fields
		self.user_label=Label(self.Frame2, text="Username")
		self.pass_label=Label(self.Frame2, text="Password")
		self.username_text = Entry(self.Frame2)
		self.password_text = Entry(self.Frame2)
		self.connect = Button(self.Frame2,text="Connect", command=self.connect)
		self.user_label.grid(row=0, column=0)
		self.pass_label.grid(row=1, column=0)
		self.username_text.grid(row=0, column=1, columnspan=2)
		self.password_text.grid(row=1, column=1, columnspan=2)
		self.connect.grid(row=3, column=1)

		# Frame for chat window
		self.chat = Text(self.Frame3,font=NORM_FONT)
		self.chat.pack(side="left", expand=1, fill="both")
		self.chat_scrollbar = Scrollbar(self.Frame3, orient="vertical")
		self.chat_scrollbar.config(command=self.chat.yview)
		self.chat_scrollbar.pack(side="left", fill="both")
		self.chat.config(yscrollcommand=self.chat_scrollbar.set)

		# Frame for entering messsages
		self.msg = Entry(self.Frame4)
		self.msg.bind("<Return>", self.send_msg)
		self.msg.pack(side="left", expand=1, fill="both")

	# Function to check if the login credentials are valid
	def connect(self):
		self.username = self.username_text.get()
		self.password = self.password_text.get()
	
		# connection[0] is 1 when username and password are valid, 0 otherwise
		# connection[1] is the socket object created
		connection = user.connect_to_server(self, HOST, PORT, self.username, self.password)

		if connection[0] == 1:
			# Changes the button to disconnect
			self.connect.config(text="Disconnect", command=self.disconnect)
			self.SOCKET = connection[1]

			self.display("\nConnected to " + HOST + " at port: " + str(PORT) + "\n")

			try:
				# Get the existing users as a string separated by '@'
				data = self.SOCKET.recv(RECV_BUFFER)
				users = data.decode().split("@")

				for u in users:
					self.add_user(u)
				# Start a new thread. GUI runs on main thread and each client runs on separate threads
				start_new_thread(user.socket_handler, (self, self.SOCKET))
			except:
				pass

		elif connection[0] == 0:
			# Error dialog box
			popup = Toplevel()
			popup.title("ERROR!")
			msg = Message(popup,text="INVALID CREDENTIALS!", width=400, font=LARGE_FONT)
			msg.place(x=10, y=50)
			btn = Button(popup,text="Dismiss", command=popup.destroy)
			btn.place(x=100 ,y=100)
			popup.geometry("300x200")

		else:
			self.display("\nServer is offline\n")
			self.disconnect()

	def disconnect(self):
		sys.exit()

	def send_msg(self,event):
		try:
			# Get the address of the sender socket
			self.sender_addr = self.SOCKET.getsockname()
			# print(self.sender_addr)
			user.send_msg(self.SOCKET,self.msg.get())
			# self.display(str(self.sender_addr) + " " + self.msg.get())
			self.display("\n<YOU>" + " :: " + self.msg.get())
			# Delete message from the textbox once it is sent
			self.msg.delete(0, END)
		except:
			self.display("\nNo connection!\n")

	# Function to add users to the userlist
	def add_user(self, user):
		self.gui_userlist.insert(0, user)

	# Function to remove users from the user list
	def remove_user(self,user):
		i = 0
		# print("User:",user)
		for name in self.gui_userlist.get(0, END):
			# print("Name:",name)
			if name == user:
				self.gui_userlist.delete(i,i)
				break
			i += 1 

	# Function to display messages in chat window
	def display(self, msg):
		self.chat.configure(state='normal')
		self.chat.insert(END, msg+"\n")
		self.chat.configure(state='disabled')

		if msg.strip() == 'Disconnected.':
			self.disconnect()
