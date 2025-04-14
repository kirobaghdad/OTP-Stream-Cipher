import unittest
from seed_authentication import sha256

class TestSHA256(unittest.TestCase):
    
    def test_sha256_known_vectors(self):
        # Test vectors from https://www.di-mgt.com.au/sha_testvectors.html
        test_vectors = [
            {"input": "", "expected": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},
            {"input": "abc", "expected": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"},
            
            {"input": "abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq", "expected": "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"},
            
            {"input": "abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmnhijklmnoijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu", "expected": "cf5b16a778af8380036ce59e7b0492370b249b11e8f07a51afac45037afee9d1"},
            
            
            {"input": 'a' * 1_000_000, "expected": "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0"},
        ]

        for vector in test_vectors:
            with self.subTest(vector=vector):
                self.assertEqual(sha256(vector["input"]), vector["expected"])

if __name__ == "__main__":
    unittest.main()