import sys
import threading
import queue
from communication import CommunicationChannel

def sender_process(send_queue,recieve_queue):
    try:
        with open('tests/input/in_1.txt', 'r') as f:
            message = f.read()
            if not message:
                raise ValueError("Input file is empty")
        channel = CommunicationChannel('sender',send_queue,recieve_queue,config_file="tests/config/config_1.json")
        if not channel.establish_connection():
            print("[sender] Failed to establish connection")
            return
        if channel.send_message(message):
            print("[sender] Message transmission successful")
        channel.close()
        
    except FileNotFoundError:
        message = "Hello! This is a test message for secure transmission."
        with open('tests/input/in_1.txt', 'w') as f:
            f.write(message)
        print("[main] Created input.txt with sample message")
    except Exception as e:
        print(f"[sender] Error: {str(e)}")

def receiver_process(send_queue,recieve_queue):
    try:
        channel = CommunicationChannel('receiver',send_queue,recieve_queue,config_file="tests/config/config_1.json")
        if not channel.establish_connection():
            print("[receiver] Failed to establish connection")
            return
        decrypted_message = channel.receive_message()
        print("[receiver] Message received and decrypted")
        with open('tests/output/out_1.txt', 'w') as f:
            f.write(decrypted_message)
        channel.close()
        
    except Exception as e:
        print(f"[receiver] Error: {str(e)}")

def main():
    print("Starting secure communication system...")
    args = sys.argv[1:]
    print(args)
    sender_to_receiver_queue = queue.Queue()
    receiver_to_sender_queue = queue.Queue()
    sender = threading.Thread(target=sender_process, args=(sender_to_receiver_queue,receiver_to_sender_queue))
    receiver = threading.Thread(target=receiver_process, args=(receiver_to_sender_queue,sender_to_receiver_queue))
    
    try:
        sender.start()
        receiver.start()
        
        timeout = 60
        sender.join(timeout)
        receiver.join(timeout)
        
        if sender.is_alive() or receiver.is_alive():
            print("[main] Error: Communication timeout")
            return
            
    except KeyboardInterrupt:
        print("\n[main] Process interrupted by user")
    except Exception as e:
        print(f"[main] Error: {str(e)}")

if __name__ == "__main__":
    main()
