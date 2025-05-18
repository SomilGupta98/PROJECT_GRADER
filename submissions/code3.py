import math

def is_prime(n):
    if n <= 1:
        return False
    limit = int(math.sqrt(n))
    for i in range(2, limit):
        if n % i == 0:
            return False
    return True
