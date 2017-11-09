#!/usr/bin/python3

from socket import *
import subprocess
import os
import signal

CMD_NONE = 0
CMD_XMIT_APP_REQ = 1
CMD_RUN_REQ = 2
CMD_STOP_REQ = 3
CMD_XMIT_APP_RES = 4
CMD_RUN_RES = 5
CMD_STOP_RES = 6

VAL_SUCCESS = 1
VAL_FAILED = 0

def getCommandFromData(data) :
	command = int.from_bytes(data[:1], "big")
	value = int.from_bytes(data[1:5], "big")
	return (command, value)

def sendPacketHeader(socket, command, value) :
	bCommand = command.to_bytes(1, "big")
	bValue = value.to_bytes(4, "big")
	socket.send(bCommand + bValue)

def runApplication(socket) :
	process = subprocess.Popen("./PLC_APP")
	if socket :
		sendPacketHeader(socket, CMD_RUN_RES, VAL_SUCCESS)
	return process

def stopApplication(process, socket) :
	process.send_signal(signal.SIGINT)
	if socket :
		sendPacketHeader(socket, CMD_STOP_RES, VAL_SUCCESS)

ADDR = ("", 3000)

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(ADDR)
serverSocket.listen(5)

while True :
	(clientSocket, addrInfo) = serverSocket.accept()
	command = CMD_NONE
	file = None
	recvLength = 0
	appLength = 0
	process = None

	while True :
		data = clientSocket.recv(1023)

		if not data :
			print("disconnected!!")
			clientSocket.close()
			if process :
				stopApplication(process, None)
			break

		if command != CMD_NONE :
			if command == CMD_XMIT_APP_REQ :
				print("APP data!!")
				file.write(data)
				recvLength = recvLength + len(data)
				if recvLength >= appLength :
					print("APP data finished!!")
					command = CMD_NONE
					file.close()
					os.chmod("PLC_APP", 755)
					sendPacketHeader(clientSocket, CMD_XMIT_APP_RES, VAL_SUCCESS)
		else :
			(command, value) = getCommandFromData(data)
			if command == CMD_XMIT_APP_REQ :
				print("APP!!")
				file = open("PLC_APP", "wb")
				recvLength = 0
				appLength = value
			elif command == CMD_RUN_REQ :
				print("run!!")
				process = runApplication(clientSocket)
				command = CMD_NONE
			elif command == CMD_STOP_REQ :
				print("stop!!")
				stopApplication(process, clientSocket)
				process = None
				command = CMD_NONE

