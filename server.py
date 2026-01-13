"""
OneClick Reels AI - API Server Entry Point
"""
import uvicorn
import socket
import sys

def is_port_available(port: int) -> bool:
    """Check if a port is available."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("0.0.0.0", port))
            return True
        except OSError:
            return False

def find_available_port(start_port: int = 8000, max_attempts: int = 10) -> int:
    """Find an available port starting from start_port."""
    for i in range(max_attempts):
        port = start_port + i
        if is_port_available(port):
            return port
    return start_port

if __name__ == "__main__":
    port = 8000
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    
    if not is_port_available(port):
        new_port = find_available_port(port + 1)
        print(f"[!] Port {port} busy, trying {new_port}")
        port = new_port
    
    print("")
    print("OneClick Reels AI - API Server")
    print("================================")
    print(f"   Server:   http://localhost:{port}")
    print(f"   API Docs: http://localhost:{port}/docs")
    print("")
    
    config = uvicorn.Config(
        "backend.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    server.run()

# Force reload




