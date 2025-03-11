def lcg(modulus: int, a: int, c: int, seed: int):
    """Linear congruential generator."""
    while True:
        seed = (a * seed + c) % modulus
        yield seed