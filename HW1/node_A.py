import socket
import random
import utility
import globals
import os
from Crypto.Cipher import AES


def get_key_from_KM(encryption_mode):
    sock_km = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = ('localhost', globals.KM_port)
    sock_km.connect(address)
    buffer = bytes()
    try:
        message = encryption_mode
        sock_km.sendall(message.encode())
        while True:
            data = sock_km.recv(16)
            if data:
                buffer += data
            else:
                break
    except Exception as excpt_km:
        print(type(excpt_km), str(excpt_km))
    finally:
        sock_km.close()
    return [buffer[:16], buffer[16:]]


def encrypt_cbc(input_bytes, current_key, initial_iv):
    try:
        current_block = input_bytes[:16]
        cbc_iv = initial_iv
        encrypted = b''
        while len(input_bytes) > 0:
            cypher_text = AES.new(current_key, AES.MODE_ECB).encrypt(utility.xor_for_bytes(cbc_iv, current_block))
            encrypted += cypher_text
            input_bytes = input_bytes[16:]
            current_block = input_bytes[:16]
            cbc_iv = cypher_text
        return encrypted
    except Exception as except_cbc:
        print(type(except_cbc), str(except_cbc))


def encrypt_ofb(input_bytes, current_key, initial_iv):
    try:
        encrypted = b''
        ofb_iv = initial_iv
        while len(input_bytes) > 0:
            to_xor = AES.new(current_key, AES.MODE_ECB).encrypt(ofb_iv)
            to_encryption = input_bytes[:16]
            encrypted += bytes(utility.xor_for_bytes(to_xor, to_encryption))
            input_bytes = input_bytes[16:]
            ofb_iv = to_xor
        return encrypted
    except Exception as except_ofb:
        print(type(except_ofb), str(except_ofb))


if __name__ == '__main__':
    K3, Q = globals.K3, globals.Q
    print('Node A is ready to start communicating')
    to_encrypt_file = open(globals.encrypt_from_path, 'rb')
    file_size = os.path.getsize(globals.encrypt_from_path)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', globals.B_port)
    sock.connect(server_address)
    terminate = 0
    while file_size > 0:
        print('Node A will fetch the keys in a short while')

        mode = str(random.randrange(0, 2))
        combination = get_key_from_KM(mode)
        key, iv = AES.new(globals.K3.encode(), AES.MODE_ECB).decrypt(combination[0]), AES.new(globals.K3.encode(), AES.MODE_ECB).decrypt(combination[1])
        print('Keys were fetched successfully!...Starting sendng to Node B')

        sock.sendall(str(len(mode.encode()) + len(combination[0]) + len(combination[1])).encode())
        sock.recv(globals.acknowledged_bytes_count)
        sock.sendall(mode.encode() + combination[0] + combination[1])
        sock.recv(globals.acknowledged_bytes_count)

        print(f'Node B received {mode} {combination[0]} {combination[1]}')

        to_send = b''
        to_send_size = 0
        if file_size - globals.Q * 16 >= 0:
            chunks_from_file = to_encrypt_file.read(globals.Q * 16)
            if int(mode) == 0:
                to_send = encrypt_cbc(utility.generate_pad(chunks_from_file), key, iv)
            elif int(mode) == 1:
                to_send = encrypt_ofb(utility.generate_pad(chunks_from_file), key, iv)
            file_size = file_size - globals.Q * 16
            to_send_size = len(to_send)
            if file_size == 0:
                terminate = 1
        else:
            chunks_from_file = to_encrypt_file.read(file_size)
            if int(mode) == 0:
                to_send = encrypt_cbc(utility.generate_pad(chunks_from_file), key, iv)
                print(len(to_send))
            elif int(mode) == 1:
                to_send = encrypt_ofb(utility.generate_pad(chunks_from_file), key, iv)
            to_send_size = len(to_send)
            file_size = 0
            terminate = 1

        print('Node A is ready to send blocks to Node B')
        sock.sendall(str(to_send_size).encode())
        sock.recv(globals.acknowledged_bytes_count)
        sock.sendall(to_send)
        sock.recv(globals.acknowledged_bytes_count)
        print('Blocks sent successfully from Node A to Node B')
        sock.sendall(str(terminate).encode())
        sock.recv(globals.acknowledged_bytes_count)

    print('Job finished')
