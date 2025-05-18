def is_prime(n):
    if n <= 1:
        return False
    factors = [i for i in range(2, n) if n % i == 0]
    return len(factors) == 0
