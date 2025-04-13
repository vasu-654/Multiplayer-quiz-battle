import socket

def start_client():
    HOST = socket.gethostname()
    PORT = 5555

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    client_name = input("Enter your name: ")
    client.send(client_name.encode())

    print(client.recv(1024).decode())
    print(client.recv(1024).decode())

    while True:
        question = client.recv(1024).decode()
        if not question:
            break
        print(question)
        answer = input("Your answer: ")
        client.send(answer.encode())
        response = client.recv(1024).decode()
        print(response)

    client.close()

# Start the client
start_client()
