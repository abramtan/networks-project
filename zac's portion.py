import time
import random
import json

# Global Variables

rr_key = 1

# Functions

def send_to_server(request, server):
    request = "Sending request " + request + " to server " + server
    print(request)
    return request

def retrieve_power():
    with open("servers.json", "r") as f:
        server_list = json.load(f)

    for server in server_list:
        # Dummy Updating Power Score
        response = send_to_server("RETRIEVE POWER", server_list[server]["address"])
        server_list[server]["power_score"] = random.randint(0, 100)
        
    with open("servers.json", "w") as f:
        json.dump(server_list, f, indent=4)

    print("Updated power scores.")

def basic_round_robin(requests):
    with open("servers.json", "r") as f:
        server_list = json.load(f)
        l = len(server_list)

    global rr_key

    # Continue looping until all requests are processed
    while requests:
        # Obtain server from server list
        server = list(server_list.keys())[rr_key-1]

        # Dummy check if server is available
        server_status = server_list[server]["status"]

        if server_status == "AVAILABLE":
            request = requests.pop(0)

            # Dummy sending to server
            response = send_to_server(request, server_list[server]["address"])
        
        # Advance key
        if rr_key < l:
            rr_key += 1
        else:
            rr_key = 1


def power_distribution(requests):
    with open("servers.json", "r") as f:
        server_list = json.load(f)
        l = len(server_list)

    # Obtain power scores
    power = {x:server_list[x]["power_score"] for x in server_list}

    # Continue looping until all requests are processed
    while requests:
        lowest_power_server = None

        # Find server with lowest power score, check if available, use next lowest if not and so on...
        while power:
            min_power = min(power, key=power.get)

            # Dummy check if server is available
            server_status = server_list[min_power]["status"]

            # Exit loop if server is available and set server, else remove server from power dictionary
            if server_status == "AVAILABLE":
                lowest_power_server = min_power
                break
            else:
                del power[min_power]

        if lowest_power_server:
            request = requests.pop(0)

            # Dummy sending to server
            response = send_to_server(request, server_list[lowest_power_server]["address"])

            # Dummy update power score <- Might need to adjust power scores or smth
            power[lowest_power_server] = power[lowest_power_server] + 10

    # Update power scores
    for server in server_list:
        server_list[server]["power_score"] = power[server]

    with open("servers.json", "w") as f:
        json.dump(server_list, f, indent=4)


def least_connections(requests):
    with open("servers.json", "r") as f:
        server_list = json.load(f)
        l = len(server_list)
    
    # Obtain connections list
    connections = {x:server_list[x]["active_connections"] for x in server_list}

    # Continue looping until all requests are processed
    while requests:
        lowest_connections_server = None

        # Find server with lowest active connections, check if available, use next lowest if not and so on...
        while connections:
            number_connections = {x:len(connections[x]) for x in connections}
            min_connections = min(number_connections, key=number_connections.get)

            # Dummy check if server is available
            server_status = server_list[min_connections]["status"]

            # Exit loop if server is available and set server, else remove server from connections dictionary
            if server_status == "AVAILABLE":
                lowest_connections_server = min_connections
                break
            else:
                del connections[min_connections]

        if lowest_connections_server:
            request = requests.pop(0)
            [request, connection] = request.split(":")

            # Dummy sending to server
            response = send_to_server(request, server_list[lowest_connections_server]["address"])

            # Dummy update active connections
            connections[lowest_connections_server].append(connection)

    # Update active connections
    for server in server_list:
        server_list[server]["active_connections"] = connections[server]

    with open("servers.json", "w") as f:
        json.dump(server_list, f, indent=4)


requests = ["REQUEST 1:C6", "REQUEST 2:C7", "REQUEST 3:C8", "REQUEST 4:C9", "REQUEST 5:C10"]
least_connections(requests)
