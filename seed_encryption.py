import math
import random
import json

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x0, y0 = extended_gcd(b % a, a)
    x = y0 - (b // a) * x0
    y = x0
    return gcd, x, y

def is_prime(n):
    if not isinstance(n, int) or n < 2:
        return False

    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, math.isqrt(n) + 1, 2):
        if n % i == 0:
            return False

    return True

def generate_prime(bits):
    while True:
        n = random.getrandbits(bits)
        n |= (1 << bits - 1) | 1
        if is_prime(n):
            return n

def mod_inverse(e, phi):
    gcd, x, y = extended_gcd(e, phi)
    if gcd != 1:
        raise ValueError("Error: Modular inverse does not exist")
    return x % phi

class RSA:
    def __init__(self, key_size = 128, config_file="config.json"):
        self.key_size = key_size
        self.public_key = None
        self.private_key = None
        self.n = None
        self.config_file = config_file
        self.generate_keys()

    def read_params(self):
        try:
            with open(self.config_file, 'r') as file:
                params = json.load(file).get("RSA_params")
            e = params.get('e')
            return e
        except FileNotFoundError:
            print(f"Error: File '{self.config_file}' not found")
            raise
        except json.JSONDecodeError:
            print(f"Error: File '{self.config_file}' contains invalid JSON")
            raise

    def generate_keys(self):
        size = self.key_size // 2
        while True:
            p = generate_prime(size)
            q = generate_prime(size)
            if p == q:
                continue

            self.n = p * q
            phi = (p - 1) * (q - 1)

            e = self.read_params()
            if math.gcd(e, phi) == 1:
                break 

        d = mod_inverse(e, phi)
        self.public_key = (e, self.n)
        self.private_key = (d, self.n)
        print("RSA Public key: ", self.public_key)
        print("RSA Private key: ", self.private_key)

    def encrypt(self, message):
        e, n = self.public_key
        return pow(message, e, n)

    def decrypt(self, ciphertext):
        d, n = self.private_key
        return pow(ciphertext, d, n)

    def get_public_key(self):
        return self.public_key

    def get_private_key(self):
        return self.private_key