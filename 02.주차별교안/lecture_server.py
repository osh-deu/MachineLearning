"""Serve course HTML files on localhost so YouTube receives a valid referrer."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse, hashlib, json, threading, time, urllib.request, webbrowser
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parent
LECTURE=ROOT/'강의교안_목차.html'
IDENTITY=hashlib.sha256(str(ROOT).encode()).hexdigest()
last_seen=time.monotonic()

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_GET(self):
        global last_seen
        last_seen=time.monotonic()
        if self.path.split('?')[0]=='/__lecture_ping':
            data=json.dumps({'lecture':IDENTITY}).encode();ctype='application/json'
        else:
            name=unquote(urlsplit(self.path).path).lstrip('/')
            target=(ROOT/name).resolve() if name else LECTURE
            if not target.is_relative_to(ROOT) or target.suffix.lower()!='.html' or not target.is_file():
                self.send_error(404);return
            data=target.read_bytes();ctype='text/html; charset=utf-8'
        self.send_response(200);self.send_header('Content-Type',ctype)
        self.send_header('Content-Length',str(len(data)))
        self.send_header('Referrer-Policy','strict-origin-when-cross-origin')
        self.send_header('Cache-Control','no-store');self.end_headers()
        try:self.wfile.write(data)
        except (BrokenPipeError,ConnectionResetError):pass

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--no-browser',action='store_true');args=parser.parse_args()
    for port in range(8870,8890):
        url=f'http://127.0.0.1:{port}'
        try:
            with urllib.request.urlopen(url+'/__lecture_ping',timeout=.25) as r:
                if json.load(r).get('lecture')==IDENTITY:
                    if not args.no_browser:webbrowser.open(url+'/')
                    print(url,flush=True);return
        except Exception:pass
        try:server=ThreadingHTTPServer(('127.0.0.1',port),Handler);break
        except OSError:continue
    else:raise RuntimeError('No available lecture server port (8870-8889).')
    def idle_stop():
        while True:
            time.sleep(60)
            if time.monotonic()-last_seen>7200:server.shutdown();return
    threading.Thread(target=idle_stop,daemon=True).start()
    if not args.no_browser:webbrowser.open(url+'/')
    print(url,flush=True)
    try:server.serve_forever()
    finally:server.server_close()

if __name__=='__main__':main()
