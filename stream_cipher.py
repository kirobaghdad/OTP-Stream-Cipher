def xor_encrypt_decrypt(plaintext, keystream_part):
    yield plaintext ^ keystream_part
