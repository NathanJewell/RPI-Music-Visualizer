import asyncio
import websockets

host = '192.168.0.26'        # Symbolic name meaning all available interfaces
port = 12345     # Arbitrary non-privileged port

@asyncio.coroutine
def message():

@asyncio.coroutine
def connecter(websocket, path):
    global connected
    connected.append(websocket)

    try:
        yield from 

@asyncio.coroutine
def handler(websocket, path):

def start():
    s = websockets.serve(message, host, port)
    asyncio.get_event_loop().run_until_complete(s)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main___":
    start()

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
