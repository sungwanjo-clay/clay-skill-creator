"""Install a self-contained native batch workflow and its per-person helper."""
import argparse, hashlib, json, subprocess
from pathlib import Path
import build

def clay(*args):
 r=subprocess.run(['clay',*args],capture_output=True,text=True)
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 v=json.loads(r.stdout)
 if any(not a.get('success') for a in v.get('appliedUpdates',[])):raise RuntimeError(v)
 return v

def replace(value,ids):
 if isinstance(value,str) and value.startswith('NODE:'):return ids[value[5:]]
 if isinstance(value,dict):return {k:replace(v,ids) for k,v in value.items()}
 if isinstance(value,list):return [replace(v,ids) for v in value]
 return value

def save(path,state):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(state,indent=2))

def install_graph(graph,state,path,name):
 digest=hashlib.sha256(json.dumps(graph,sort_keys=True).encode()).hexdigest()
 if state.get('blueprint_sha256') not in (None,digest):raise ValueError('Graph differs from receipt. Inspect the installation before changing it.')
 state['blueprint_sha256']=digest
 if not state.get('workflow_id'):
  w=clay('workflows','create','--name',name);state.update(workflow_id=w['id'],url=w['url'],nodes={});save(path,state)
 ids=state['nodes'];wf=state['workflow_id']
 if 'trigger' not in ids:
  if not state.get('trigger_id'):
   state['trigger_id']=clay('workflows','triggers','create',wf,'--input',json.dumps(graph['trigger']))['resourceId'];save(path,state)
  ids['trigger']=clay('workflows','triggers','get',state['trigger_id'])['workflowNodeId'];save(path,state)
 for n in graph['nodes']:
  if n['key'] in ids:continue
  spec=replace(n['spec'],ids)
  if spec.get('nodeType')=='agent':spec['agentName']=spec['name']+' / '+wf
  created=clay('workflows','nodes','create',wf,'--input',json.dumps(spec));ids[n['key']]=created['nodeId'];save(path,state)
  print('Created '+spec['name'],flush=True)
 result=clay('workflows','graph','validate',wf)
 if not result.get('valid'):raise RuntimeError(result)
 clay('workflows','graph','format',wf)
 state['snapshot_id']=clay('workflows','snapshots','list',wf)['data'][0]['id'];save(path,state)
 return state

def install_audience(path):
 state=json.loads(path.read_text()) if path.exists() else {'fields':{}}
 fields={'lead':('Alpha Campaign · Person context','text'),'brief':('Alpha Campaign · Writing brief','text'),'status':('Alpha Campaign · Status','text'),'email':('Alpha Campaign · Verified email','email'),'subject':('Alpha Campaign · Subject','text'),'body':('Alpha Campaign · Draft','text'),'evidence':('Alpha Campaign · Evidence and holds','text'),'batch':('Alpha Campaign · Batch','text'),'person':('Alpha Campaign · Person','text')}
 catalog=clay('audiences','fields','list','--entity-type','people')
 existing=catalog.get('data',catalog.get('fields',[]))
 for key,(name,typ) in fields.items():
  if key not in state['fields']:
   if any(v.get('name')==name for v in existing):raise ValueError('Owned field already exists. Recover its installation receipt instead of creating a conflicting installation: '+name)
   state['fields'][key]=clay('audiences','fields','create','--entity-type','people','--name',name,'--data-type',typ);save(path,state)
 fid=state['fields']['status']['id']
 for key,name,op,value in [('pending','Alpha Campaign — Processing queue','Equal','QUEUED'),('review','Alpha Campaign — Review results','NotEmpty',None)]:
  if key not in state:
   clause={'type':'BinOp','key':fid,'dataPath':['contact_entity_field_values','field',fid],'operator':op,'entityType':'CONTACT'}
   if value is not None:clause['value']=value
   state[key]=clay('audiences','create','--entity-type','people','--name',name,'--filter',json.dumps({'type':'GroupOp','combinationMode':'And','items':[clause]}));save(path,state)
 return state

def main():
 p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--state',type=Path,required=True);p.add_argument('--create',action='store_true');p.add_argument('--exa-account')
 a=p.parse_args();package=Path(__file__).resolve().parents[1]
 if a.state.resolve().is_relative_to(package):raise ValueError('Keep installation receipts outside the package')
 if str(clay('whoami')['workspace']['id'])!=a.workspace:raise ValueError('Workspace mismatch')
 print(json.dumps({'max_people':100,'will_run':False,'will_publish':False,'creates_owned_audience_fields':9,'optional_exa':bool(a.exa_account)}))
 if not a.create:return
 audiencepath=a.state.with_name(a.state.stem+'-audience.json')
 audience=install_audience(audiencepath)
 child=build.child(audience,a.exa_account)
 childpath=a.state.with_name(a.state.stem+'-child.json');parentpath=a.state.with_name(a.state.stem+'-parent.json')
 childstate=json.loads(childpath.read_text()) if childpath.exists() else {}
 childstate=install_graph(child,childstate,childpath,'Alpha Campaign — Per-Person Email and Copy')
 parent=build.parent(audience);parentstate=json.loads(parentpath.read_text()) if parentpath.exists() else {}
 parentstate=install_graph(parent,parentstate,parentpath,'Alpha Campaign — Source to Verified Outreach')
 result={'workspace_id':a.workspace,'parent':parentstate,'child':childstate,'optional_exa':bool(a.exa_account),'audience':audience};save(a.state,result)
 print(json.dumps({'status':'DRAFT_CREATED','url':parentstate['url'],'child_url':childstate['url']}))
if __name__=='__main__':main()
