# server.py
# Author: Jesus Oviedo, 9447947; Andy Wu, 7952278

import socket
import threading
from os import _exit
from sys import stdout
from time import sleep

import hashlib
import argparse


class BlogChain:
    def _init_(self):
        self._chain = []
        self._head = -1



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
            # connect to next node
            if PID == 'P1':
                out_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                out_sock.connect((IP, PORTS['P2']))
                print("connected to server", flush=True)
            elif PID == 'P2':
                #connect p2
            elif PID == 'P3':
                #connect p2
            elif PID == 'P4':
                #connect p2
            elif PID == 'P5':
                #connect p2


def respond(conn, addr):
    # listen for incoming messages
    while True:
        try:
            data = conn.rec(1024)
            sleep(3)
        except:
            print(f"exception in receiving data from {addr[1]}", flush=True)
            break
        if not data:
            # close connection to node
            conn.close()
            print(f"connection closed from {addr[1]}", flush=True)
            break

        data = data.decode()


if __name__ == "__main__":

    sleep(1)

    # get command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('pid', type=str, help='Node ID')
    args = parser.parse_args()

    # get PID, server IP, and node port number
    PID = args.pid
    IP = socket.gethostname()
    PORTS = {'P1':9291, 'P2':9292, 'P3':9293, 'P4':9294, 'P5':9295}
    PORT = PORTS[PID]
    
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
        except:
            print("exception in accepting incoming connection", flush=True)
            break
        out_socks.append((conn, addr))
        nodes[addr[1]] = ['', conn, -1]
        threading.Thread(target=respond, args=(conn, addr)).start()