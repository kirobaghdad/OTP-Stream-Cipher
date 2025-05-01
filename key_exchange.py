import random
import json

from colorama import Fore

def is_prime(n):
    if n < 2:
        return False
    
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
        
    return True

def generate_prime(min_value, max_value):
    prime = random.randint(min_value, max_value)
    
    while not is_prime(prime):
        prime = random.randint(min_value, max_value)
    
    return prime


def read_DH_params(config_file):
    try:
        # Open and read the JSON file
        with open(config_file, 'r') as file:
            params = json.load(file).get("DH_params")
        
        # Extract parameters
        p_hex_strings  = params.get('p_value')
        g_hex_strings = params.get("g_value")
        p_hex_bytes = [int(h, 16) for h in p_hex_strings]
        g_hex_bytes = [int(h, 16) for h in g_hex_strings]
        
        p_value = int.from_bytes(p_hex_bytes, byteorder='big')
        g_value = int.from_bytes(g_hex_bytes, byteorder='big')
        
        # Basic validation
        if not all(isinstance(x, (int, float)) for x in [p_value, g_value]):
            raise ValueError("DH params. must be numbers")
        
        if p_value <= 0 or g_value <= 0:
            raise ValueError("DH Params. must be positive")

        return p_value, g_value

    except FileNotFoundError:
        print(Fore.RED + f"Error: File '{config_file}' not found")
        raise
    except json.JSONDecodeError:
        print(Fore.RED + f"Error: File '{config_file}' contains invalid JSON")
        raise
    except KeyError as e:
        print(Fore.RED + f"Error: Missing parameter {e} in JSON file")
        raise

# To generate my public and private keys
def generate_keys(p, g):
    # Step 2: choose private keys
    my_private = random.randint(1, p-1)  # My private key
    
    # Step 3: Calculate public keys
    my_public = pow(g, my_private, p)

    return my_private, my_public

def generate_shared_secret(other_public_key, my_private_key, p):
    shared_secret = pow(other_public_key, my_private_key, p)
    return shared_secret

def encrypt_decrypt_message(message, shared_secret, text_color):
    print(text_color + f"Shared secret: {shared_secret}, Message: {message}")
    encrypted_message = message ^ shared_secret
    return encrypted_message
