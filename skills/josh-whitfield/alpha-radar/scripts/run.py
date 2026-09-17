"""Run native Clay research; carry review memory from the prior Clay run, not a lead cache."""
import argparse, json, sys
sys.dont_write_bytecode=True
from pathlib import Path
from install import clay, save

def outputs(run,key):
    for node in run.get('nodes',[]):
        value=node.get('outputs',{})
        if key in value: return value[key]
        if key in value.get('structuredOutputs',{}): return value['structuredOutputs'][key]
    return None

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--state',type=Path,required=True)
    p.add_argument('--brief',help='New audience and objective. Omit only to repeat the preceding brief.')
    p.add_argument('--settings',type=Path,help='Optional JSON settings file outside the package')
    p.add_argument('--like',action='append',default=[],help='Candidate ID or exact name explicitly approved by the human')
    p.add_argument('--dislike',action='append',default=[],help='Candidate ID or exact name explicitly rejected by the human')
    p.add_argument('--start',action='store_true',help='Start the paid native workflow; omission previews')
    p.add_argument('--status',action='store_true',help='Read the last run without starting anything')
    args=p.parse_args();state=json.loads(args.state.read_text());wf=state['workflow_id']
    identity=clay('whoami')
    if str(identity['workspace']['id'])!=state['workspace_id']: raise ValueError('Switch to the installation workspace before continuing')
    prior=clay('workflows','runs','get',wf,state['last_run_id'],'--verbose') if state.get('last_run_id') else None
    if args.status:
        if prior is None: raise ValueError('No run has started')
        print(json.dumps(prior,indent=2));return
    if prior and prior['status'] not in ('completed','failed','cancelled'):
        raise ValueError('The previous run is unresolved. Inspect its status before starting another.')
    old_focus=outputs(prior,'focus') if prior else None
    focus=args.brief or old_focus
    if not focus: raise ValueError('Supply an audience and objective with --brief')
    previous_settings=outputs(prior,'settings_json') if prior else None
    settings=json.loads(args.settings.read_text()) if args.settings else json.loads(previous_settings or '{}')
    memory=json.loads(outputs(prior,'memory_json') or '{}') if prior else {}
    # Score output contains the updated memory; choose it ahead of the input-memory node.
    if prior:
        for node in prior.get('nodes',[]):
            if node.get('nodeId')==state['nodes']['score']:
                memory=json.loads(node.get('outputs',{}).get('memory_json','{}'))
    same_brief=' '.join(focus.lower().split())==' '.join((old_focus or '').lower().split())
    same_settings=settings==json.loads(previous_settings or '{}')
    if not same_brief or not same_settings: memory={}
    feedback=[];used=set()
    for rating,labels in [(1,args.like),(0,args.dislike)]:
        for label in labels:
            candidates=[cid for cid,row in memory.get('seen',{}).items() if cid==label or row.get('name','').lower()==label.lower()]
            if len(candidates)!=1: raise ValueError('Review must identify exactly one candidate from the same ICP memory: '+label)
            cid=candidates[0]
            if cid in used: raise ValueError('Conflicting or duplicate review for '+label)
            used.add(cid)
            feedback.append({'candidate_id':cid,'rating':rating,'feedback_id':state['last_run_id']+':'+cid+':'+str(rating)})
    payload={'focus':focus,'memory_json':json.dumps(memory) if memory else '', 'feedback_json':json.dumps(feedback),'settings_json':json.dumps(settings)}
    print(json.dumps({'workspace':identity['workspace'],'focus':focus,'settings':settings,'remembered_candidates':len(memory.get('seen',{})),'human_reviews_to_apply':len(feedback),'starts_run':args.start},indent=2))
    if not args.start:return
    run=clay('workflows','runs','test',wf,'--inputs',json.dumps(payload))
    state['last_run_id']=run['runId'];save(args.state,state)
    print(json.dumps(run,indent=2))

if __name__=='__main__':main()
