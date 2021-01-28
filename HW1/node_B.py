import socket
import utility
import globals
from Crypto.Cipher import AES


def decrypt_cbc(input_bytes, key, initial_iv):
    try:
        current_block = input_bytes[:16]
        iv = initial_iv

        result = b''
        while len(input_bytes) > 0:
            plain_text = utility.xor_for_bytes(iv, AES.new(key, AES.MODE_ECB).decrypt(current_block))
            result += plain_text
            input_bytes = input_bytes[16:]
            iv = current_block
            current_block = input_bytes[:16]
        return result
    except Exception as excpt_cbc:
        print(type(excpt_cbc), str(excpt_cbc))


def decrypt_ofb(input_bytes, key, initial_iv):
    try:
        result = b''
        iv = initial_iv
        while len(input_bytes) > 0:
            to_xor = AES.new(key, AES.MODE_ECB).encrypt(iv)
            result += utility.xor_for_bytes(to_xor, input_bytes[:16])
            iv = to_xor
            input_bytes = input_bytes[16:]
        return result
    except Exception as excpt_ofb:
        print(type(excpt_ofb), str(excpt_ofb))


if __name__ == '__main__':
    K3, Q = globals.K3, globals.Q
    output_file = open(globals.decrypt_to_path, 'wb')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 2557)

    print(f'Node B started on address {server_address[0]} with port {server_address[1]}')

    sock.bind(server_address)
    sock.listen()
    print('Node B entered waiting state in order to fetch content from Node A! Waiting ....')

    while True:
        connection, client_address = sock.accept()
        print('Connection with Node A established waiting to fetch working mode and associated key!')
        while True:
            keys_length = int(connection.recv(16).decode('ascii'))
            connection.sendall(globals.acknowledged)
            keys_binaries = connection.recv(keys_length)
            current_mode = int(keys_binaries[:1].decode('ascii'))
            keys_binaries = keys_binaries[1:]
            current_key = AES.new(globals.K3.encode(), AES.MODE_ECB).decrypt(keys_binaries[:16])
            current_iv = AES.new(globals.K3.encode(), AES.MODE_ECB).decrypt(keys_binaries[16:])
            connection.sendall(globals.acknowledged)
            print(f'Current working mode is:{current_mode} and associated keys are {current_key} {current_iv}')
            blocks_size = int(connection.recv(16).decode('ascii'))
            connection.sendall(globals.acknowledged)
            print(f'Block of size:{blocks_size} will be transferred')
            blocks = connection.recv(blocks_size)
            decrypted_blocks = b''
            print(f'Block of size:{blocks_size} will start decrypting with mode:{current_mode}')
            if current_mode == 0:
                decrypted_blocks += utility.remove_pad(decrypt_cbc(blocks, current_key, current_iv))
            elif current_mode == 1:
                decrypted_blocks += utility.remove_pad(decrypt_ofb(blocks, current_key, current_iv))
            output_file.write(decrypted_blocks)
            connection.sendall(globals.acknowledged)
            print(f'Done decrypting received block of size:{blocks_size}!')
            terminate = int(connection.recv(16).decode('ascii'))
            connection.sendall(globals.acknowledged)
            if terminate == 1:
                print('Job finished!')
                output_file.close()
                break

