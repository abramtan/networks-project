import os
import socket
import pickle
import sys
import threading
import time
from datetime import datetime
import config

clientName = 'clientTest'
serverIP = config.hostIP
lbIP = config.lbIP
lbPort = 60325
headersize = 10
QUERY_TIME = 10 #How often to query server for performance in seconds
MSG_TIMEOUT = 3
MAX_ATTEMPT = 5
TEST_MODE = False

def receive(client):
    try:
        data = b''
        msglen = int(client.recv(headersize))
        #print(f"new msg len {msglen}")
        while True:
            if len(data) >= msglen:
                break
            else:
                #print(f'current msg size {len(data)}, supposed msg len:{msglen}')
                remMsgLen = msglen - len(data)
                if remMsgLen >= 16:
                    data += client.recv(16)
                else:
                    data += client.recv(remMsgLen)
        input = pickle.loads(data)
        print(f'Received {input}')

        if input['hostType'] == 'server':
            client.close()
            sys.exit(130)
    except Exception as e:
        print(f"Problem reading message: {e}")
    finally:
        pass

def send(client, obj):
    msg = pickle.dumps(obj)
    msg = bytes(f'{len(msg) :< {headersize}}', 'utf-8') + msg
    #print(msg)
    client.send(msg)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#client.settimeout(5)
client.connect((lbIP, lbPort))

try:
    query = {'requestType' : 'calcQuery',
                 'hostType' : 'client', 
                 'hostName' : clientName,
                 'ip' : serverIP}
    send(client, query)
            #print('Waiting for connection...')
            #client, addr = client.accept()
    while True:
        try:
            receive(client)
            time.sleep(3)
        except socket.timeout:
            pass
except KeyboardInterrupt:
    print("Terminating...")
    try:
        client.close()
        sys.exit(130)
    except SystemExit:
        os._exit(130)