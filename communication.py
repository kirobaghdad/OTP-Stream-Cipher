import math
import queue
import random
from key_exchange import generate_keys, encrypt_decrypt_message, generate_shared_secret
from stream_cipher import stream_cipher
from seed_authentication import hmac_sha256
from colorama import Fore,Style, init

class CommunicationChannel:
    def __init__(self, role,send_queue,receive_queue,p,g,config_file, text_color):
        self.role = role
        self.timeout = 10
        self.max_retries = 3
        self.seed = None
        self.shared_secret = None
        self.config_file = config_file
        self.send_queue = send_queue
        self.receive_queue = receive_queue
        self.p= p
        self.g= g
        self.text_color = text_color

    def wait_for_message(self, operation_name):
        retries = 0
        while retries < self.max_retries:
            try:
                return self.receive_queue.get(timeout=self.timeout), True
            except queue.Empty:
                retries += 1
                
                print(Fore.RED + f"[{self.role}] Timeout waiting for {operation_name}. Retry {retries}/{self.max_retries}")
                
        return None, False

    def establish_connection(self):
        private_key, public_key= generate_keys(self.p,self.g)
        self.send_queue.put(public_key)
        result, success = self.wait_for_message("receiver's public key")
        if not success:
            raise ConnectionError("Failed to receive receiver's public key")
        other_public_key = result
        self.shared_key = generate_shared_secret(other_public_key, private_key, self.p)
        print(self.text_color + f"[{self.role}] Generated shared key: {self.shared_key}")
        
        if self.role == 'sender':
            self.seed = random.getrandbits(32)
            print(self.text_color + "[sender] ", end='')
            encrypted_seed = encrypt_decrypt_message(self.seed, self.shared_key, self.text_color)
            print(self.text_color + f"[{self.role}] Generated seed: {self.seed}, Encrypted seed: {encrypted_seed}")
            self.send_queue.put(encrypted_seed)
        else:
            result, success = self.wait_for_message("sender's seed key")
            if not success:
                raise ConnectionError("Failed to receive sender's seed key")
            encrypted_seed = result
            print(self.text_color + "[receiver] ", end='')
            self.seed = encrypt_decrypt_message(encrypted_seed, self.shared_key, self.text_color)
            print(self.text_color + f"[{self.role}] Received encrypted seed: {encrypted_seed}, Decrypted seed: {self.seed}")
        print(self.text_color + f"[{self.role}] Key exchange completed. Sent: {public_key}, Received: {other_public_key}, Seed: {self.seed}")
        return True

    def send_message(self, message):
        if not self.seed:
            raise ValueError("Secure connection not established")
            
            
        #send message length at first 
        self.send_queue.put(len(message))
        
        cipher_text = ""
        
        for encrypted_chunk in stream_cipher(message, self.seed,self.config_file, is_encrypting=True):
            cipher_text += encrypted_chunk
            self.send_queue.put(encrypted_chunk)
            
        hmac = hmac_sha256(cipher_text, str(self.seed))
        
        temp = len(hmac)
        for i in range(0, temp, 20):
            self.send_queue.put(hmac[i:i + 20])

        print(self.text_color + f"[{self.role}] sent message: {message} \nencrypted message: {cipher_text}\nhmac: {hmac}")
        return True


    def receive_message(self):
        if not self.seed:
            raise ValueError("Secure connection not established")
            
        # receive length 
        message_length, success = self.wait_for_message("message length")
        
        if not success:
            raise ConnectionError("Failed to receive message length")
        
        encrypted_text = ""
        
        # receive each 10 chars
        for _ in range(math.ceil(message_length / 10)):            
            result, success = self.wait_for_message("encrypted chunk")
            
            if not success:
                raise ConnectionError("Failed to receive message chunk")
        
            encrypted_text += result
            
        received_hmac = ""
        
        # receive hmac
        for _ in range(math.ceil((256) / (10 * 8))):            
            result, success = self.wait_for_message("HMAC chunk")
            
            if not success:
                raise ConnectionError("Failed to receive HMAC chunk")
        
            received_hmac += result
            
        
        calculated_hmac = hmac_sha256(encrypted_text, str(self.seed))
        
        if calculated_hmac != received_hmac:
            raise ValueError("Message authentication failed")
        
        print(self.text_color + f"[{self.role}] received encrypted message: {encrypted_text}\nhmac: {received_hmac}")
        
        decrypted_text = ""
        
        for decrypted_chunk in stream_cipher(encrypted_text, self.seed,self.config_file, is_encrypting=False):
            decrypted_text += decrypted_chunk
            
        print(self.text_color + f"[{self.role}] received decrypted message: {decrypted_text} ")
        return decrypted_text


    def close(self):
        self.send_queue.put(None)
        print(Fore.WHITE + f"[{self.role}] thread finished successfully")

