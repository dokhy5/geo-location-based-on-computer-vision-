from socket import *
import threading
import time

ip = '192.168.1.13'
port = 8000

# Function to receive messages from the server
def receive_messages(client):
    while True:
        try:
            message = client.recv(2048).decode()
            if message != '':
                print(message)
        except ConnectionResetError:
            print("Connection with the server closed.")
            break


# Function to send messages to the server
def send_messages(client):
    while True:
        try:
            car_plate = input("Enter the car license number: ")
            
            print('_'*89)
            if car_plate != '':
                client.send(car_plate.encode())
            else:
                print("The message is empty.")
        except ConnectionResetError:
            print("Connection with the server closed.")
            break


def connect_to_server(username):
    while True:
        client = socket(AF_INET, SOCK_STREAM)
        try:
            client.connect((ip, port))
            print(f"Connected to the server {ip}:{port}")
            client.send(username.encode())
            threading.Thread(target=receive_messages, args=(client,)).start()
            send_messages(client)
        except ConnectionRefusedError:
            print("Unable to connect to the server.")
            print("Retrying in 10 minutes...")
            time.sleep(600)  # Delay for 10 minutes (600 seconds)
        except KeyboardInterrupt:
            print("Exiting...")
            client.close()
            break
        finally:
            client.close()


def main():
    try:
        username = input("Enter your username: ")
        connect_to_server(username)
    except KeyboardInterrupt:
        print("Exiting...")


if __name__ == "__main__":
    main()