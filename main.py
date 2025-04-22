import sys
import threading
import queue
from communication import CommunicationChannel
from key_exchange import generate_DH_params

def sender_process(send_queue,receive_queue,p,g,input_file,config_file):
    try:
        with open(input_file, 'r') as f:
            message = f.read()
            if not message:
                raise ValueError("Input file is empty")
        channel = CommunicationChannel('sender',send_queue,receive_queue,p,g,config_file)
        if not channel.establish_connection():
            print("[sender] Failed to establish connection")
            return
        if channel.send_message(message):
            print("[sender] Successful message transmission")
        channel.close()
        
    except FileNotFoundError:
        raise FileNotFoundError(f"[sender] Input file {input_file} not found")
    except Exception as e:
        print(f"[sender] Error: {str(e)}")

def receiver_process(send_queue,receive_queue,p,g,output_file,config_file):
    try:
        channel = CommunicationChannel('receiver',send_queue,receive_queue,p,g,config_file)
        if not channel.establish_connection():
            print("[receiver] Failed to establish connection")
            return
        decrypted_message = channel.receive_message()
        with open(output_file, 'w') as f:
            f.write(decrypted_message)
        channel.close()
        
    except Exception as e:
        print(f"[receiver] Error: {str(e)}")

def main():
    args = sys.argv[1:]
    print(args)
    input_file = 'tests/input/default_in.txt'
    output_file = 'tests/output/default_out.txt'
    config_file = 'tests/config/default_config.json'

    i = 0
    while i < len(args):
        if args[i] == '--i' and i + 1 < len(args):
            input_file = args[i + 1]
            i += 2
        elif args[i] == '--o' and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        elif args[i] == '--c' and i + 1 < len(args):
            config_file = args[i + 1]
            i += 2
        else:
            i += 1
    print(f"[main] Input file: {input_file}")
    print(f"[main] Output file: {output_file}")
    print(f"[main] Config file: {config_file}")
    sender_to_receiver_queue = queue.Queue()
    receiver_to_sender_queue = queue.Queue()
    p, g = generate_DH_params(config_file=config_file)
    sender = threading.Thread(target=sender_process, args=(sender_to_receiver_queue,receiver_to_sender_queue,p,g,input_file,config_file))
    receiver = threading.Thread(target=receiver_process, args=(receiver_to_sender_queue,sender_to_receiver_queue,p,g,output_file,config_file))
    
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
