"""EdgeOne Python/Flask entry. Internal paths omit the /api routing prefix."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from flask import Flask,request
from werkzeug.wrappers import Response
from _qingyu_app import application
app=Flask(__name__)
@app.route('/status',methods=['GET'])
@app.route('/knowledge',methods=['GET'])
@app.route('/chat',methods=['POST'])
@app.route('/health',methods=['GET'])
def endpoint():
 env=request.environ.copy()
 path=request.path
 env['PATH_INFO']='/health' if path=='/health' else '/api'+path
 return Response.from_app(application,env)
