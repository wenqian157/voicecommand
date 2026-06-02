import socket

# server
HOST = "127.0.0.1"
PORT = 5006

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

print(f"Server listening on {HOST}:{PORT}...")
while True:
    data, addr = sock.recvfrom(1024)
    if not data:
        break
    command = data.decode("utf-8")
    match command:
        case "next":
            print(f"Received command: {command}")
        case "stop":
            sock.close()
            print("\nSocket Closed.")
            break