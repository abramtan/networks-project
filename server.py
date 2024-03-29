import os
import random
import socket
import pickle
import sys
import threading
import time
import config
import subprocess
import pandas as pd


hostname = 'server_' + str(random.randint(0, 100))
serverIP = config.hostIP
#serverPort = 60523
serverPort = random.randint(50000, 60000)
lbIP = config.lbIP
lbPort = 60325
headersize = 10
connected = False #Do not set to True
onLoad = False
MSG_TIMEOUT = 3
MAX_ATTEMPT = 5

def save_string_to_file(text, filename):
    file = open(filename, 'w')
    file.write(text)
    file.close()

#Receive method for initial connection
def receive(client, addr):
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
        if connected:
            decisionTree(client, input)
        return input
    except Exception as e:
        print(f"Problem reading message: {e}")
    finally:
        pass

def send(client, obj):
    msg = pickle.dumps(obj)
    msg = bytes(f'{len(msg) :< {headersize}}', 'utf-8') + msg
    #print(msg)
    client.send(msg)

#Handles request
def decisionTree(client, input):
    try:
        if input['requestType'] == 'perfQuery':
            print("Received perfQuery")
            #TODO Insert performance calculation method
            #pkgWatt, ramWatt = perfCommand()
            pkgWatt, ramWatt = perfCommandTEST()
            reply = {'requestType' : 'perfQuery',
                    'hostType' : 'server',
                    'hostName' : hostname,
                    'result' : pkgWatt + ramWatt
                    }
            print(f"Replying perfQuery with result: {pkgWatt}, {ramWatt}")
            send(client, reply)
        elif input['requestType'] == 'calcQuery':
            print("Received calcQuery")
            onLoad = True
            #TODO Calculate
            result = random.randint(0, 1000)
            reply = {'requestType' : 'calcQuery',
                    'hostType' : 'server',
                    'hostName' : hostname,
                    'result' : result
                    }
            print(f"Replying calcQuery with result: {result}")
            send(client, reply)
            onLoad = False
    except Exception as e:
        print(f'Thread encountered problem: {e}')
    finally:
        pass

def perfCommand():
    turbostat_command = ["sudo", "turbostat", "--Summary", "--quiet", "--interval", "1", "--show", "PkgWatt,RAMWatt", "--num_iterations", "1"]
    output = subprocess.run(turbostat_command, capture_output=True, text=True)
    time.sleep(1)
    turbostat_output = output.stdout
    try:
        output = turbostat_output.split('\n')[1].split('\t')
        print("Success perfCommand")
        perfStore.loc[len(perfStore.index)] = [runInstance, time.ctime(time.time()), onLoad, output[0], output[1]]
        return float(output[0]), float(output[1]) #PkgWatt, RAMWatt
    except:
        print("Failed perfCommand")
        return 0.0,0.0
    
def perfCommandTEST():
    return random.randint(1,1000), random.randint(1,1000)
#-------------------------------------------------------------------------------------------------------------------------------------------------
runInstance = random.randint(1,1000)
perfStore = pd.DataFrame(columns = ['runInstance', 'time', 'onLoad', 'pkgWatt', 'ramWatt'])
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.settimeout(5)
#Attempt to connect to LB
while connected == False:
    try:
        print("Attempting to connect to server")
        client.connect((lbIP, lbPort))
        input = {'requestType' : 'connect', 
                 'hostType' : 'server', 
                 'hostName' : hostname,
                 'ip' : serverIP,
                 'port': serverPort}
        send(client, input)
        data = receive(client, None)
        if data == input: #If server reply is the exact same as connect request
            connected = True
    except socket.error:
        pass
print("Connected to LB\n=================================")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((serverIP, serverPort))
server.listen()
server.setblocking(False)
server.settimeout(1)
print(f"Created listening socket {serverIP}:{serverPort}")
#Listen to request

try:
    while True:
        try:
            #print('Waiting for connection...')
            client, addr = server.accept()
            threading.Thread(target = receive, args = (client, addr)).start()
        except socket.timeout:
            pass
except KeyboardInterrupt:
    print("Terminating...")
    try:
        server.close()
        perfStore.to_csv(f'perfData{runInstance}.csv')
        sys.exit(130)
    except SystemExit:
        os._exit(130)
