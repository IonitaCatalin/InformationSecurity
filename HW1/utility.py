def generate_pad(input_bytes):
    padding_size = (16 - len(input_bytes)) % 16
    if padding_size == 0:
        padding_size = 16
    padding = (chr(padding_size) * padding_size).encode()
    return input_bytes + padding


def remove_pad(input_bytes):
    return input_bytes[:-ord(chr(input_bytes[-1]))]


def xor_for_bytes(first_bytes_array, second_bytes_array):
    return bytes(a ^ b for a, b in zip(first_bytes_array, second_bytes_array))
