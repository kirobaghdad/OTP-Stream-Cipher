import sys
import threading
import queue
import json

from colorama import Fore
from communication import CommunicationChannel
import tkinter as tk

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


def run_threads(input_file, output_file, chunk_size, LCG_params, DH_params, timeout=60):
    # Create fresh queues for each run
    sender_to_receiver_queue = queue.Queue()
    receiver_to_sender_queue = queue.Queue()

    
    # Create new thread instances
    sender = threading.Thread(
        target=sender_process,
        args=(sender_to_receiver_queue, receiver_to_sender_queue, LCG_params, DH_params, chunk_size, input_file)
    )
    receiver = threading.Thread(
        target=receiver_process,
        args=(receiver_to_sender_queue, sender_to_receiver_queue, LCG_params, DH_params, chunk_size, output_file)
    )
    
    try: 
        # Start threads
        sender.start()
        receiver.start()
        
        # Wait for threads to complete or timeout
        sender.join(timeout)
        receiver.join(timeout)
        
        
        # Ensure threads are fully terminated
        if sender.is_alive():
            print("Sender timed out, signaled to stop")
            sender.join()  # Wait for sender to fully terminate
        if receiver.is_alive():
            print("Receiver timed out, signaled to stop")
            receiver.join()  # Wait for receiver to fully terminate

    except KeyboardInterrupt:
        print(Fore.RED + "\n[main] Process interrupted by user")
    except Exception as e:
        print(Fore.RED + f"[main] Error: {str(e)}")
            

    return sender_to_receiver_queue, receiver_to_sender_queue
    

def main():
    args = sys.argv[1:]
    input_file = 'tests/input/default_in.txt'
    output_file = 'tests/output/default_out.txt'
    config_file = 'tests/config/default_config.json'

    i = 0
    
    GUI = False
    
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
        elif args[i] == '--g':
            GUI = True
            i += 1
        else:
            i += 1
            
            
    print(Fore.MAGENTA + f"[main] Input file: {input_file}")
    print(Fore.MAGENTA + f"[main] Output file: {output_file}")
    print(Fore.MAGENTA + f"[main] Config file: {config_file}")
    
    
    DH_params, LCG_params, chunk_size = read_params(config_file=config_file)

    print(Fore.MAGENTA + f"[main] DH_params: {DH_params['p']}, {DH_params['g']}, chunk_size: {chunk_size}, LCG_params: {LCG_params['m']}, {LCG_params['a']}, {LCG_params['c']}")

    if GUI == True:    
        
        def handle_enter(event):
            if event.state & 0x1: 
                sender_entry.insert(tk.INSERT, "\n")  # Insert a newline
                return "break" 
            else:
                send_message()  
                return "break"

        def send_message():
            message = sender_entry.get("1.0", tk.END).strip()
            # Save to file
            with open(input_file, "w") as file:
                file.write(message)
                
            sender_entry.delete("1.0", tk.END)
                
            run_threads(input_file,output_file,chunk_size, LCG_params, DH_params, 60)
            
            receiver_entry.config(state='normal')
            receiver_entry.delete("1.0", tk.END)
            
            with open(output_file, "r") as file:
                received_messge = file.read()
            
            receiver_entry.insert("1.0", received_messge)
            receiver_entry.config(state='disabled')
            

        # Create the main window
        root = tk.Tk()
        root.title("OTP Stream Cipher")

        # Create and place the title label
        title_label = tk.Label(root, text="OTP Stream Cipher", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Create the sender frame
        sender_frame = tk.Frame(root)
        sender_frame.grid(row=1, column=0, padx=10, pady=10)

        # Add label and entry to sender frame
        sender_label = tk.Label(sender_frame, text="Sender")
        sender_label.pack()
        
        sender_entry = tk.Text(sender_frame, width=30, height=5)
        # sender_entry = tk.Entry(sender_frame, width=30)
        sender_entry.pack()
        
        # Bind the Enter key to the send_message function   
        sender_entry.bind('<Return>', handle_enter)
        # Create the receiver frame
        receiver_frame = tk.Frame(root)
        receiver_frame.grid(row=1, column=1, padx=10, pady=10)

        # Add label and entry to receiver frame
        receiver_label = tk.Label(receiver_frame, text="Receiver")
        receiver_label.pack()
        receiver_entry = tk.Text(receiver_frame, width=30, height=5, state='disabled')
        receiver_entry.pack()

        # Create and place the send button
        send_button = tk.Button(root, text="Send Message", command=send_message)
        send_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        def close_window(event=None):
            root.destroy()  # Close the Tkinter window
        
        root.bind('<Escape>', close_window)

        # Start the main event loop
        root.mainloop()
    else:
        run_threads(input_file,output_file,chunk_size, LCG_params, DH_params, 60)
    
    
        print(Fore.WHITE)
            

if __name__ == "__main__":
    main()