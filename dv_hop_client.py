# -*- coding: utf-8 -*-
#!/usr/bin/python3
# test BLE Scanning software
# 오픈소스 활용, 만든이 : 주진원, 수정 : 박준택

import blescan          # open source module (better not to modify)
import bluetooth
import bluetooth._bluetooth as bluez

#import pexpect -> 이 module은 현재 쓸 계획 X

import os
import sys
import time
import struct
import socket
import subprocess
import glob
import multiprocessing
#import queue

# global variables
reset_point = 0
SERVER = "192.168.0.2"      # server address
PORT = 8585                 # port number
RSSI_THRESHOLD = -70

RPI_MAC_ADDR_SET = ['b8:27:eb:48:de:38', 'b8:27:eb:aa:2a:fd', 'b8:27:eb:a5:11:b8', 'b8:27:eb:96:5f:48', 'b8:27:eb:17:d9:c0', 'b8:27:eb:52:1b:57',
                    'b8:27:eb:32:ac:9d', 'b8:27:eb:61:96:25', 'b8:27:eb:b9:87:55', 'b8:27:eb:db:fe:06', 'b8:27:eb:ed:d2:9a', 'b8:27:eb:99:54:56',
                    'b8:27:eb:b0:05:dd', 'b8:27:eb:57:e3:74', 'b8:27:eb:af:b9:a5', 'b8:27:eb:38:cb:ca', 'b8:27:eb:90:aa:0c', 'b8:27:eb:3d:c0:38',
                    'b8:27:eb:e8:d2:e2', 'b8:27:eb:77:13:3d', 'b8:27:eb:3e:65:c9', 'b8:27:eb:0f:6f:d2', 'b8:27:eb:d7:b7:5e', 'b8:27:eb:05:f4:5e',
                    'b8:27:eb:77:8e:e0', 'b8:27:eb:ae:e4:a7', 'b8:27:eb:f4:47:bb', 'b8:27:eb:14:51:07', 'b8:27:eb:e2:0b:b7', 'b8:27:eb:fc:ab:d8']

# function : check if scanned device is Rpi and return ID of Rpi
def addr_confirm(addr):
    set_num = len(RPI_MAC_ADDR_SET)
    isRpi = False

    for i in range(set_num):
        if(RPI_MAC_ADDR_SET[i] == str(addr)):
            isRpi = str(i)

    return isRpi

# function : determine ID to send to server based on hostname of Rpi
def comfirm_host_ID():
    myhost = os.uname()[1]          # get hostname (A0, A1, A2, A3, N1, N2, N3, ....)
    host_order = int(myhost[1:])

    if myhost[0] == 'A':            # if Rpi is A(anchor)
        return host_order
    else:                           # if Rpi is N(node)
        return host_order+3

# funcion : scan ble devices and enqueue raw data(iBeacon)
def get_ble_data(sock, q):
    while 1:
        returnedList = blescan.parse_events(sock, 5)    # second parameter means the number of devices to scan at once. more devices take longer to scan.
        q.put(returnedList)

# function : send data form "host_ID%scanned_Rpi" to server
def send_ble_data_to_server(q, host_ID):
    # send data to server
    while 1:
        if q.empty() is False:
            ble_raw_data = q.get()
            for ble_data in ble_raw_data:
                mac_address, udid, major, minor, tx_power, rssi = ble_data.split(',')   # get mac_address and rssi
                Rpi = addr_confirm(mac_address)                                     # find device number of scanned device
                if Rpi is not False:
                    str1 = Rpi + ',' + mac_address + ',' + rssi
                    print(str1)
                        


##############################################################################################
def restart(): #이 함수는 오픈소스를 활용하여 만들었습니다. 수정하지 말것은 표시해놓겠습니다.
# 코드를 다시 실행하고 싶으면 실행하는 것을 추천
    global reset_point
    reset_point += 1
    if reset_point > 6:
        executable = sys.executable#금지
        args = sys.argv[:]#금지
        args.insert(0, sys.executable)#금지
        time.sleep(2)#숫자는 바꿔도 된다
        os.execvp(executable, args)#금지
################################################################################################

# funcion : main
if __name__ == "__main__":

#-----------------------   DO NOT MODIFY   -----------------------#
#  github : switchdoclabs/iBeacon-Scanner-/master/testblescan.py  #
#-----------------------------------------------------------------#
    dev_id = 0
    try:
            sock = bluez.hci_open_dev(dev_id)
            #print ("ble thread started")

    except:
            print ("error accessing bluetooth device...")
            sys.exit(1)

    blescan.hci_le_set_scan_parameters(sock)
    blescan.hci_enable_le_scan(sock)
#-----------------------------------------------------------------#

    q = multiprocessing.Queue()         # queue for multiprocessing
    host_ID = comfirm_host_ID()

    # run two functions in parallel to send data to server
    p1 = multiprocessing.Process(target = get_ble_data, args = (sock, q))
    p2 = multiprocessing.Process(target = send_ble_data_to_server, args = (q, host_ID))
    p1.start()
    p2.start()

    # p1.join()     # client process terminated with ctrl+c
    # p2.join()     # so join() is not necessary
