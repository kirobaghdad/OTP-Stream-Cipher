import lcg

def stream_cipher(plaintext):
    # for every 10 chars return the encrypted or decrypted data
    
    for i in range(0, len(plaintext), 10):
        chunk = plaintext[i:i + 10]
        yield xor_encrypt_decrypt(chunk, next(lcg(10, 5, 4, 10)))

def xor_encrypt_decrypt(plaintext, keystream_part):
    return plaintext ^ keystream_part
