import socket

host = '192.168.0.26'        # Symbolic name meaning all available interfaces
port = 12345     # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))

print(host , port)
s.listen(1)
conn, addr = s.accept()
print('Connected by', addr)
while True:
    try:
        data = conn.recv(1024).decode();

        if not data: break

        print("Client Says: "+ data)
        data = str(data);
        data =
        conn.send(data.encode())

        if data == "END":
            conn.close();d

    except socket.error:
        print("Error Occured.")
        break
