import queue
import random
from key_exchange import generate_keys
from stream_cipher import stream_cipher
from seed_encryption import RSA
from seed_authentication import hmac_sha256

class CommunicationChannel:
    def __init__(self, role,send_queue,recieve_queue):
        self.role = role
        self.timeout = 10  
        self.max_retries = 3
        self.seed = None
        self.shared_secret = None
        self.send_queue = send_queue
        self.receive_queue = recieve_queue

    def wait_for_message(self, operation_name):
        retries = 0
        while retries < self.max_retries:
            try:
                return self.receive_queue.get(timeout=self.timeout), True
            except queue.Empty:
                retries += 1
                print(f"[{self.role}] Timeout waiting for {operation_name}. Retry {retries}/{self.max_retries}")
        return None, False

    def establish_connection(self):
        print(f"[{self.role}] Initiating key exchange...")
        private_key, public_key = generate_keys()
        self.send_queue.put(public_key)
        result, success = self.wait_for_message("receiver's public key")
        if not success:
            raise ConnectionError("Failed to receive receiver's public key")
        other_public_key = result
        
        if self.role == 'sender':
            result, success = self.wait_for_message("receiver's rsa public key")
            if not success:
                raise ConnectionError("Failed to receive receiver's rsa public key")
            rsa_public_key = result
            self.seed = random.getrandbits(32)
            rsa = RSA(key_size=64)
            encrypted_seed = rsa.encrypt(self.seed,rsa_public_key)
            self.send_queue.put(encrypted_seed)
        else:
            rsa = RSA(key_size=64)
            rsa.generate_keys()
            self.send_queue.put(rsa.get_public_key())
            result, success = self.wait_for_message("sender's seed key")
            if not success:
                raise ConnectionError("Failed to receive sender's seed key")
            encrypted_seed = result
            self.seed = rsa.decrypt(encrypted_seed)
        print(f"[{self.role}] Key exchange completed. Sent: {public_key}, Recieved: {other_public_key}, Seed: {self.seed}")
        return True

    def send_message(self, message):
        if not self.seed:
            raise ValueError("Secure connection not established")
            
        cipher_text = ""
        for encrypted_chunk in stream_cipher(message, self.seed, is_encrypting=True):
            cipher_text += encrypted_chunk
            
        hmac = hmac_sha256(cipher_text, str(self.seed))
        self.send_queue.put((cipher_text, hmac))
        print(f"[{self.role}] sent message: {message} ")
        return True

    def receive_message(self):
        if not self.seed:
            raise ValueError("Secure connection not established")
            
        result, success = self.wait_for_message("encrypted message")
        if not success:
            raise ConnectionError("Failed to receive message")
            
        cipher_text, received_hmac = result
        
        calculated_hmac = hmac_sha256(cipher_text, str(self.seed))
        if calculated_hmac != received_hmac:
            raise ValueError("Message authentication failed")
            
        decrypted_text = ""
        for decrypted_chunk in stream_cipher(cipher_text, self.seed, is_encrypting=False):
            decrypted_text += decrypted_chunk
            
        print(f"[{self.role}] received message: {decrypted_text} ")
        return decrypted_text

    def close(self):
        """Close the communication channel"""
        self.send_queue.put(None)
        print(f"[{self.role}] thread finished successfully")
