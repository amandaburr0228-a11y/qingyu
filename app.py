"""WSGI deployment entry point. Ephemeral sessions; no conversation persistence."""
import hmac,json,mimetypes,os,secrets,threading,time
from http.cookies import SimpleCookie
from pathlib import Path
from engine import run,KB
ROOT=Path(__file__).parent/'web'
_sessions={};_lock=threading.Lock();_slots=threading.BoundedSemaphore(4)
def application(env,start):
 def respond(code,obj,extra=()):
  data=json.dumps(obj,ensure_ascii=False).encode() if not isinstance(obj,bytes) else obj
  start(code,[('Content-Type','application/json; charset=utf-8'),('Content-Length',str(len(data))),('Cache-Control','no-store'),('X-Content-Type-Options','nosniff')]+list(extra));return [data]
 path=env.get('PATH_INFO','/');method=env.get('REQUEST_METHOD','GET')
 if method=='GET' and path=='/health':return respond('200 OK',{'status':'ok'})
 if method=='GET' and path=='/api/status':return respond('200 OK',dict(modelConfigured=bool(os.getenv('LLM_API_KEY')),accessRequired=bool(os.getenv('DEMO_ACCESS_CODE'))))
 if method=='GET' and path=='/api/knowledge':return respond('200 OK',KB)
 if method=='POST' and path=='/api/chat':
  code=os.getenv('DEMO_ACCESS_CODE','')
  if code and not hmac.compare_digest(env.get('HTTP_X_DEMO_CODE','').encode(),code.encode()):return respond('401 Unauthorized',{'error':'请输入正确的演示访问码'})
  if os.getenv('LLM_API_KEY') and not code and os.getenv('ALLOW_PUBLIC_MODEL')!='true':return respond('503 Service Unavailable',{'error':'请先在服务器设置 DEMO_ACCESS_CODE'})
  try:
   size=int(env.get('CONTENT_LENGTH') or 0)
   if not 0<size<100000:raise ValueError()
   obj=json.loads(env['wsgi.input'].read(size));text=obj['text'];intensity=obj.get('intensity',5)
   if not isinstance(text,str) or not 0<len(text.strip())<=3000 or type(intensity)!=int or not 0<=intensity<=10:raise ValueError()
  except (ValueError,KeyError,TypeError):return respond('400 Bad Request',{'error':'输入格式不正确'})
  cookie=SimpleCookie()
  try:cookie.load(env.get('HTTP_COOKIE',''))
  except Exception:pass
  sid=cookie['qingyu_session'].value if 'qingyu_session' in cookie else ''
  now=time.monotonic()
  with _lock:
   for key in list(_sessions):
    if now-_sessions[key]['updated']>3600:del _sessions[key]
   if sid not in _sessions:
    if sid and obj.get('newSession') is not True:return respond('409 Conflict',{'error':'会话已过期或服务已重启，请点击开启新对话'})
    if len(_sessions)>=200:return respond('503 Service Unavailable',{'error':'演示服务繁忙'})
    sid=secrets.token_urlsafe(32);_sessions[sid]=dict(history=[],updated=now,last=0,lock=threading.Lock())
   session=_sessions[sid]
  secure='; Secure' if env.get('wsgi.url_scheme')=='https' or env.get('HTTP_X_FORWARDED_PROTO')=='https' else ''
  headers=[('Set-Cookie',f'qingyu_session={sid}; HttpOnly; SameSite=Strict; Path=/; Max-Age=3600'+secure)]
  if not session['lock'].acquire(False):return respond('429 Too Many Requests',{'error':'上一轮仍在处理中'})
  acquired=False
  try:
   if now-session['last']<2:return respond('429 Too Many Requests',{'error':'请稍等两秒再发送'})
   acquired=_slots.acquire(False)
   if not acquired:return respond('503 Service Unavailable',{'error':'演示服务繁忙，请稍后重试'})
   session['last']=now;session['updated']=now
   if obj.get('newSession') is True:session['history']=[]
   result=run(text,session['history'],intensity)
   session['history']=(session['history']+[dict(result,text=text)])[-24:]
   return respond('200 OK',result,headers)
  except Exception:return respond('500 Internal Server Error',{'error':'本轮处理失败，请稍后重试'})
  finally:
   if acquired:_slots.release()
   session['lock'].release()
 if method=='GET' and path in ['/', '/index.html','/style.css','/app.js']:
  file=ROOT/('index.html' if path=='/' else path[1:]);data=file.read_bytes();start('200 OK',[('Content-Type',(mimetypes.guess_type(str(file))[0] or 'text/plain')+'; charset=utf-8'),('Content-Length',str(len(data))),('X-Content-Type-Options','nosniff')]);return [data]
 return respond('404 Not Found',{'error':'不存在'})
