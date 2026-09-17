"""Install the bundled graph using the installer's authenticated Clay CLI."""
import argparse, hashlib, json, subprocess
from pathlib import Path

def clay(*args):
    p=subprocess.run(['clay',*args],capture_output=True,text=True)
    if p.returncode: raise RuntimeError(p.stdout+p.stderr)
    value=json.loads(p.stdout)
    if any(not x.get('success') for x in value.get('appliedUpdates',[])): raise RuntimeError(value)
    return value

def replace(value, ids):
    if isinstance(value,str) and value.startswith('NODE:'): return ids[value[5:]]
    if isinstance(value,dict): return {k:replace(v,ids) for k,v in value.items()}
    if isinstance(value,list): return [replace(v,ids) for v in value]
    return value

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2))

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--state',type=Path,required=True,help='Local installation receipt OUTSIDE the skill package')
    p.add_argument('--workspace',required=True,help='Exact workspace ID read from clay whoami')
    p.add_argument('--name',default='Alpha Radar — Adaptive Evidence & Learning')
    p.add_argument('--create',action='store_true',help='Create the graph; omission only previews')
    args=p.parse_args()
    package=Path(__file__).resolve().parents[1]
    if args.state.resolve().is_relative_to(package): raise ValueError('Keep installation receipts outside the portable package')
    graph_bytes=(package/'references/blueprint.json').read_bytes()
    graph=json.loads(graph_bytes); digest=hashlib.sha256(graph_bytes).hexdigest()
    identity=clay('whoami'); workspace=identity['workspace']
    if str(workspace['id'])!=args.workspace: raise ValueError('Active workspace differs from the requested workspace')
    print(json.dumps({'workspace':workspace,'nodes':len(graph['nodes'])+1,'name':args.name,'will_run':False,'will_publish':False}))
    if not args.create: return
    state=json.loads(args.state.read_text()) if args.state.exists() else {}
    if state and (state['workspace_id']!=args.workspace or state['blueprint_sha256']!=digest):
        raise ValueError('Existing receipt is for another workspace or graph version; use a new receipt path')
    if not state:
        workflow=clay('workflows','create','--name',args.name)
        state={'workspace_id':args.workspace,'workflow_id':workflow['id'],'url':workflow['url'],'blueprint_sha256':digest,'nodes':{}}
        save(args.state,state)
    wf=state['workflow_id']; ids=state['nodes']
    if 'trigger' not in ids:
        if not state.get('trigger_id'):
            created=clay('workflows','triggers','create',wf,'--input',json.dumps(graph['trigger']))
            state['trigger_id']=created['resourceId'];save(args.state,state)
        trigger=clay('workflows','triggers','get',state['trigger_id'])
        ids['trigger']=trigger['workflowNodeId'];save(args.state,state)
    for row in graph['nodes']:
        if row['key'] in ids: continue
        spec=replace(row['spec'],ids)
        if spec.get('nodeType')=='agent':
            spec['agentName']=spec['name']+' / '+wf
        result=clay('workflows','nodes','create',wf,'--input',json.dumps(spec))
        ids[row['key']]=result['nodeId'];save(args.state,state)
        print('Created '+spec['name'],flush=True)
    checked=clay('workflows','graph','validate',wf)
    if not checked.get('valid'): raise RuntimeError(checked)
    clay('workflows','graph','format',wf)
    print(json.dumps({'status':'DRAFT_CREATED','url':state['url'],'state':str(args.state)}))

if __name__=='__main__':main()
