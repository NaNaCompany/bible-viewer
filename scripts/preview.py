"""Serve the app at its real project path; block tracking during local QA."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
import argparse

ROOT=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        if path.startswith('/bible-viewer/'):
            path=path[len('/bible-viewer'):]
        return super().translate_path(path)
    def end_headers(self):
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-src 'none'; object-src 'none'")
        super().end_headers()
    def log_message(self,format,*args): pass
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8769);args=parser.parse_args()
    print(f'Local: http://127.0.0.1:{args.port}/bible-viewer/',flush=True)
    ThreadingHTTPServer(('127.0.0.1',args.port),partial(Handler,directory=str(ROOT/'docs'))).serve_forever()
