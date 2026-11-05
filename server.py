"""Local development launcher; deployment uses Gunicorn."""
import os
from socketserver import ThreadingMixIn
from wsgiref.simple_server import WSGIServer,make_server
from app import application
class ThreadedServer(ThreadingMixIn,WSGIServer):
 daemon_threads=True
if __name__=='__main__':
 port=int(os.getenv('PORT','8000'))
 print(f'打开 http://localhost:{port}',flush=True)
 make_server('127.0.0.1',port,application,server_class=ThreadedServer).serve_forever()
