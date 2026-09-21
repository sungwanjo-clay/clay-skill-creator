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
    p.add_argument('--name',default='Alpha Copy — Evidence Into Relevant Outreach')
    p.add_argument('--create',action='store_true',help='Create the graph; omission only previews')
    p.add_argument('--exa-account',help='Optional explicit Clay HTTP header account ID containing the user-supplied Exa x-api-key; never pass the key itself')
    p.add_argument('--audience',help='Optional existing audience segment ID; creates a dedicated audience installation')
    p.add_argument('--entity-type',choices=['CONTACT','ACCOUNT'])
    p.add_argument('--brief',type=Path,help='Shared settings JSON for audience runs')
    p.add_argument('--field-map',type=Path,help='Confirmed source paths mapped to company/contact input names')
    args=p.parse_args()
    package=Path(__file__).resolve().parents[1]
    if args.state.resolve().is_relative_to(package): raise ValueError('Keep installation receipts outside the portable package')
    graph_bytes=(package/'references/blueprint.json').read_bytes()
    graph=json.loads(graph_bytes)
    if args.exa_account:
        from exa import extend
        graph=extend(graph,args.exa_account)
    if args.audience:
        if not (args.entity_type and args.brief and args.field_map): raise ValueError('Audience installs require entity-type, brief and field-map')
        audience=clay('audiences','get',args.audience)
        if audience['entityType']!={'CONTACT':'people','ACCOUNT':'companies'}[args.entity_type]: raise ValueError('Audience entity type mismatch')
        settings=json.loads(args.brief.read_text()); mapping=json.loads(args.field_map.read_text())
        settings['source_id']=args.audience
        allowed=set(graph['trigger']['inputSchema']['properties'])
        if not isinstance(settings,dict) or set(settings)-allowed: raise ValueError('Shared brief has unknown inputs')
        if not isinstance(mapping,dict) or set(mapping)-{'company_domain','company_name','recipient_name','recipient_role','source_record_id','evidence_json','past_observation_json','current_observation_json','comparison_page_path'}: raise ValueError('Unsupported mapped input')
        if not {'company_domain','source_record_id'}<=set(mapping): raise ValueError('Map domain and record identity')
        if not all(isinstance(v,str) and v.startswith('$.') for v in mapping.values()): raise ValueError('Mappings require confirmed $.object.key paths')
        graph['trigger']={'triggerType':'audience_segment','segmentId':args.audience,'entityType':args.entity_type}
        adapter='SETTINGS = '+repr(settings)+'\nFIELD_MAP = '+repr(mapping)+'\n'+(package/'references/source-adapter.py').read_text()
        first=graph['nodes'][0]['spec'];first['incomingEdges']=[{'sourceNode':'NODE:source_adapter'}]
        for field in first['inputSchema']['properties'].values():field['sourceNodeId']='NODE:source_adapter'
        for row in graph['nodes']:
            if row['key']=='exa_prepare':
                row['spec']['inputSchema']['properties']['comparison_page_path']['sourceNodeId']='NODE:source_adapter'
        graph['nodes'].insert(0,{'key':'source_adapter','spec':{'name':'Source · Map this audience record and shared brief','nodeType':'code','code':adapter,'inputSchema':{'type':'object','properties':{'source_record':{'type':'string','sourceNodeId':'NODE:trigger','sourcePath':'$'}}},'incomingEdges':[{'sourceNode':'NODE:trigger'}]}})
    elif args.entity_type or args.brief or args.field_map:raise ValueError('Source options require --audience')
    graph_bytes=json.dumps(graph,sort_keys=True).encode() if args.audience or args.exa_account else graph_bytes
    digest=hashlib.sha256(graph_bytes).hexdigest()
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
