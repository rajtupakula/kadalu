import os
import json
import socket
import uuid
import logging

from kadalulib import (execute, CommandException)

SOCKET_FILE_PATH = "/var/run/vmexec-socket/vmexec.sock"
GLUSTERFS_CMD = "/usr/sbin/glusterfs"
MOUNT_CMD = "/usr/bin/mount"
UNMOUNT_CMD = "/usr/bin/umount"
HOSTVOL_MOUNTDIR = "/mnt/kadalu"
is_connected = False

cmdList = ["glusterfs", "/mount", "/umount", "findmnt", "losetup"]

def connectSocket(client_socket):
    retry_interval = 60
    max_retries = 5

    retry_count = 0
    connected = False
    while retry_count < max_retries and not connected:
        try:
            # Attempt to connect to the server
            client_socket.connect(SOCKET_FILE_PATH)
            connected = True
            logging.info("Connected to the server!")
            break
        except ConnectionRefusedError:
            # Connection refused, wait for a while before retrying
            logging.info("Connection refused. Retrying in seconds..." + str(retry_interval))
            time.sleep(retry_interval)
            retry_count += 1

    logging.info("the connection state is " + str(connected))
    return connected

def parseCommand(commandList):
    if "glusterfs" in commandList[0]:
        commandList[0] = GLUSTERFS_CMD
    elif "/mount" in commandList[0]:
        commandList[0] = MOUNT_CMD
    elif "/umount" in commandList[0]:
        commandList[0] = UNMOUNT_CMD
        
    return " ".join(commandList)

def socketClient(commandList):
    cmd = parseCommand(commandList)
    logging.info("the command is ")
    logging.info(cmd)
    global is_connected
    client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    json_data = json.dumps({
        "error" : "Unable to execute command",
        "result": 1,
        "output" : ""
    })

    if not is_connected :
        logging.info("socket not connected " + str(is_connected))
        is_connected = connectSocket(client_socket)

    if not is_connected:
        logging.error("Unable to connect to the server after max retries.")
        json_data["error"] = "Unable to connect to the server for command execution after max retries."
    else:
        try:
            logging.info("Seding the data to socket server for cmd execution")
            
            data = {
                "id" : str(uuid.uuid4()),
                "commandtype" : 4,
                "command" : cmd,
                "hidden" : False,
                "commandtimeout" : 100,
                "nodelist" : [""]
            }
            json_inp = json.dumps(data)
            client_socket.sendall(json_inp.encode('utf-8'))

            #receive a response from the server
            response = client_socket.recv(1024).decode('utf-8')
            json_data = json.loads(response)
        finally:
            # Close the connection
            client_socket.close()
            is_connected = False
    if len(json_data['error']) != 0 :
                raise CommandException(json_data['result'], json_data['output'], json_data['error'])
    return (json_data["output"], json_data["error"], json_data['result'])

def executeCommand(*cmd):
    logging.info("In execute command method to check command is glusterfs or mount or umount")
    head = cmd[0]
    logging.info(head)
    if any(cmdStr in head for cmdStr in cmdList):
        logging.info("The command is glusterfs or mount or umount")
        return socketClient(list(cmd))
    else:
        return execute(*cmd)
