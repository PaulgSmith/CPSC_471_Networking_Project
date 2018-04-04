#!/usr/bin/env python3
""""FTP Protocols Server"""
__author__ = "Andrew De La Fuente and Paul Smith"
__copyright__ = "Copyright (C) 2018 Andrew De La Fuente and Paul Smith"
__license__ = "Public Domain"
__version__ = "1.0"

import argparse
import socket
import sys
import commands
import os

def send_data(sock, data):
    """
    Funtion formats the header to the message
    and sends the data.

    Args:
        param1: Name of the socket to use.
        param2: The information to be sent.

    Returns:
        TNothing.

    Raises:
        KeyError: None.
    """
    data_size = str(len(data))
    while len(data_size) < 10:
        data_size = "0" + data_size
    data = data_size + data
    data_sent = 0
    while data_sent != len(data):
        data_sent += sock.send(data[data_sent:])
        
def recvAll(sock, numBytes):
    """
    Function receives the data from a socket.

    Args:
        param1: Name of the socket to use.
        param2: The length of data to be received.

    Returns:
        The data received.

    Raises:
        KeyError: None.
    """
    recvBuff = ""
    tmpBuff = ""
    while len(recvBuff) < numBytes:
        tmpBuff =  sock.recv(numBytes)
        # The other side has closed the socket
        if not tmpBuff:
            break
        recvBuff += tmpBuff
    return recvBuff
    
def recv(sock):
    """
    Fuction receives receives header information before
    calling recvAll() to handle the data of the message. Passes
    any header information needed to receive the message to recvAll()

    Args:
        param1: Name of the socket to use.

    Returns:
        The full message received.

    Raises:
        KeyError: None.
    """
    data = ""
    file_size = 0	
    file_size_buff = ""
    file_size_buff = recvAll(sock, 10)
    file_size = int(file_size_buff)
    data = recvAll(sock, file_size)
    return data
    
def data_connection():
    """
    Function creates an ethereal socket

    Args:
        None.

    Returns:
        The object of an accepted socket connection.

    Raises:
        KeyError: None.
    """
    tmp_socket = socket.socket(socket.AF_INET ,socket.SOCK_STREAM)
    tmp_socket.bind(('',0))
    socket_number = str(tmp_socket.getsockname()[1])
    send_data(connection_socket,  socket_number)
    tmp_socket.listen(1)
    new_socket ,addr = tmp_socket.accept()
    return new_socket


parser = argparse.ArgumentParser(description="FTP server side")
parser.add_argument("port",  help="server port you wish to listen on")
args = parser.parse_args()
server_port = args.port

if server_port.isdigit():
    server_port = int(server_port)
else:
    print("The port {} is in the wrong format".format(server_port))
    sys.exit()
    
server_socket = socket.socket(socket.AF_INET ,socket.SOCK_STREAM)
server_socket.bind(('',server_port))
server_socket.listen(1)
print ('The server is ready to receive')
connection_socket ,addr = server_socket.accept()
print ('Connected by', addr)
data =''

while 1:
    try:
        exec_code = recv(connection_socket)
        if exec_code == "ls":
            tmp = ""
            data_socket = data_connection()
            for line in commands.getoutput('ls'):
                tmp += line
            send_data(data_socket, tmp)
            data_socket.close()
            
        if exec_code == "quit":
            break
            
        if exec_code == "get":
            data_socket = data_connection()
            file_name = recv(data_socket)
            while 1:
                try:
                    file = open(file_name, "r")
                except:
                    print("problem opening the file", file_name)
                try:
                    byte = file.read(1)
                    while byte != "":
                        send_data(data_socket, byte)
                        byte = file.read(1)
                finally:
                    data_socket.close()
                    file.close()
                    
        if exec_code == "put":
            data_socket = data_connection()
            file_name = recv(data_socket)
            try:
                if os.path.exists(file_name):
                    i = 1
                    num = "(" + str(i) + ")"
                    f_name, f_extension = os.path.splitext(file_name)
                    tmp = f_name
                    file_name = tmp + num + f_extension
                    while os.path.exists(file_name):
                        i += 1
                        num = "(" + str(i) + ")"
                        file_name = tmp + num + f_extension
                file = open(file_name, "w+")
                while 1:
                    tmp = recv(data_socket)
                    if not tmp:
                        break
                    file.write(tmp)
                file.close()
                print("File download is complete")
            except socket.error as socketerror:
                print("Error: ", socketerror)
            data_socket.close()
    except:
        pass
connection_socket.close()
print("Command Socket Closed")
