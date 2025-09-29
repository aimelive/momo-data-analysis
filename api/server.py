
import http.server
import json
import base64
import os
from urllib.parse import urlparse, parse_qs
from http import HTTPStatus
import threading

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'transactions.json')
# Simple credentials for Basic Auth (use only for assignment/testing)
AUTH_USER = 'devsquad'
AUTH_PASS = 'devsquadpass'

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(records):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

def check_auth(headers):
    auth = headers.get('Authorization')
    if not auth or not auth.startswith('Basic '):
        return False
    try:
        token = auth.split(' ',1)[1].strip()
        decoded = base64.b64decode(token).decode('utf-8')
        user, pwd = decoded.split(':',1)
        return user == AUTH_USER and pwd == AUTH_PASS
    except Exception:
        return False

class SimpleAPIHandler(http.server.BaseHTTPRequestHandler):
    def _unauthorized(self):
        self.send_response(HTTPStatus.UNAUTHORIZED)
        self.send_header('WWW-Authenticate', 'Basic realm="MoMo API"')
        self.end_headers()

    def _parse_id(self):
        parts = self.path.rstrip('/').split('/')
        if len(parts) >= 3 and parts[-2] == 'transactions':
            return parts[-1]
        return None

    def _read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        if length:
            return self.rfile.read(length).decode('utf-8')
        return ''

    def do_AUTH(self):
        if not check_auth(self.headers):
            self._unauthorized()
            return False
        return True

    def do_GET(self):
        if not self.do_AUTH():
            return
        if self.path == '/transactions' or self.path == '/transactions/':
            records = load_data()
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(records).encode('utf-8'))
            return
        # single resource
        if self.path.startswith('/transactions/'):
            tid = self._parse_id()
            if not tid:
                self.send_response(HTTPStatus.BAD_REQUEST); self.end_headers(); return
            records = load_data()
            found = next((r for r in records if r.get('transaction_id') == tid), None)
            if found:
                self.send_response(HTTPStatus.OK)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(found).encode('utf-8'))
            else:
                self.send_response(HTTPStatus.NOT_FOUND); self.end_headers()
            return
        self.send_response(HTTPStatus.NOT_FOUND); self.end_headers()

    def do_POST(self):
        if not self.do_AUTH():
            return
        if self.path != '/transactions':
            self.send_response(HTTPStatus.NOT_FOUND); self.end_headers(); return
        body = self._read_body()
        try:
            obj = json.loads(body)
        except:
            self.send_response(HTTPStatus.BAD_REQUEST); self.end_headers(); return
        records = load_data()
        # ensure transaction_id provided and unique
        tid = obj.get('transaction_id')
        if not tid:
            self.send_response(HTTPStatus.BAD_REQUEST)
            self.end_headers()
            return
        if any(r.get('transaction_id') == tid for r in records):
            self.send_response(HTTPStatus.CONFLICT)
            self.end_headers()
            return
        records.append(obj)
        save_data(records)
        self.send_response(HTTPStatus.CREATED)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode('utf-8'))

    def do_PUT(self):
        if not self.do_AUTH():
            return
        if not self.path.startswith('/transactions/'):
            self.send_response(HTTPStatus.NOT_FOUND); self.end_headers(); return
        tid = self._parse_id()
        if not tid:
            self.send_response(HTTPStatus.BAD_REQUEST); self.end_headers(); return
        body = self._read_body()
        try:
            obj = json.loads(body)
        except:
            self.send_response(HTTPStatus.BAD_REQUEST); self.end_headers(); return
        records = load_data()
        for i,r in enumerate(records):
            if r.get('transaction_id') == tid:
                # update record fields shallowly
                r.update(obj)
                records[i] = r
                save_data(records)
                self.send_response(HTTPStatus.OK)
                self.send_header('Content-Type','application/json')
                self.end_headers()
                self.wfile.write(json.dumps(r).encode('utf-8'))
                return
        self.send_response(HTTPStatus.NOT_FOUND); self.end_headers()

    def do_DELETE(self):
        if not self.do_AUTH():
            return
        if not self.path.startswith('/transactions/'):
            self.send_response(HTTPStatus.NOT_FOUND); self.end_headers(); return
        tid = self._parse_id()
        if not tid:
            self.send_response(HTTPStatus.BAD_REQUEST); self.end_headers(); return
        records = load_data()
        new = [r for r in records if r.get('transaction_id') != tid]
        if len(new) == len(records):
            self.send_response(HTTPStatus.NOT_FOUND); self.end_headers(); return
        save_data(new)
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

def run(server_class=http.server.ThreadingHTTPServer, handler_class=SimpleAPIHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Serving on 0.0.0.0:{port} ... (Basic Auth user={AUTH_USER})")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down")
        httpd.server_close()

if __name__ == '__main__':
    run()
