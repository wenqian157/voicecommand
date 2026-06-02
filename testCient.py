import socket


HOST = "127.0.0.1"
PORT = 5006

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    command = input("press enter to send next command..")
    if command == "n":
        sock.sendto("next".encode("utf-8"), (HOST, PORT))
    elif command == "q":
        break