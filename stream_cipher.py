from colorama import Fore
from lcg import lcg
import json

def read_lcg_params(LCG_params):
    try:
        # Extract parameters
        m = LCG_params.get('m')
        a = LCG_params.get('a')
        c = LCG_params.get('c')

        # Basic validation
        if not all(isinstance(x, (int, float)) for x in [m, a, c]):
            raise ValueError("All parameters must be numbers")
        if m <= 0:
            raise ValueError("Modulus (m) must be positive")

        return m, a, c

    except KeyError as e:
        print(Fore.RED + f"Error: Missing parameter {e} in LCG_params dictionary")
        raise

def stream_cipher(plaintext, seed,LCG_params, chunk_size, is_encrypting=True):
    m, a, c = read_lcg_params(LCG_params)
    lcg_gen = lcg(modulus=m, a=a, c=c, seed=seed)
    if is_encrypting:
        chunk_size = chunk_size 
    else:
        chunk_size = chunk_size * 2  # For decryption, we need to double the chunk size as we convert  it to hex
    for i in range(0, len(plaintext), chunk_size):
        chunk = plaintext[i:i + chunk_size]
        yield xor_encrypt_decrypt(chunk, lcg_gen, is_encrypting)

def xor_encrypt_decrypt(plaintext, lcg_gen, is_encrypting):
    if is_encrypting:
        data_bytes = plaintext.encode('utf-8')
    else:
        data_bytes = bytes.fromhex(plaintext)
    
    key_stream = b''
    while len(key_stream) < len(data_bytes):
        keystream_part = next(lcg_gen)
        key_bytes = int(keystream_part).to_bytes(max(4, (int(keystream_part).bit_length() + 7) // 8), byteorder='big')
        key_stream += key_bytes
    
    key_stream = key_stream[:len(data_bytes)]
    
    result = bytes([d ^ k for d, k in zip(data_bytes, key_stream)])
    
    if is_encrypting:
        return result.hex()
    else:
        return result.decode('utf-8')