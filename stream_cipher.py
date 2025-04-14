import lcg
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


def stream_cipher(plaintext):
    # for every 10 chars return the encrypted or decrypted data
    
    # read LCG Params    
    m, a, c = read_lcg_params("config.json")
    
    for i in range(0, len(plaintext), 10):
        chunk = plaintext[i:i + 10]
        
        yield xor_encrypt_decrypt(chunk, next(lcg(modulus= m, a = a, c = c)))

def xor_encrypt_decrypt(plaintext, keystream_part):
    return plaintext ^ keystream_part
