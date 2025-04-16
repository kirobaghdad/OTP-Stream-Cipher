import unittest
import os
import json
from seed_encryption import RSA, extended_gcd, mod_inverse, is_prime

class TestRSA(unittest.TestCase):

    def test_extended_gcd(self):
        gcd, x, y = extended_gcd(240, 46)
        self.assertEqual(gcd, 2)
        self.assertEqual(240 * x + 46 * y, gcd)

    def test_mod_inverse_valid(self):
        e = 7
        phi = 40
        d = mod_inverse(e, phi)
        self.assertEqual((e * d) % phi, 1)

    def test_mod_inverse_invalid(self):
        with self.assertRaises(ValueError):
            mod_inverse(6, 12)  # gcd(6, 12) != 1, so no inverse

    def test_is_prime(self):
        self.assertTrue(is_prime(2))
        self.assertTrue(is_prime(101))
        self.assertFalse(is_prime(100))
        self.assertFalse(is_prime(1))
        self.assertFalse(is_prime(0))

    def test_generate_keys(self):
        rsa = RSA(key_size=24, config_file="test.json")
        print(rsa.get_public_key())
        print(rsa.get_private_key())
        pub = rsa.get_public_key()
        priv = rsa.get_private_key()
        self.assertIsNotNone(pub)
        self.assertIsNotNone(priv)
        self.assertEqual(len(pub), 2)
        self.assertEqual(len(priv), 2)

    def test_encrypt_decrypt(self):
        rsa = RSA(key_size=24, config_file="test.json")
        message = 4
        encrypted = rsa.encrypt(message)
        print(encrypted)
        decrypted = rsa.decrypt(encrypted)
        print(decrypted)
        self.assertEqual(decrypted, message)


if __name__ == '__main__':
    unittest.main()
