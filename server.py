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
import tqdm
import ffmpeg_streaming
from ffmpeg_streaming import Formats
import datetime
import boto3
from pprint import pprint

wattMultiplier = 120
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
SERVER_HOST = serverIP
SERVER_PORT = 5001
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
activeConnections = 0
jobCount = 0
lock = threading.Lock()

# def receiveVideoHandler(s):
#     client_upload_video, address = s.accept()
#     receiveVideo(client_upload_video, address)

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

def receiveVideo(client_upload_video, address):
    global activeConnections, jobCount
    state = "Success"
    lock.acquire()
    print(f'Starting receiveVideo. Active connections: {activeConnections}')
    activeConnections += 1
    onLoad = True
    jobNo = random.randint(1,1000)
    jobStore.loc[len(jobStore.index)] = [jobNo, time.ctime(time.time()), "Start", '-']
    print(f"# of active connections: {activeConnections}")
    lock.release()
    try:
        print(f"{address} is uploading a video...")

        # receive the file infos
        # receive using client socket, not server socket
        received = client_upload_video.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)
        # remove absolute path if there is
        filename = os.path.basename(filename)
        # convert to integer
        filesize = int(filesize)

        # start receiving the file from the socket
        # and writing to the file stream
        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        
        # Timestamp the uploaded video file
        t = time.localtime()
        current_time = time.strftime("%d_%H_%M_%S", t)
        save_video_filepath = './media/originals/' + filename[:-4] + '_' + current_time + '.mp4'
        print(save_video_filepath)

        os.makedirs(os.path.dirname(save_video_filepath), exist_ok=True)
        
        with open(save_video_filepath, "wb") as f:
            while True:
                # read 1024 bytes from the socket (receive)
                bytes_read = client_upload_video.recv(BUFFER_SIZE)
                if not bytes_read:    
                    # nothing is received
                    # file transmitting is done
                    break
                # write to the file the bytes we just received
                f.write(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
        
        client_upload_video.close()
        save_hls_filepath = transcode(filename, current_time)
        os.remove(save_video_filepath)
        #print(save_hls_filepath)
        print(type(current_time))
        #print(filename)
        #uploadS3(save_hls_filepath[:25], current_time, filename)
    except Exception as e:
        t = time.localtime()
        current_time = time.strftime("%d_%H_%M_%S", t)
        state = 'Fail'
        save_hls_filepath = transcode("BigBuckBunny-short.mp4", current_time)
    finally:
        lock.acquire()
        if activeConnections > 0:
            activeConnections -= 1
        jobStore.loc[len(jobStore.index)] = [jobNo, time.ctime(time.time()), "End", state]
        jobCount +=1
        onLoad = False
        print(f"Request Complete with status {state}")
        print(f"# of active connections: {activeConnections}")
        lock.release()

def transcode(filename, current_time):
    video = ffmpeg_streaming.input(filename)
    print("Transcoding...")
    def monitor(ffmpeg, duration, time_, time_left, process):
        per = round(time_ / duration * 100)
        sys.stdout.write(
            "\rTranscoding...(%s%%) %s left [%s%s]" %
            (per, datetime.timedelta(seconds=int(time_left)), '#' * per, '-' * (100 - per))
        )
        sys.stdout.flush()

    save_hls_filepath = './media/dash/' + current_time + '/' + filename[:-4] + '.m3u8'

    hls = video.hls(Formats.h264())
    hls.auto_generate_representations([640, 480])
    hls.output(save_hls_filepath, monitor=monitor)
    os.remove(save_hls_filepath)

    return save_hls_filepath

def uploadS3(save_hls_filepath, current_time, file_name):
    local_directory = save_hls_filepath
    bucket = 'networks-project-s3-bucket'
    destination = current_time

    print(local_directory, destination)
    print('\n')

    client = boto3.client('s3')

    for root, dirs, files in os.walk(local_directory):

        for filename in files:

            local_path = os.path.join(root, filename)
            relative_path = os.path.relpath(local_path, local_directory)
            s3_path = os.path.join(destination, relative_path)

            print('Searching "%s" in "%s"' % (s3_path, bucket))
            try:
                response = client.head_object(Bucket=bucket, Key=s3_path)
                print("Path found on S3! Skipping %s..." % s3_path)
            except:
                print("Uploading %s..." % s3_path)
                response = client.upload_file(local_path, bucket, s3_path, ExtraArgs={'ACL':'public-read'})
            pprint(response)

    print(f'Done uploading. Access video here: https://networks-project-s3-bucket.s3.amazonaws.com/{destination}/{file_name[:-4]}.m3u8')

def send(client, obj):
    msg = pickle.dumps(obj)
    msg = bytes(f'{len(msg) :< {headersize}}', 'utf-8') + msg
    #print(msg)
    client.send(msg)

#Handles request
def decisionTree(client, input):
    global activeConnections
    try:
        if input['requestType'] == 'perfQuery':
            print("Received perfQuery")
            pkgWatt, ramWatt = perfCommandTEST()
            #pkgWatt, ramWatt = 0,0 
            lock.acquire()
            wattSum = "" + str(pkgWatt + ramWatt)
            #connections = "" + str(activeConnections)
            reply = {'requestType' : 'perfQuery',
                     'hostType' : 'server',
                     'hostName' : hostname,
                      'result' : wattSum,
                      'activeConnections' : str(activeConnections)
            }
            lock.release()
            
            print(f"Replying perfQuery with result: {pkgWatt+ramWatt}, connections= {activeConnections}")
            send(client, reply)
    except Exception as e:
        send(client, reply)
        print(f'Thread encountered problem: {e}')
    finally:
        pass

def perfCommand():
    turboInterval = 1
    turbostat_command = ["sudo", "turbostat", "--Summary", "--quiet", "--interval", turboInterval, "--show", "PkgWatt,RAMWatt", "--num_iterations", "1"]
    output = subprocess.run(turbostat_command, capture_output=True, text=True)
    time.sleep(turboInterval + 1)
    turbostat_output = output.stdout
    try:
        output = turbostat_output.split('\n')[1].split('\t')
        print("Success perfCommand")
        perfStore.loc[len(perfStore.index)] = [time.ctime(time.time()), onLoad, output[0], output[1]]
        return float(output[0]), float(output[1]) #PkgWatt, RAMWatt
    except:
        print("Failed perfCommand")
        return 0.0,0.0
    
def perfCommandTEST():
    lock.acquire()
    count = activeConnections
    lock.release()
    offset = random.randint(-20, 20)
    if count < 4:
        calc = wattMultiplier * 0.3 * count + offset
        if calc < 0:
            return 0
        else:
            return wattMultiplier * 0.3 * count + offset, 0
    else:
        return wattMultiplier
#-------------------------------------------------------------------------------------------------------------------------------------------------
runInstance = time.ctime(time.time())
perfStore = pd.DataFrame(columns = ['time', 'onLoad', 'pkgWatt', 'ramWatt'])
jobStore = pd.DataFrame(columns = ['jobNo', 'time', 'State', 'Success'])
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

lbIP, lbPort = client.getpeername()

# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.bind((serverIP, serverPort))
# server.listen()
# server.setblocking(False)
# server.settimeout(1)
# print(f"Created listening socket {serverIP}:{serverPort}")
# #Listen to request

# Opening port for video upload
s = socket.socket()
s.bind((SERVER_HOST, SERVER_PORT))
s.listen()
# print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

def lbPort():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((serverIP, serverPort))
        server.listen()
        server.setblocking(False)
        server.settimeout(1)
        print(f"Created listening socket {serverIP}:{serverPort}")
        while True:
            try:
                client, addr = server.accept()
                print("reading...")
                threading.Thread(target = receive, args = (client, addr)).start()
            except socket.timeout:
                pass
    finally:
        server.close()

try:
    threading.Thread(target = lbPort, args = ()).start()
    while True:
        try:
            # For receiving videos
            client_upload_video, address = s.accept() 
            threading.Thread(target = receiveVideo, args = (client_upload_video, address)).start()
        except socket.timeout:
            pass
except KeyboardInterrupt:
    print("Terminating...")
    try:
        s.close()
        perfStore.to_csv(f'{runInstance}-perfData.csv')
        jobStore.to_csv(f'{runInstance}-jobData.csv')
        sys.exit(130)
    except SystemExit:
        os._exit(130)