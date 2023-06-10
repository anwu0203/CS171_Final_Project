import socket
import threading
from os import _exit
from sys import stdout
from time import sleep

import hashlib
import argparse

def get_user_input():
    while True:
        user_input = input()
        if user_input == 'exit':
            # exit and close all connections
            for out_sock in out_socks:
                out_sock[0].close()
            stdout.flush()
            _exit(0)
        elif user_input == 'connect':
            try:
                out_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                out_sock.connect((IP, SERVER_PORT))
                addr = out_sock.getsockname()
                out_socks.append((out_sock, addr))
                print("connected to server", flush=True)
                threading.Thread(target=respond, args=(out_sock, addr)).start()
            except:
                print("exception in trying to connect to server", flush=True)
        elif user_input == 'print':
            for out_sock in out_socks:
                print(f'conn: {out_sock[0]} addr: {out_sock[1]}', flush=True)
                print(f'laddr {out_sock[0].getsockname()}, raddr {out_sock[0].getpeername()}')
        else:
            for out_sock in out_socks:
                try:
                    out_sock[0].sendall(bytes(user_input, "utf-8"))
                except:
                    print("exception in sending to server", flush=True)


def respond(conn, addr):
    # listen for incoming messages
    while True:
        try:
            data = conn.recv(1024)
        except:
            print(f"exception in receiving data from {addr[1]}", flush=True)
            break
        if not data:
            # close connection to node
            conn.close()
            out_socks.remove((conn, addr))
            print(f"connection closed from {addr[1]}", flush=True)
            break

        data = data.decode()
        print(data)


if __name__ == "__main__":

    sleep(1)

    # get command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('pid', type=str, help='Node ID')
    parser.add_argument('port', type=str, help='Port Number')
    parser.add_argument('s_port', type=str, help='Server Port Number')
    args = parser.parse_args()

    # get PID, server IP, and node port number
    PID = args.pid
    PORT = int(args.port)
    SERVER_PORT = int(args.s_port)
    IP = socket.gethostname()
    
    # open listening socket
    in_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    in_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    in_sock.bind((IP, PORT))
    in_sock.listen()

    # containers for connections
    out_socks = []
    nodes = {}
    clients_insocks = {}

    global missing_replies
    missing_replies = [5]

    # start thread for user input
    threading.Thread(target=get_user_input).start()

    # receive incoming connections
    while True:
        try:
            conn, addr = in_sock.accept()
            print(f"accepted connection from {addr[1]}", flush=True)
        except:
            print("exception in accepting incoming connection", flush=True)
            break
        out_socks.append((conn, addr))
        # nodes[addr[1]] = ['', conn, -1]
        threading.Thread(target=respond, args=(conn, addr)).start()