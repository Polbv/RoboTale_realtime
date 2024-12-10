import socket

client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
HOST="192.168.218.63"
PORT=12345
client_socket.connect((HOST,PORT))

message="hello"
client_socket.send(message.encode('utf-8'))
response=client_socket.recv(1024).decode('utf-8')
print(response)
client_socket.close()