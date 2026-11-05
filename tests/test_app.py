import io,json,unittest
from unittest.mock import patch
import app
class APITest(unittest.TestCase):
 def call(self,path,method='GET',body=None,cookie=''):
  data=json.dumps(body).encode() if body is not None else b'';status=[];headers=[]
  def start(s,h):status.append(s);headers.extend(h)
  result=b''.join(app.application({'PATH_INFO':path,'REQUEST_METHOD':method,'CONTENT_LENGTH':str(len(data)),'wsgi.input':io.BytesIO(data),'HTTP_COOKIE':cookie},start))
  return status[0],dict(headers),json.loads(result)
 def test_health(self):self.assertEqual(self.call('/health')[0],'200 OK')
 def test_bad_body(self):self.assertEqual(self.call('/api/chat','POST',{})[0],'400 Bad Request')
 def test_secret_required(self):
  with patch.dict('os.environ',{'DEMO_ACCESS_CODE':'test-code'}):self.assertEqual(self.call('/api/chat','POST',{'text':'hello'})[0],'401 Unauthorized')
 def test_authoritative_history(self):
  with patch.dict('os.environ',{'LLM_API_KEY':'','DEMO_ACCESS_CODE':''}):
   s,h,d=self.call('/api/chat','POST',{'text':'我想伤害自己','intensity':9})
   self.assertEqual(d['risk']['level'],'高')
   cookie=h['Set-Cookie'].split(';')[0]
   with patch('app.time.monotonic',return_value=__import__('time').monotonic()+3):
    s,h,d=self.call('/api/chat','POST',{'text':'好的','intensity':5,'history':[]},cookie)
   self.assertEqual(d['stage'],'安全支持')
 def test_no_source_files(self):self.assertEqual(self.call('/engine.py')[0],'404 Not Found')
