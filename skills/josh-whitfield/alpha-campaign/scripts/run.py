"""Preview or run a bounded batch; keep inputs and receipts outside the package."""
import argparse, json
from pathlib import Path
from install import clay,save

def main():
 p=argparse.ArgumentParser();p.add_argument('--state',required=True,type=Path);p.add_argument('--brief',type=Path);p.add_argument('--audience-brief',default='');p.add_argument('--max-people',type=int,default=5);p.add_argument('--batch-id',default='');p.add_argument('--memory',type=Path);p.add_argument('--feedback',type=Path);p.add_argument('--start',action='store_true');p.add_argument('--status',metavar='RUN_ID');p.add_argument('--process-queue-from',metavar='RUN_ID');p.add_argument('--results-from',metavar='RUN_ID');p.add_argument('--output',type=Path);p.add_argument('--record-ids',help='Optional comma-separated subset of this parent run, for a bounded canary or continuation')
 a=p.parse_args();s=json.loads(a.state.read_text());wf=s['parent']['workflow_id']
 if str(clay('whoami')['workspace']['id'])!=str(s['workspace_id']):raise ValueError('Workspace mismatch')
 if a.results_from:
  import sys
  sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'references'))
  from pipeline import reconcile
  run=clay('workflows','runs','get',wf,a.results_from,'--verbose')
  if run['status']!='completed':raise ValueError('Parent incomplete; inspect native errors and partial queue receipts')
  queue=next((n['outputs'] for n in run.get('nodes',[]) if n['nodeId']==s['parent']['nodes']['queue_prepare']),None)
  if queue is None:raise ValueError('No queue ledger; inspect the empty-source or earlier native result')
  receipt=next((n['outputs'] for n in run['nodes'] if n['nodeId']==s['parent']['nodes']['results']),{})
  ids=[str(r['result']['entityId']) for r in receipt.get('queue_receipts',[]) if r.get('success') is True]
  if len(ids)>100:raise ValueError('Unexpected queue count')
  fields={k:v['id'] for k,v in s['audience']['fields'].items()};expected={e['candidate_id']:e for e in queue['entries']};results=[]
  for offset in range(0,len(ids),50):
   rows=clay('audiences','records','get','--entity-type','people','--ids',','.join(ids[offset:offset+50]))['data']
   for row in rows:
    values=row['fields'];lead=json.loads(values[fields['lead']]);entry=expected.get(lead['candidate_id'])
    if not entry or values.get(fields['lead'])!=entry['lead'] or values.get(fields['brief'])!=entry['brief']:continue
    if values.get(fields['status'])=='QUEUED':
     results.append({'candidate_id':lead['candidate_id'],'name':lead['name'],'status':'QUEUED','reason':'Awaiting a terminal helper result; inspect its native run','subject':'','body':''})
    else:
     result=json.loads(values.get(fields['evidence']) or '{}')
     if result.get('status')!=values.get(fields['status']):continue
     results.append(result)
  class Context:
   def get_input(self,key):return {'dispatch':queue,'results':results}.get(key)
  result=reconcile(Context())
  if any(r['status']=='QUEUED' for r in result['people']):result['status']='BATCH_PROCESSING_OR_UNRESOLVED'
  elif any(r['status']=='PIPELINE_ERROR' for r in result['people']):result['status']='BATCH_RECONCILIATION_REQUIRED'
  if a.output:save(a.output,result)
  print(json.dumps(result,indent=2));return
 if a.process_queue_from:
  if not a.output or a.output.exists():raise ValueError('Use a new private --output receipt; inspect any existing receipt before retrying')
  run=clay('workflows','runs','get',wf,a.process_queue_from,'--verbose')
  if run['status']!='completed':raise ValueError('Parent has not completed; inspect its failed or active stages first')
  terminal=next((n['outputs'] for n in run.get('nodes',[]) if n['nodeId']==s['parent']['nodes']['results']),{})
  if terminal.get('status')!='QUEUED_FOR_NATIVE_PROCESSING':raise ValueError('No reconciled queue receipt in this parent run')
  ids=[str(r['result']['entityId']) for r in terminal['queue_receipts'] if r.get('success') is True]
  if len(ids)!=len(set(ids)) or not 1<=len(ids)<=100:raise ValueError('Queue count or identity conflict')
  if a.record_ids:
   selected=a.record_ids.split(',')
   if len(selected)!=len(set(selected)) or not set(selected).issubset(ids):raise ValueError('Select unique exact record IDs queued by this parent run')
   ids=selected
  audience=s['audience'];fields={k:v['id'] for k,v in audience['fields'].items()}
  source=next(n['outputs'] for n in run['nodes'] if n['nodeId']==s['parent']['nodes']['queue_prepare'])
  expected={json.loads(e['lead'])['candidate_id']:e for e in source['entries']}
  for offset in range(0,len(ids),50):
   rows=clay('audiences','records','get','--entity-type','people','--ids',','.join(ids[offset:offset+50]))['data']
   if len(rows)!=len(ids[offset:offset+50]):raise ValueError('Queued records missing')
   for row in rows:
    values=row['fields'];lead=json.loads(values[fields['lead']]);entry=expected.get(lead['candidate_id'])
    if not entry or values.get(fields['status'])!='QUEUED' or values.get(fields['lead'])!=entry['lead'] or values.get(fields['brief'])!=entry['brief']:
     raise ValueError('Queue changed or was already processed; inspect before retrying')
  receipt={'parent_run':a.process_queue_from,'record_ids':ids,'starts':[],'status':'PREVIEW'}
  print(json.dumps(receipt))
  if not a.start:return
  receipt['status']='STARTING';save(a.output,receipt)
  for offset in range(0,len(ids),50):
   ack=clay('workflows','runs','test',s['child']['workflow_id'],'--audience-segment',audience['pending']['id'],'--record-ids',','.join(ids[offset:offset+50]))
   receipt['starts'].append({'record_ids':ids[offset:offset+50],'ack':ack});save(a.output,receipt)
  receipt['status']='EXECUTION_REQUESTED_VERIFY_RUN_ID';save(a.output,receipt)
  print('Verify a new helper run ID. If this draft only staged Test data, run the exact queued rows in the Clay helper test panel. Do not rerun old samples. Reconcile terminal Audience results.');return
 if a.status:
  result=clay('workflows','runs','get',wf,a.status,'--verbose')
  if a.output:save(a.output,result)
  print(json.dumps(result,indent=2));return
 if not a.brief:raise ValueError('Provide --brief')
 if not 1<=a.max_people<=100:raise ValueError('max-people must be 1–100')
 brief=json.loads(a.brief.read_text());inputs={'brief_json':json.dumps(brief),'audience_brief':a.audience_brief,'max_people':a.max_people,'batch_id':a.batch_id,
  'memory_json':a.memory.read_text() if a.memory else '', 'feedback_json':a.feedback.read_text() if a.feedback else ''}
 if any(k in brief for k in ['api_key','apiKey','token','secret','authorization']):raise ValueError('Credentials belong in secure Clay connections')
 print(json.dumps({'inputs':inputs,'will_start':a.start,'sends_email':False},indent=2))
 if a.start:
  if not a.output:raise ValueError('Provide --output to preserve the run receipt before starting')
  if a.output.exists():raise ValueError('Receipt already exists; inspect that run, do not accidentally restart it')
  result=clay('workflows','runs','test',wf,'--inputs',json.dumps(inputs));save(a.output,result);print(json.dumps(result))
if __name__=='__main__':main()
