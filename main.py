import threading
import queue
from communication import CommunicationChannel

def sender_process(send_queue,recieve_queue):
    try:
        with open('input.txt', 'r') as f:
            message = f.read()
            if not message:
                raise ValueError("Input file is empty")
        channel = CommunicationChannel('sender',send_queue,recieve_queue)
        if not channel.establish_connection():
            print("[Sender] Failed to establish connection")
            return
        if channel.send_message(message):
            print("[Sender] Message transmission successful")
        channel.close()
        
    except FileNotFoundError:
        message = "Hello! This is a test message for secure transmission."
        with open('input.txt', 'w') as f:
            f.write(message)
        print("[Main] Created input.txt with sample message")
    except Exception as e:
        print(f"[Sender] Error: {str(e)}")

def receiver_process(send_queue,recieve_queue):
    try:
        channel = CommunicationChannel('receiver',send_queue,recieve_queue)
        if not channel.establish_connection():
            print("[Receiver] Failed to establish connection")
            return
        decrypted_message = channel.receive_message()
        print("[Receiver] Message received and decrypted")
        with open('output.txt', 'w') as f:
            f.write(decrypted_message)
        channel.close()
        
    except Exception as e:
        print(f"[Receiver] Error: {str(e)}")

def main():
    print("Starting secure communication system...")
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
            print("[Main] Error: Communication timeout")
            return
            
        
    except KeyboardInterrupt:
        print("\n[Main] Process interrupted by user")
    except Exception as e:
        print(f"[Main] Error: {str(e)}")

if __name__ == "__main__":
    main()
