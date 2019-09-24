# test BLE Scanning software
# jcs 6/8/2014

# open source code downloaded from github
# wget http://raw.githubusercontent.com/switchdoclabs/iBeacon-Scanner-/master/testblescan.py

import blescan
import sys

import bluetooth._bluetooth as bluez

dev_id = 0
try:
	sock = bluez.hci_open_dev(dev_id)
	print "ble thread started"

except:
	print "error accessing bluetooth device..."
    	sys.exit(1)

blescan.hci_le_set_scan_parameters(sock)
blescan.hci_enable_le_scan(sock)

while True:
	returnedList = blescan.parse_events(sock, 10)	# second parameter means the number of devices to scan at once. more devices take longer to scan.
	print "----------"
	for beacon in returnedList:
		print beacon
