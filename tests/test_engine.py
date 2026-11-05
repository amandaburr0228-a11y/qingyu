import unittest
from unittest.mock import patch
from engine import run
class Tests(unittest.TestCase):
 def test_low(self):
  d=run('考试失败了',[],5);self.assertEqual(d['risk']['level'],'低');self.assertEqual(d['knowledge'][0]['id'],'CBT-01')
 def test_override(self):
  d=run('我想死',[],9);self.assertEqual(d['risk']['level'],'高');self.assertEqual(d['knowledge'],[]);self.assertEqual(d['trace'][-1]['agent'],'转介 Agent')
 def test_indirect(self):self.assertEqual(run('我想彻底消失',[],8)['risk']['level'],'中')
 def test_progression(self):
  h=[]
  for i in range(8):
   d=run('最近不想动',h,5);h.append(dict(d,text='最近不想动'))
  self.assertEqual(d['stage'],'巩固与预防');self.assertEqual(d['knowledge'][0]['id'],'BA-01')
 def test_disagreement(self):
  with patch('engine.model',return_value='{"level":"高","reason":"隐性风险"}'):
   self.assertEqual(run('活着有些累',[],5)['risk']['level'],'高')
 def test_context_persistence(self):
  first=run('最近什么都不想做，只想躺着',[],5)
  follow=run('已经有几天了',[dict(first,text='最近什么都不想做，只想躺着')],5)
  self.assertEqual(follow['knowledge'][0]['id'],'BA-01')
  self.assertNotEqual(first['reply'],follow['reply'])
 def test_safety_continuity(self):
  d=run('我想死',[],9)
  follow=run('好的',[dict(d,text='我想死')],5)
  self.assertEqual(follow['stage'],'安全支持')
 def test_model_failure(self):
  with patch('engine.model',side_effect=TimeoutError):
   d=run('我想消失',[],8);self.assertEqual(d['stage'],'安全支持')
if __name__=='__main__':unittest.main()
