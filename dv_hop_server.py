# -*- coding: utf-8 -*-
# 만든이: 주진원
import multiprocessing
import time
import socket
import time
import pexpect
import threading
import numpy as np
import math
import copy
import queue
import shared_ndarray as sn
import _thread
import matplotlib.pyplot as plt


PORT=8585
NUMBER_OF_RPI=21 #전체 노드 수 라즈베리파이 갯수이므로 항상 고쳐주자
HOST="192.168.0.2"
SOCKET_QUEUE_SIZE=200
thread_number=dict()
ANCHOR_COORDINATE=np.array([[0,12],[6,12],[6,0]]) #A1,A2,A3의 좌표, A0는 (0,0)이다.
NUMBER_OF_ANCHOR=4


server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #서버 즉시 재 사용
server_socket.bind((HOST,PORT))
server_socket.listen(SOCKET_QUEUE_SIZE) #Q 생성


def handler(client_socket,addr,q,number): #데이터를 수신하는 함수
    BUFFER_SIZE=60
    while 1:
        data = client_socket.recv(BUFFER_SIZE).decode()
        if data=="": #data가 아무것도 없으면 client에서의 internet이 끊어진 것이기에 thread를 중지시켜야한다.
            client_socket.close()
            stop_thread(number)
            break
        else:
            q.put(data)

def stop_thread(number): #연결이 끊어지면 thread를 멈추게 하기 위한 코드
    global thread_number
    thread_number[number].join()


def data_receive(q):#새로운 연결이 들어온 경우 새로운 thread를 만들어서 socket통신을 원활하게 해주는 코드
    global thread_number
    i=0
    while 1:
        client_socket,addr=server_socket.accept()
        thread_number[i]=threading.Thread(target=handler,args=(client_socket,addr,q,i))
        thread_number[i].start()
        i+=1

def put_data(q): #socket통신으로 들어온 데이터를 shared_ndarray에 넣는 작업이다
    while 1:
        if q.empty() is False:
            data=q.get()
            print(data)


if __name__=="__main__":
    q=multiprocessing.Queue()

    p1 = multiprocessing.Process(target=data_receive,args=(q,))
    p2 = multiprocessing.Process(target=put_data,args=(q,))


    p1.start()
    p2.start()

    p1.join()
    p2.join()
