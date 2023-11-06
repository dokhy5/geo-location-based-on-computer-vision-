import collections
import os
import socket
import threading
import pickle
from datetime import datetime 
from new import object_detection
import time 

max_num_cars = 20
cars = collections.OrderedDict()
founded_car_details = []

def search_car(car):
    try:
     
            if not car:
                raise ValueError("At least one car license plate must be provided")
            if car[1] in cars:
                print(f"{car[1]} found!")
                return cars[car[1]]
            else :
                print (f"{car[1]} not found")

    except ValueError as e:
        print(f"Error: {e}")

    except TypeError as e:
        print(f"Error: {e}")

    return None

class Client:
    lock = threading.Lock()  # Define a lock as a class variable
    
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def receive_messages(self):
        try:
            while True:  # Run in an infinite loop to keep receiving messages
                message = self.client_socket.recv(2048)
                if not message:
                    break  # Exit the loop if an empty message is received
                massage_spit = pickle.loads(message)
                car_part = massage_spit.split()
                if car_part:
                    threading.Thread(target=process_search, args=(car_part,)).start()

        except ConnectionResetError:
            print("Connection with the server closed.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")


    def send_dictionary(self, data):
        serialized_data = pickle.dumps(data)
        self.client_socket.sendall(serialized_data)


    def connect_to_server(self, username):
        try:
            self.client_socket.connect((self.ip, self.port))
            print(f"Connected to the server {self.ip}:{self.port}")
            self.client_socket.send(username.encode())
            
            threading.Thread(target=self.receive_messages).start()
        except ConnectionRefusedError:
            print("Unable to connect to the server.")
        except KeyboardInterrupt:
            print("Exiting...")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def main(self, username):
        self.connect_to_server(username)
        

def send_dictionary_to_server(data):
    client = Client('172.20.10.2', 8000)
    username = 'camera'
    client.main(username)
    client.send_dictionary(data)

def process_search(car):
    founded_car = search_car(car)
    print(founded_car)
    if founded_car:
        with Client.lock:  # Use the class lock
            founded_car_details.append(founded_car)
            print(f"Sending {founded_car} to the server...")
            send_dictionary_to_server(founded_car_details)

def add_car(car_license_plate):
    nowtime = datetime.now()
    try:
        if not isinstance(car_license_plate, str):
            raise TypeError("Car license plate should be a string")
        if len(cars) >= max_num_cars:
            cars.popitem()

        if car_license_plate in cars:
            cars[car_license_plate].append([car_license_plate, 2, nowtime.strftime("%Y-%m-%d %H:%M:%S")])
        else:
            cars[car_license_plate] = [[car_license_plate, 2, nowtime.strftime("%Y-%m-%d %H:%M:%S")]]

    except TypeError as e:
        print(f"Error: {e}")

def convert_arabic_letters(string):
    arabic_letters = {
        'alf': 'ا',
        'baa': "ب",
        'ta': 'ت',
        'tha': 'ث',
        'geem': 'ج',
        'haa':'ح',
        'ghaa': 'خ',
        'dal': 'د',
        'zal': 'ذ',
        'raa': 'ر',
        'zeen': 'ز',
        'sin': 'س',
        'shin': 'ش',
        'sad': 'ص',
        'daad': 'ض',
        'taa': 'ط',
        'thaa': 'ظ',
        'ain': 'ع',
        'ghin': 'غ',
        'faa': 'ف',
        'kaaf': 'ق',
        'kaf': 'ك',
        'lam': 'ل',
        'meem': 'م',
        'non': 'ن',
        'ha': 'ه',
        'waw': 'و',
        'yaa': 'ي'
    }
    
    words = string.split()
    converted_string = ""
    
    for word in words:
        if word in arabic_letters:
            converted_string += arabic_letters[word]
        else:
            converted_string += word
    
    return converted_string

if __name__ == "__main__":
    with open("Highest.txt", 'r') as file:
        file_content = file.read()
    
    car_plate = convert_arabic_letters(file_content)
    
    threading.Thread(target=add_car, args=(car_plate,)).start()
    time.sleep(5)  # Wait for add_car to populate the cars dictionary
    threading.Thread(target=send_dictionary_to_server, args=(founded_car_details,)).start()


    print(cars)