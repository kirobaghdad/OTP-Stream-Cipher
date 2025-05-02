import random

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



# To generate my public and private keys
def generate_keys(DH_params):
    p = DH_params.get('p')
    g = DH_params.get('g')
    my_private = random.randint(1, p-1)  # My private key    
    my_public = pow(g, my_private, p) # My public key

    return my_private, my_public

def generate_shared_secret(other_public_key, my_private_key, p):
    shared_secret = pow(other_public_key, my_private_key, p)
    return shared_secret

def encrypt_decrypt_message(message, shared_secret, text_color):
    print(text_color + f"Shared secret: {shared_secret}, Message: {message}")
    encrypted_message = message ^ shared_secret
    return encrypted_message
