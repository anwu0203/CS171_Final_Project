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


def connect():
    sleep(3)
    for portID, port in PORTS.items():
        if (portID != PID):
            try:
                out_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                out_sock.connect((IP, port))
                raddr = out_sock.getpeername()
                out_socks[portID] = (out_sock, raddr)
                print(f"connected to {raddr[1]}", flush=True)
            except:
                print("exception in trying to connect to server", flush=True)
    sleep(1)
    for sockID, out_sock in out_socks.items():
        try:
            out_sock[0].sendall(bytes('Hi ' + PID, "utf-8"))
        except:
            print("exception in sending to server", flush=True)

    

def get_user_input():
    while True:
        user_input = input()
        if user_input == 'exit':
            # exit and close all connections
            for sockID, out_sock in out_socks.items():
                out_sock[0].close()
            stdout.flush()
            _exit(0)
        elif user_input == 'connect':
            threading.Thread(target=connect).start()
        elif user_input == 'print':
            for sockID, out_sock in out_socks.items():
                print(f'Outsock ID: {sockID} conn: {out_sock[0]} addr: {out_sock[1]}', flush=True)
            for sockID, in_sock in in_socks.items():
                print(f'Insock ID: {sockID} conn: {in_sock[0]} addr: {in_sock[1]}', flush=True)
        else:
            for sockID, out_sock in out_socks.items():
                try:
                    out_sock[0].sendall(bytes(user_input, "utf-8"))
                except:
                    print("exception in sending to server", flush=True)


def respond(conn, raddr):
    
    # listen for incoming messages
    while True:
        try:
            data = conn.recv(1024)
        except:
            print(f"exception in receiving data from {raddr[1]}", flush=True)
            break
        if not data:
            # close connection to node
            conn.close()
            try:
                out_socks.pop(pid)
            except:
                print(f"exception in disconnecting from {raddr[1]}", flush=True)
            try:
                in_socks.pop(pid)
            except:
                print(f"exception in disconnecting from {raddr[1]}", flush=True)
            print(f"connection closed from {raddr[1]}", flush=True)
            break

        data = data.decode()
        print(data)
        if data.startswith('Hi'):
            pid = data[3:]
            for portID, port in PORTS.items():
                if pid == portID:
                    in_socks[portID] = (conn, raddr)
                    break

            # test outward connection to target node
            sleep(3)
            try:
                out_socks[pid][0].sendall(bytes("connection check", "utf-8"))
                print("check success", flush=True)
            except:
                print(f"check failed {pid}, {port}", flush=True)
                try:
                    out_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    out_sock.connect((IP, port))
                    raddr = out_sock.getpeername()
                    out_socks[pid] = (out_sock, raddr)
                    print(f"connected to {raddr[1]}", flush=True)
                except:
                    print("exception in trying to connect to server", flush=True)
                sleep(1)
                for sockID, out_sock in out_socks.items():
                    try:
                        out_sock[0].sendall(bytes('Hi ' + PID, "utf-8"))
                    except:
                        print("exception in sending to server", flush=True)
            


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
    # PORTS = [9291, 9292, 9293, 9294, 9295]
    PORT = PORTS[PID]
    
    # open listening socket
    in_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    in_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    in_sock.bind((IP, PORT))
    in_sock.listen()

    # containers for connections
    out_socks = {}
    in_socks = {}

    global missing_replies
    missing_replies = [5]

    # start thread for user input
    threading.Thread(target=get_user_input).start()
    threading.Thread(target=connect).start()

    # receive incoming connections
    while True:
        try:
            conn, addr = in_sock.accept()
            print(f"accepted connection from {addr[1]}", flush=True)
        except:
            print("exception in accepting incoming connection", flush=True)
            break
        threading.Thread(target=respond, args=(conn, addr)).start()