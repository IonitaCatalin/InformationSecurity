import socket
import globals
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


def init_K1_K2():
    return get_random_bytes(16), get_random_bytes(16)


def get_enc_128bits_init(encryption_key, plaintext):
    return AES.new(encryption_key.encode(), AES.MODE_ECB).encrypt(plaintext),AES.new(encryption_key.encode(),AES.MODE_ECB).encrypt(get_random_bytes(16))


def refreshed_key(encryption_key):
    return AES.new(encryption_key.encode(), AES.MODE_ECB).encrypt(get_random_bytes(16))


if __name__ == '__main__':

    K3, Q = globals.K3, globals.Q
    K1, K2 = init_K1_K2()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 2558)
    sock.bind(server_address)
    print(f"Node KM started on address {server_address[0]} with port {server_address[1]}")
    while True:
        sock.listen()
        while True:
            print("Node KM entered waiting state and is ready to receive data from node A!")
            connection, client_address = sock.accept()
            try:
                print("Connection with Node A established !")
                while True:
                    mode = connection.recv(16)
                    if mode is not None:
                        ciphertext = b''
                        iv = b''
                        print(f"Node KM received mode:{mode.decode('ascii')} one key will be generated accordingly")
                        if int(mode.decode('ascii')) == 0:
                            K1 = refreshed_key(globals.K3)
                            ciphertext, iv = get_enc_128bits_init(K3, K1)
                        elif int(mode.decode('ascii')) == 1:
                            K2 = refreshed_key(globals.K3)
                            ciphertext, iv = get_enc_128bits_init(K3, K2)
                        data = ciphertext + iv
                        connection.sendall(data)
                        break
            except Exception as exception:
                print(type(exception), str(Exception))
            finally:
                connection.close()
