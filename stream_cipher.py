from lcg import lcg
import json

def read_lcg_params(file_path):
    try:
        # Open and read the JSON file
        with open(file_path, 'r') as file:
            params = json.load(file).get("LCG_params")
        
        # Extract parameters
        m = params.get('m')
        a = params.get('a')
        c = params.get('c')

        # Basic validation
        if not all(isinstance(x, (int, float)) for x in [m, a, c]):
            raise ValueError("All parameters must be numbers")
        if m <= 0:
            raise ValueError("Modulus (m) must be positive")

        return m, a, c

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        raise
    except json.JSONDecodeError:
        print(f"Error: File '{file_path}' contains invalid JSON")
        raise
    except KeyError as e:
        print(f"Error: Missing parameter {e} in JSON file")
        raise

def stream_cipher(plaintext, seed, is_encrypting=True):
    # for every 10 chars return the encrypted or decrypted data
    
    # read LCG Params    
    m, a, c = read_lcg_params("config.json")
    if is_encrypting:
        # For encryption, process the text in 10-character chunks
        for i in range(0, len(plaintext), 10):
            chunk = plaintext[i:i + 10]
            yield xor_encrypt_decrypt(chunk, next(lcg(modulus=m, a=a, c=c, seed=seed)), True)
    else:
        # For decryption, process the hex string in 20-character chunks (10 bytes = 20 hex chars)
        for i in range(0, len(plaintext), 20):
            chunk = plaintext[i:i + 20]
            yield xor_encrypt_decrypt(chunk, next(lcg(modulus=m, a=a, c=c, seed=seed)), False)

def xor_encrypt_decrypt(plaintext, keystream_part, is_encrypting):
    # Convert plaintext to bytes based on input type
    try:
        if is_encrypting:
            # For encryption, convert string to bytes
            data_bytes = plaintext.encode('utf-8')
        else:
            # For decryption, convert hex string to bytes
            data_bytes = bytes.fromhex(plaintext)
        
        # Convert keystream to bytes
        key_bytes = int(keystream_part).to_bytes(max(4, (int(keystream_part).bit_length() + 7) // 8), byteorder='big')
        
        # Perform XOR operation
        result = bytes([d ^ k for d, k in zip(data_bytes, key_bytes)])
        
        if is_encrypting:
            # For encryption, return hex string
            return result.hex()
        else:
            # For decryption, return decoded string
            return result.decode('utf-8')
            
    except Exception as e:
        print(f"Error in {'encryption' if is_encrypting else 'decryption'}: {str(e)}")
        raise