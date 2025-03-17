import random

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
    """Find a primitive root modulo p"""
    for g in range(2, p):
        if all(pow(g, powers, p) != 1 
               for powers in range(1, p-1)):
            return g
    return None

# To generate my public and private keys
def generate_keys():
    # Step 1: Generate large prime number p and primitive root g
    p = generate_prime(100, 1000)  # Public prime number
    g = find_primitive_root(p)     # Public primitive root
    
    # Step 2: choose private keys
    my_private = random.randint(1, p-1)  # My private key
    
    # Step 3: Calculate public keys
    my_public = pow(g, my_private, p)

    return my_private, my_public

# Exchanges the keys between the 2 servers
def diffie_hellman():

    pass


