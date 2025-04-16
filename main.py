# import threading
# import queue
# import random
# from key_exchange import generate_keys
# from stream_cipher import stream_cipher
# from seed_encryption import RSA
# from seed_authentication import hmac_sha256

# # IPC
# QUEUE_TIMEOUT = 10
# MAX_RETRIES = 3
# sender_to_receiver_queue = queue.Queue()
# receiver_to_sender_queue = queue.Queue()
# plaintext = ""
# decrypted_text = ""


# # Apllying circuit breaker pattern (from SWE course)
# def wait_for_queue(q, timeout, operation_name):
#     retries = 0
#     while retries < MAX_RETRIES:
#         try:
#             return q.get(timeout=timeout), True
#         except queue.Empty:
#             retries += 1
#             print(f"[Warning] Timeout waiting for {operation_name}. Retry {retries}/{MAX_RETRIES}")
#     return None, False

# def sender_thread():
#     print("[Sender] Starting sender thread...")
#     try:
#         private_key_a, public_key_a = generate_keys()
#         sender_to_receiver_queue.put(public_key_a)
#         result, success = wait_for_queue(receiver_to_sender_queue, QUEUE_TIMEOUT, "receiver's public key")
#         if not success:
#             print("[Sender] Error: Failed to receive receiver's public key")
#             return
#         public_key_b = result

#         print("[Sender] D-H finished. Sender's sent public key = ", public_key_a, " Received receiver's public key = ", public_key_b)

#         result, success = wait_for_queue(receiver_to_sender_queue, QUEUE_TIMEOUT, "receiver's public key")
#         if not success:
#                     print("[Sender] Error: Failed to receive receiver's public key")
#                     return
#         rsa_b_public_key = result
#         print("[Sender] Received receiver's RSA public key = ", rsa_b_public_key)
                
#         seed = random.getrandbits(32)
#         print("[Sender] Seed: ", seed)
        
#         encrypted_seed = pow(seed, rsa_b_public_key[0], rsa_b_public_key[1])        
#         sender_to_receiver_queue.put(encrypted_seed)
#         print("[Sender] Encrypted seed transmitted = ", encrypted_seed)

#         try:
#             with open('input.txt', 'r') as f:
#                 plaintext = f.read()
#                 if not plaintext:
#                     raise ValueError("Input file is empty")
#         except FileNotFoundError:
#             plaintext = "Hello I am Kiro,Hamdy."
#             with open('input.txt', 'w') as f:
#                 f.write(plaintext)
#             print("[Sender] Created input.txt with sample message")
#         except ValueError as e:
#             print(f"[Sender] Error: {e}")
#             return

#         print("[Sender] Plaintext: ", plaintext)
#         cipher_text = ""
#         for encrypted_chunk in stream_cipher(plaintext, seed):
#             print("[Sender] Encrypted chunk (hex): ", encrypted_chunk)
#             cipher_text += encrypted_chunk

#         hmac = hmac_sha256(cipher_text, str(seed))
#         print("[Sender] Sent HMAC: ", hmac)
#         sender_to_receiver_queue.put((cipher_text, hmac))
#         print("[Sender] Thread finished")

#     except Exception as e:
#         print(f"[Sender] Critical error: {str(e)}")
#         sender_to_receiver_queue.put(None)

# def receiver_thread():
#     print("[Receiver] Starting receiver thread...")
#     try:
#         private_key_b, public_key_b = generate_keys()
        
#         result, success = wait_for_queue(sender_to_receiver_queue, QUEUE_TIMEOUT, "sender's public key")
#         if not success:
#             print("[Receiver] Error: Failed to receive sender's public key")
#             return
#         if result is None:
#             print("[Receiver] Error: Sender encountered an error")
#             return
#         public_key_a = result
#         receiver_to_sender_queue.put(public_key_b)
#         print("[Receiver] D-H finished. Receiver's sent public key = ", public_key_b, " Received sender's public key = ", public_key_a)

#         rsa = RSA(key_size=64)
#         receiver_to_sender_queue.put(rsa.get_public_key())
#         print("[Receiver] RSA Public key sent = ", rsa.get_public_key())

#         result, success = wait_for_queue(sender_to_receiver_queue, QUEUE_TIMEOUT, "encrypted seed")
#         if not success:
#             print("[Receiver] Error: Failed to receive encrypted seed")
#             return
#         if result is None:
#             print("[Receiver] Error: Sender encountered an error")
#             return
        
#         encrypted_seed = result
#         seed = rsa.decrypt(encrypted_seed)
#         print("[Receiver] Received encrypted seed = ", encrypted_seed, " and decrypted seed = ", seed)

#         result, success = wait_for_queue(sender_to_receiver_queue, QUEUE_TIMEOUT, "encrypted message")
#         if not success:
#             print("[Receiver] Error: Failed to receive encrypted message")
#             return
#         if result is None:
#             print("[Receiver] Error: Sender encountered an error")
#             return
#         cipher_text, received_hmac = result
#         print("[Receiver] Received encrypted message = ", cipher_text," Received HMAC = ", received_hmac)
        
#         calculated_hmac = hmac_sha256(cipher_text, str(seed))
#         if calculated_hmac != received_hmac:
#             print("[Receiver] Error: Message authentication failed!")
#             return


#         decrypted_text = ""
#         for decrypted_chunk in stream_cipher(cipher_text, seed, is_encrypting=False):
#             decrypted_text += decrypted_chunk

#         if not decrypted_text:
#             print("[Receiver] Error: Decrypted message is empty")
#             return

#         with open('output.txt', 'w') as f:
#             f.write(decrypted_text)
#         print(f"[Receiver] Decrypted message: {decrypted_text}")
#         print("[Receiver] Thread finished")

#     except Exception as e:
#         print(f"[Receiver] Critical error: {str(e)}")

# def main():    
#     sender = threading.Thread(target=sender_thread)
#     receiver = threading.Thread(target=receiver_thread)
    
#     try:
#         sender.start()
#         receiver.start()
        
#         timeout = QUEUE_TIMEOUT * (MAX_RETRIES + 1)
#         sender.join(timeout)
#         receiver.join(timeout)
        

#         if sender.is_alive() or receiver.is_alive():
#             print("Error: Communication timeout - killing threads")
#             return
        
#     except KeyboardInterrupt:
#         print("\nProcess interrupted by user")
#     except Exception as e:
#         print(f"Error in main thread: {str(e)}")

# if __name__ == "__main__":
#     main()
