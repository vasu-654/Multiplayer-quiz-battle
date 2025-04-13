import socket
import threading
import pandas as pd
import time

# Load the excel sheet
df = pd.read_excel('questions.xlsx')

# Function to handle client connections
def handle_client(conn, addr, client_name, questions_per_client, ready_clients, clients, answers, scores):
    print(f"New connection from {addr}, Client name: {client_name}")
    conn.send("Welcome to the quiz game!".encode())
    time.sleep(1)
    conn.send("Get ready, the game is about to start!".encode())
    time.sleep(1)

    ready_clients.append(client_name)

    while len(ready_clients) < len(clients):
        time.sleep(1)

    if len(ready_clients) == len(clients):
        conn.send("All clients are ready. Type 'start' to begin the quiz.".encode())
        while True:
            command = conn.recv(1024).decode().strip()
            if command.lower() == 'start':
                break

    total_score = 0
    questions_sent = set()
    for _ in range(questions_per_client):
        while True:
            question = df.sample()
            question_no = question['question no'].values[0]
            if question_no not in questions_sent:
                questions_sent.add(question_no)
                break

        question_text = question['question'].values[0]
        weightage = question['weightage'].values[0]
        answer = question['answer'].values[0]

        conn.send(f"Question {question_no}: {question_text}".encode())
        start_time = time.time()
        client_answer = conn.recv(1024).decode().strip()
        end_time = time.time()
        time_taken = end_time - start_time

        if client_answer.lower() == answer.lower():
            marks = weightage * (1 / time_taken)
            total_score += marks

        conn.send(f"Your score so far: {total_score}".encode())

    scores[client_name] = total_score

    answers[client_name] = True

    while len(answers) < len(clients):
        time.sleep(1)

    if len(answers) == len(clients):
        max_score_client = max(scores, key=scores.get)
        winner_message = f"The winner is {max_score_client} with a score of {scores[max_score_client]}"
        for client_conn, _, _ in clients:
            client_conn.send(winner_message.encode())

# Function to handle client connections
def start_server():
    HOST = socket.gethostname()
    PORT = 5555

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"Server is listening on {HOST}:{PORT}")

    clients = []
    ready_clients = []
    answers = {}
    scores = {}

    # Prompt user for the number of questions per client
    questions_per_client = int(input("Enter the number of questions per client: "))

    while True:
        conn, addr = server.accept()
        client_name = conn.recv(1024).decode().strip()
        clients.append((conn, addr, client_name))
        print(f"New client connected: {client_name}")
        print(f"Number of connected clients: {len(clients)}")

        conn.send(str(questions_per_client).encode())

        client_thread = threading.Thread(target=handle_client, args=(conn, addr, client_name, questions_per_client, ready_clients, clients, answers, scores))
        client_thread.start()

# Start the server
start_server()
