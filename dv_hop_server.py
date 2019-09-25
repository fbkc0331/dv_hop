# -*- coding: utf-8 -*-
# using open source code, created by 주진원, editted by 박준택

import multiprocessing
# import time
import socket
# import pexpect
import threading
# import numpy as np
# import math
# import copy
# import queue
# import shared_ndarray as sn
# import _thread
# import matplotlib.pyplot as plt


# global variables
HOST = "192.168.0.129"      # host address
PORT = 8585                 # port number

SOCKET_QUEUE_SIZE = 200     # size for client socket queue
thread = dict()             # dictionary for multi-threading

# NUMBER_OF_RPI=21 #전체 노드 수 라즈베리파이 갯수이므로 항상 고쳐주자

# ANCHOR_COORDINATE=np.array([[0,12],[6,12],[6,0]]) #A1,A2,A3의 좌표, A0는 (0,0)이다.
# NUMBER_OF_ANCHOR=4


#---------------------------------------------------  SOCKET COMMUNICATION  ---------------------------------------------------#
# function : initialize server_socket
def server_socket_init():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # IP4v, stream socket
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)     # socket option : reuse server address
    server_socket.bind((HOST, PORT))
    server_socket.listen(SOCKET_QUEUE_SIZE)                                 # queue for client socket trying to connect

    return server_socket


# function : multi-threading for seamless socket communication
def recv_data_multi_thread(server_socket, q):
    global thread
    thread_num = 0

    while 1:
        client_socket, addr = server_socket.accept()
        thread[thread_num] = threading.Thread(target = recv_data, args = (client_socket, q, thread_num))
        thread[thread_num].start()
        thread_num += 1


# function : recieve ble data from client socket
def recv_data(client_socket, q, thread_num):      # todo : addr은 필요없을거같은데
    BUFF_SIZE = 64
    while 1:
        data = client_socket.recv(BUFF_SIZE).decode()
        if data == "":                              # if there is no recieved data,
            client_socket.close()                   # it means client losts internet connection
            stop_thread(thread_num)                 # so, have to close client socket and stop thread
            break
        else:
            q.put(data)


# function : stop thread when client socket is disconnected
def stop_thread(thread_num):
    global thread
    thread[thread_num].join()   # todo : 스레드 멈추고 리스트 앞으로 당겨서 저장해야할거같은데?
    del thread[thread_num]


def put_data(q): #socket통신으로 들어온 데이터를 shared_ndarray에 넣는 작업이다
    while 1:
        if q.empty() is False:
            data=q.get()
            print(data)
            #check_time=time.time()
            #cut=data_apart(data)
            #input_raw_data.array[int(data[0:cut])][int(data[cut+1:])]=1


#def data_apart(data): #데이터 수신 형태가 (보낸 raspi 숫자)%(잡힌 raspi 숫자)이기에 나누기 위해서 다음과 같이 사용
#    num=len(data)
#    for i in range(0,num):
#        if data[i] is '%':
#            return i



if __name__=="__main__":
    server_socket = server_socket_init()

    q=multiprocessing.Queue()
    print("Queue finished")

    p1 = multiprocessing.Process(target=recv_data_multi_thread,args=(server_socket, q))
    p2 = multiprocessing.Process(target=put_data,args=(q,))

    p1.start()
    print("Process1")
    p2.start()
    print("Process2")

    p1.join()
    p2.join()
