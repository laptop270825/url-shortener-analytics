ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode_base62(num: int) -> str:
    if num == 0:
        return ALPHABET[0]
    result = []
    while num > 0:
        num, remainder = divmod(num, 62)
        result.append(ALPHABET[remainder])
    return "".join(reversed(result))