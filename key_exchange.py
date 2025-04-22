import random
import json

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

# TODO
def find_primitive_root(p):
    for g in range(2, p):
        if all(pow(g, powers, p) != 1 
               for powers in range(1, p-1)):
            return g
    return None

def read_DH_params(file_path):
    try:
        # Open and read the JSON file
        with open(file_path, 'r') as file:
            params = json.load(file).get("DH_params")
        
        # Extract parameters
        p_min_value = params.get('p_min_value')
        p_max_value = params.get('p_max_value')

        # Basic validation
        if not all(isinstance(x, (int, float)) for x in [p_min_value, p_max_value]):
            raise ValueError("All parameters must be numbers")
        if p_min_value <= 0 or p_max_value <= 0:
            raise ValueError("DH Params. must be positive")

        return p_min_value, p_max_value

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        raise
    except json.JSONDecodeError:
        print(f"Error: File '{file_path}' contains invalid JSON")
        raise
    except KeyError as e:
        print(f"Error: Missing parameter {e} in JSON file")
        raise


def generate_DH_params(config_file=None):
    # Step 1: Read parameters from the config file
    p_min_value, p_max_value = read_DH_params(config_file)

    # Step 2: Generate a prime number p
    p = generate_prime(p_min_value, p_max_value)

    # Step 3: Find a primitive root g of p
    g = find_primitive_root(p)
    
    if g is None:
        raise ValueError("Failed to find a primitive root for the prime number")

    return p, g
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

def encrypt_decrypt_message(message, shared_secret):
    print(f"Shared secret: {shared_secret}, Message: {message}")
    encrypted_message = message ^ shared_secret
    return encrypted_message
