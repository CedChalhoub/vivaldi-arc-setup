# Minimal CDP client (stdlib only): evaluates a JS expression in Vivaldi's UI page.
# usage: python3 -I cdp.py '<js expression>'   or   python3 -I cdp.py -f file.js   (TGT=main.html to target the UI bundle)
import base64, json, os, socket, struct, sys, urllib.request
from urllib.parse import urlparse

PORT = 9333
targets = json.load(urllib.request.urlopen(f"http://localhost:{PORT}/json"))
page = next(t for t in targets if t["type"] in ("app", "page") and os.environ.get("TGT", "/window.html") in t["url"])
u = urlparse(page["webSocketDebuggerUrl"])
s = socket.create_connection((u.hostname, u.port))
key = base64.b64encode(os.urandom(16)).decode()
s.sendall((f"GET {u.path} HTTP/1.1\r\nHost: {u.netloc}\r\nUpgrade: websocket\r\n"
           f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
buf = b""
while b"\r\n\r\n" not in buf:
    buf += s.recv(4096)
buf = buf.split(b"\r\n\r\n", 1)[1]

def recv_exact(n):
    global buf
    while len(buf) < n:
        buf += s.recv(65536)
    out, buf = buf[:n], buf[n:]
    return out

def send(obj):
    data = json.dumps(obj).encode()
    mask = os.urandom(4)
    n = len(data)
    hdr = bytes([0x81]) + (bytes([0x80 | n]) if n < 126 else bytes([0x80 | 126]) + struct.pack(">H", n) if n < 65536 else bytes([0x80 | 127]) + struct.pack(">Q", n))
    s.sendall(hdr + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

def recv():
    msg = b""
    while True:
        b1, b2 = recv_exact(2)
        n = b2 & 0x7F
        if n == 126: n = struct.unpack(">H", recv_exact(2))[0]
        elif n == 127: n = struct.unpack(">Q", recv_exact(8))[0]
        msg += recv_exact(n)
        if b1 & 0x80:
            return json.loads(msg)

send({"id": 1, "method": "Runtime.evaluate",
      "params": {"expression": open(sys.argv[2]).read() if sys.argv[1] == "-f" else sys.argv[1], "awaitPromise": True, "returnByValue": True}})
while True:
    r = recv()
    if r.get("id") == 1:
        res = r["result"]
        print(json.dumps(res.get("result", {}).get("value", res), indent=1, ensure_ascii=False))
        break
