import sys
import threading
import queue
import json

from colorama import Fore
from communication import CommunicationChannel

def read_params(config_file):
    try:
        # Open and read the JSON file
        with open(config_file, 'r') as file:
            try:
                config_data = json.load(file)
            except json.JSONDecodeError:
                raise ValueError(f"Error: File '{config_file}' is empty or contains invalid JSON")
            params = config_data.get("DH_params", {})
            params['chunk_size'] = config_data.get("chunk_size")
            params['LCG'] = config_data.get("LCG_params", {})
        
        # Extract parameters
        p_hex_strings  = params.get('p_value')
        g_hex_strings = params.get("g_value")
        p_hex_bytes = [int(h, 16) for h in p_hex_strings]
        g_hex_bytes = [int(h, 16) for h in g_hex_strings]
        
        p_value = int.from_bytes(p_hex_bytes, byteorder='big')
        g_value = int.from_bytes(g_hex_bytes, byteorder='big')
        chunk_size_value = params.get('chunk_size')
        # Basic validation
        if not all(isinstance(x, (int, float)) for x in [p_value, g_value]):
            raise ValueError("DH params. must be numbers")
        
        if p_value <= 0 or g_value <= 0:
            raise ValueError("DH Params. must be positive")
        

        return {'p': p_value, 'g': g_value}, params.get('LCG', {}), chunk_size_value

    except FileNotFoundError:
        print(Fore.RED + f"Error: File '{config_file}' not found")
        raise
    except json.JSONDecodeError:
        print(Fore.RED + f"Error: File '{config_file}' contains invalid JSON")
        raise
    except KeyError as e:
        print(Fore.RED + f"Error: Missing parameter {e} in JSON file")
        raise

def sender_process(send_queue,receive_queue,LCG_params, DH_params, chunk_size,input_file):
    try:
        with open(input_file, 'r') as f:
            message = f.read()
            if not message:
                raise ValueError("Input file is empty")
        channel = CommunicationChannel('sender',send_queue,receive_queue,LCG_params, DH_params, chunk_size, Fore.BLUE)
        if not channel.establish_connection():
            print(Fore.RED + "[sender] Failed to establish connection")
            return
        if channel.send_message(message):
            print(Fore.BLUE + "[sender] Successful message transmission")
        channel.close()
        
    except FileNotFoundError:
        raise FileNotFoundError(f"[sender] Input file {input_file} not found")
    except Exception as e:
        print(Fore.RED + f"[sender] Error: {str(e)}")

def receiver_process(send_queue,receive_queue,LCG_params, DH_params, chunk_size,output_file):
    try:
        channel = CommunicationChannel('receiver',send_queue,receive_queue,LCG_params, DH_params, chunk_size, Fore.YELLOW)
        if not channel.establish_connection():
            print(Fore.RED + "[receiver] Failed to establish connection")
            return
        decrypted_message = channel.receive_message()
        with open(output_file, 'w') as f:
            f.write(decrypted_message)
        channel.close()
        
    except Exception as e:
        print(Fore.RED + f"[receiver] Error: {str(e)}")

def main():
    args = sys.argv[1:]
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
    print(Fore.WHITE + f"[main] Input file: {input_file}")
    print(Fore.WHITE + f"[main] Output file: {output_file}")
    print(Fore.WHITE + f"[main] Config file: {config_file}")
    
    sender_to_receiver_queue = queue.Queue()
    receiver_to_sender_queue = queue.Queue()
    
    DH_params, LCG_params, chunk_size = read_params(config_file=config_file)

    print(Fore.MAGENTA + f"[main] DH_params: {DH_params['p']}, {DH_params['g']}, chunk_size: {chunk_size}, LCG_params: {LCG_params['m']}, {LCG_params['a']}, {LCG_params['c']}")

    sender = threading.Thread(target=sender_process, args=(sender_to_receiver_queue,receiver_to_sender_queue,LCG_params, DH_params, chunk_size, input_file))

    receiver = threading.Thread(target=receiver_process, args=(receiver_to_sender_queue,sender_to_receiver_queue,LCG_params, DH_params, chunk_size,output_file))
    
    try:
        receiver.start()
        sender.start()
        
        timeout = 60
        sender.join(timeout)
        receiver.join(timeout)
        
        if sender.is_alive() or receiver.is_alive():
            print(Fore.RED + "[main] Error: Communication timeout")
            return
            
    except KeyboardInterrupt:
        print(Fore.RED + "\n[main] Process interrupted by user")
    except Exception as e:
        print(Fore.RED + f"[main] Error: {str(e)}")

if __name__ == "__main__":
    main()