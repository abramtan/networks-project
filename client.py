import os
import socket
import pickle
import sys
import threading
import time
from datetime import datetime
import config
import tqdm
from pprint import pprint

# TODO Number of uploads, how many times to upload the .mp4

filename = "BigBuckBunny-short.mp4"
no_of_uploads = 3  # How many times to upload the video

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
        # print(f"new msg len {msglen}")
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
        # print(f'Received {input}')

        return input

        # if input['requestType'] == 'getServer':
        #     return input  # server['ip'], server['port']
        # elif input['hostType'] == 'server':
        #     client.close()
        #     sys.exit(130)
    except Exception as e:
        print(f"Problem reading message: {e}")
    finally:
        pass

def send(client, obj):
    msg = pickle.dumps(obj)
    msg = bytes(f'{len(msg) :< {headersize}}', 'utf-8') + msg
    #print(msg)
    client.send(msg)

def upload_video(host, port, filename):
    SEPARATOR = "<SEPARATOR>"
    BUFFER_SIZE = 4096 # send 4096 bytes each time step

    # get the file size
    filesize = os.path.getsize(filename)

    # create the client socket
    s = socket.socket()
    try:
        print(f"[+] Connecting to {host}:{port}")
        s.connect((host, port))
        print("[+] Connected.")

        # send the filename and filesize
        s.send(f"{filename}{SEPARATOR}{filesize}".encode())

        # start sending the file
        progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "rb") as f:
            while True:
                # read the bytes from the file
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    # file transmitting is done
                    break
                # we use sendall to assure transimission in 
                # busy networks
                s.sendall(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
    except Exception as e:
        print(e)
    # close the socket
    finally:
        s.close()






queries = 2
queryGap = 30
fullDuration = 20 #Trial length in minutes
iterTimes = fullDuration * 60 / queryGap

for i in range(int(iterTimes)):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #client.settimeout(5)
        client.connect((lbIP, lbPort))
        query = {'requestType' : 'getServer',
                    'hostType' : 'client', 
                    'hostName' : clientName,
                    'ip' : serverIP}
        
        send(client, query)

        result = None

        while result == None:
            try:
                result = receive(client)
                time.sleep(3)
            except socket.timeout:
                pass
        client.close()

        print("Sending to:", result)

        #upload_video(result['ip'], 5001, filename)
        for i in range(queries):
            threading.Thread(target = upload_video, args = (result['ip'], 5001, filename)).start()
            time.sleep(3)
        print(f"Query {i} started, sleeping...")
        time.sleep(queryGap)
        
    except KeyboardInterrupt:
        print("Terminating...")
        try:
            client.close()
            sys.exit(130)
        except SystemExit:
            os._exit(130)