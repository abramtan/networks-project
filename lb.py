import os
import random
import socket
import pickle
import sys
import threading
import time
from datetime import datetime
import config
import argparse

lbIP = config.hostIP
lbPort = 60325
headersize = 10
QUERY_TIME = 10 #How often to query server for performance in seconds
MSG_TIMEOUT = 3
MAX_ATTEMPT = 5
TEST_MODE = False

rr_key = 1

def serverReceive(client, echo = True, result = False):
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
        #print(f'Received {input}'
        if echo:
            pass
            # send(client, input)
        if result:
            return input
        decisionTree(client, input)
    finally:
        client.close()

def send(client, obj):
    msg = pickle.dumps(obj)
    msg = bytes(f'{len(msg) :< {headersize}}', 'utf-8') + msg
    # print(msg)
    client.send(msg)

def decisionTree(client, input):
    #Input tree
        try:
            #New Connection
            if input['requestType'] == 'connect':
                print(f"[decisionTree]New connection made: {input['hostName']}({input['hostType']})")
                lock.acquire()
                if input['hostType'] == 'client':
                    clients[input['hostName']] = {'ip' : input['ip'], 'port' : input['port']}
                    lock.release()
                elif input['hostType'] == 'server':
                    servers[input['hostName']] = {'ip' : input['ip'], 'port' : input['port'],'perf' : sys.maxsize, 'status' : True} #Set perf to max size so that no request will be forwarded to hosts that do not reply
                    lock.release()
                    if TEST_MODE:
                        testQueries(servers[input['hostName']])
                send(client, input)
            #Received performance query
            elif input['requestType'] == 'perfQuery':
                if input['hostName'] in servers.keys():
                    print(f"[decisionTree]Received perfQuery reply from {input['hostName']} with value of {input['result']}")
                    lock.acquire()
                    servers[input['hostName']]['perf'] = input['result']
                    lock.release()
                    send(client, input)
            elif input['requestType'] == 'calcQuery':
                if input['hostType'] == 'client':
                    print("Client made calcQuery")
                    #choose a server to forward query to and send
                    tempClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server = servers[select_mode()]
                    print(server)
                    tempClient.connect((server['ip'], server['port']))
                    send(tempClient, input)
                    result = serverReceive(tempClient, False, True)
                    print(f"calcQuery result: {result}")
                    send(client, result)
                if input['hostName'] in servers.keys():
                    print(f"[decisionTree]Received calcQuery reply from {input['hostName']} with value of {input['result']}")
                    #TODO: Add in algorithm thing
                    send(client, input)
            # Received query for available server IP, port from client
            elif input['requestType'] == 'getServer':
                if input['hostType'] == 'client':
                    print("Client made getServer query")
                    #choose a server to forward query to and send
                    result = servers[select_mode()]
                    # result['requestType'] = 'getServer'
                    input.update(result)
                    print(input)  # server['ip'], server['port']
                    send(client, input)
        finally:
            pass

def queryTimer():
    global servers
    waiting = True
    currentTime = QUERY_TIME
    while waiting:
        if currentTime > 0:
            time.sleep(1)
            currentTime -= 1
        else:
            serverDict = servers
            print("\n[queryTimer]Sending perfQuery to all servers")
            currentTime = QUERY_TIME
            for server in serverDict.keys():
                try:
                    perfQueryTest = {'requestType' : 'perfQuery'}
                    ackSend(servers[server], perfQueryTest)
                except Exception as e:
                    servers[server]['status'] = False
                    print(f"[queryTimer]perfQuery failed: {e}")
            wait = False
    threading.Thread(target = queryTimer).start()

def ackSend(server, obj):
    tempClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        tempClient.connect((server['ip'], server['port']))
        send(tempClient, obj)
        print(f'[ackSend]Sent {obj['requestType']} to {server['port']}')
        serverReceive(tempClient, True, False)
    finally:
        pass

def testQueries(requester):
    time.sleep(1)
    print(f"Performing TEST_MODE on {requester}")
    #perfQueryTest
    for i in range(MAX_ATTEMPT):
        try:
            perfQueryTest = {'requestType' : 'perfQuery', 'hostType' : 'LB'}
            ackSend(requester, perfQueryTest)
            print(f"[testQueries:TEST_MODE]:perfQuery success")
            break
        except Exception as e:
            print(f"[testQueries:TEST_MODE]:perfQuery failed: {e}")
    #calcQuery Test
    for i in range(MAX_ATTEMPT):
        try:
            print(f"Sending calcQuery request to {requester}")
            calcQueryTest = {'requestType' : 'calcQuery', 'hostType' : 'LB'}
            ackSend(requester, calcQueryTest)
            print(f"[testQueries:TEST_MODE]:calcQuery success")
            break
        except Exception as e:
            print(f"[testQueries:TEST_MODE]:calcQuery failed: {e}")

def select_mode():
    global mode

    match mode.upper():
        case "POWER":
            #print('POWER')
            return power_distribution()
        case "CONNECTIONS":
            #print('CONNECTIONS')
            return basic_round_robin()
        case "RR":
            #print('RR')
            return basic_round_robin()
        
def basic_round_robin():
    global servers
    l = len(servers)

    global rr_key

    # Obtain server from server list
    server = list(servers.keys())[rr_key-1]
    
    # Advance key
    if rr_key < l:
        rr_key += 1
    else:
        rr_key = 1

    # Returns key of the server to be sent to
    return server

def power_distribution():
    global servers
    l = len(servers)

    # Obtain power scores
    power = {x:servers[x]["perf"] for x in servers}
    lowest_power_server = None

    # Find server with lowest power score, check if available, use next lowest if not and so on...
    while power:
        min_power = min(power, key=power.get)

        # Dummy check if server is available
        server_status = servers[min_power]["status"]

        # Exit loop if server is available and set server, else remove server from power dictionary
        if server_status:
            lowest_power_server = min_power
            break
        else:
            del power[min_power]

    if lowest_power_server:
        return lowest_power_server
    else:
        return None

parser = argparse.ArgumentParser(description="Load Balancer")
parser.add_argument("--mode", type=str, help="Mode of Load Balancer")
args = parser.parse_args()
if args.mode != None:
    mode = args.mode
elif args.mode != None and args.mode.upper() not in ['CONNECTIONS', 'POWER', 'RR']: 
    print("Invalid arguments, exiting...")
    sys.exit(130)
else:
    print("No arguments, exiting...")
    sys.exit(130)

mode = args.mode

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((lbIP, lbPort))
server.listen()
server.setblocking(False)
server.settimeout(1)
lock = threading.Lock()
clients = {}
servers = {}

try:
    #perfQuery Timer
    threading.Thread(target = queryTimer).start()

    while True:
        try:
            #print('Waiting for connection...')
            client, addr = server.accept()
            print('Connected')
            threading.Thread(target = serverReceive, args = (client, True, False)).start()
        except socket.timeout:
            pass
except KeyboardInterrupt:
    print(f"Clients: {clients}")
    print(f"Servers: {servers}")
    print("Terminating...")
    try:
        server.close()
        sys.exit(130)
    except SystemExit:
        os._exit(130)