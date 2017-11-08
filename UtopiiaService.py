#!/usr/bin/python3

from socket import *
import subprocess
import os
import signal

ADDR = ("", 3000)

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(ADDR)
serverSocket.listen(5)

while True :
	(clientSocket, addrInfo) = serverSocket.accept()
	data = clientSocket.recv(1024)
	app_length = int(data)
	print("app length : " + str(app_length))

	recv_length = 0
	file = open("PLC_APP", "wb")
	os.chmod("PLC_APP", 755)
	while recv_length < app_length :
		app = clientSocket.recv(app_length - recv_length)
		print(len(app))
		file.write(app)
		recv_length = recv_length + len(app)
	file.close()

	data = clientSocket.recv(1024).decode("utf-8")
	if data == "run" :
		print("run!!")
		p = subprocess.Popen("./PLC_APP")

	data = clientSocket.recv(1024).decode("utf-8")
	if data == "stop" :
		print("stop!!")
		p.send_signal(signal.SIGINT)

	clientSocket.close()

