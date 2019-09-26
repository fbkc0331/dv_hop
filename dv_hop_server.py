# -*- coding: utf-8 -*-
# using open source code, created by 주진원, editted by 박준택



import socket
import threading
import multiprocessing

import numpy as np
import copy

import shared_ndarray as sn

# import time
# import pexpect

# import math

# import queue

# import _thread
# import matplotlib.pyplot as plt


# global variables
HOST = "192.168.0.129"      # host address
PORT = 8585                 # port number
SOCKET_QUEUE_SIZE = 200     # size for client socket queue
thread = dict()             # dictionary for multi-thread socket communication

NUM_RPI = 30                # number of all Rpi including anchors and nodes

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


# function : recieve ble data("host_ID,Rpi_ID,rssi") from client socket and enqueue it
def recv_data(client_socket, q, thread_num):
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
    thread[thread_num].join()
    del thread[thread_num]


#-----------------------------------------------------  DATA PROCESSING  ------------------------------------------------------#
# function : dequeue ble data("host_ID,Rpi_ID,rssi"), split it apart by separator ',' and put data to shared matrix(sh_link_info_mat)
def put_link_info(q, sh_link_info_mat):                     # sh_ means it is on shared memory
    while 1:
        if q.empty() is False:
            ble_data = q.get()                              #
            from_ID, to_ID, rssi = ble_data.split(',')      # ble data is 7,11,-74 means Rpi_ID 7 found Rpi_ID 11 with rssi == -74
            sh_link_info_mat.array[from_ID][to_ID] = 1      # so put this information to shared memory

            print(sh_link_info_mat.array)


#----------------------------------------------------  MATRIX CALCULATION  ----------------------------------------------------#
# function : get (n x n) matrix contains hop count from Rpi_i to Rpi_j (i, j = 0 ~ n-1)
def get_hop_cnt_mat(link_info_mat):                                         # link_info_mat is copy of sh_link_info_mat
    hop_cnt_mat = np.zeros((NUM_RPI, NUM_RPI))
    cp_link_info_mat = copy.deepcopy(link_info_mat)                         #
    symmetric_mat(cp_link_info_mat)                                         # copies are used for power of matrix
    pwr_link_info_mat = copy.deepcopy(cp_link_info_mat)                     #

    get_hop_cnt_data(hop_cnt_mat, pwr_link_info_mat, 1)                     # num_hop == 1
    for num_hop in range(2, NUM_RPI):                                       # num_hop == 2 ~ NUM_RPI-1
        pwr_link_info_mat = np.dot(pwr_link_info_mat, cp_link_info_mat)     #
        get_hop_cnt_data(hop_cnt_mat, pwr_link_info_mat, num_hop)           #

    return hop_cnt_mat


# function : make link_info_mat to symmetric matrix -> if Rpi_i did not find Rpi_j but Rpi_j found Rpi_i, assume Rpi_i also found Rpi_j
def symmetric_mat(link_info_mat):
    n = len(link_info_mat)
    for row in range(n):
        for col in range(n):
            if link_info_mat[row][col] != link_info_mat[col][row]:
                link_info_mat[row][col] = link_info_mat[col][row] = 1


# function : put hop count data to hop count matrix
def get_hop_cnt_data(hop_cnt_mat, pwr_link_info_mat, num_hop):
    n = len(pwr_link_info_mat)
    for row in range(n):
        for col in range(n):
            if pwr_link_info_mat[row][col] != 0 and hop_cnt_mat[row][col] == 0:
                hop_cnt_mat[row][col] = num_hop




#---------------------------------------------------  POSITION ESTIMATION  ----------------------------------------------------#


#------------------------------------------------------  MAIN FUNCTION  -------------------------------------------------------#
#function : main
if __name__=="__main__":
    server_socket = server_socket_init()

    q = multiprocessing.Queue()
    print("Queue finished")
    sh_link_info_mat = sn.SharedNDarray((NUM_RPI, NUM_RPI))

    p1 = multiprocessing.Process(target = recv_data_multi_thread, args = (server_socket, q))
    p2 = multiprocessing.Process(target = put_link_info, args=(q, sh_link_info_mat))

    p1.start()
    print("Process1")
    p2.start()
    print("Process2")

    p1.join()
    p2.join()
