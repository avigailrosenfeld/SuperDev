"""Proxy server: serves chat.html + forwards /api/* to Copilot Studio."""
import json
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

TOKEN   = os.environ.get("AAD_TOKEN", "")
BOT_URL = 'https://default2be2a2393b714ff18947f86d59e166.e0.environment.api.powerplatform.com/copilotstudio/dataverse-backed/authenticated/bots/ca_agent'
API_VER = 'api-version=2022-03-01-preview'
PORT    = 8080


class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(fmt % args, flush=True)

    def _respond(self, status, body=b'', content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_OPTIONS(self):
        self._respond(204)

    def do_GET(self):
        if self.path in ('/', '/chat.html'):
            with open('chat.html', 'rb') as f:
                self._respond(200, f.read(), 'text/html; charset=utf-8')
        elif self.path.startswith('/api'):
            self._proxy('GET', self.path[4:] or '/conversations')
        else:
            self._respond(404, b'Not found')

    def do_POST(self):
        if self.path.startswith('/api'):
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length) if length else b''
            self._proxy('POST', self.path[4:] or '/conversations', body)
        else:
            self._respond(404, b'Not found')

    def _proxy(self, method, path, body=None):
        sep = '&' if '?' in path else '?'
        url = BOT_URL + path + sep + API_VER
        print(f'PROXY {method} {url}', flush=True)
        try:
            req = urllib.request.Request(url, data=body, method=method)
            req.add_header('Authorization', f'Bearer {TOKEN}')
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                print(f'  <- {resp.status}', flush=True)
                self._respond(resp.status, data)
        except urllib.error.HTTPError as e:
            data = e.read()
            print(f'  <- HTTP {e.code}: {data[:300]}', flush=True)
            self._respond(e.code, data)
        except Exception as e:
            print(f'  <- ERROR: {e}', flush=True)
            self._respond(502, json.dumps({'error': str(e)}).encode())


if __name__ == '__main__':
    print(f'SuperDev chat proxy on http://localhost:{PORT}', flush=True)
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
