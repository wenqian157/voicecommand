import socket

# server
HOST = "127.0.0.1"
PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

print(f"Server listening on {HOST}:{PORT}...")
try:
    while True:
        data, addr = sock.recvfrom(1024)
        if not data:
            break
        command = data.decode("utf-8")
        print(f"Received command: {command}")
        # Here you can add code to send the command to the robot or process it as needed
except KeyboardInterrupt:
    print("\nStopped.")