"""Preview or start one native Alpha Copy run from an editable brief file."""
import argparse,json
from pathlib import Path
from install import clay,save

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--state',type=Path,required=True)
 p.add_argument('--brief',type=Path,help='JSON object of named workflow inputs')
 p.add_argument('--start',action='store_true')
 p.add_argument('--status',action='store_true')
 a=p.parse_args();state=json.loads(a.state.read_text())
 if str(clay('whoami')['workspace']['id'])!=state['workspace_id']:raise ValueError('Workspace mismatch')
 wf=state['workflow_id']
 if a.status:
  if not state.get('last_run_id'):raise ValueError('No run recorded by this runner')
  print(json.dumps(clay('workflows','runs','get',wf,state['last_run_id'],'--verbose'),indent=2));return
 if not a.brief:raise ValueError('--brief is required')
 inputs=json.loads(a.brief.read_text())
 if not isinstance(inputs,dict) or not inputs.get('company_domain'):raise ValueError('Brief needs company_domain')
 if not (inputs.get('offer') or inputs.get('icp') or inputs.get('sender_offer_json')):raise ValueError('Enter an offer or ICP')
 print(json.dumps({'workspace_id':state['workspace_id'],'workflow':state['url'],'inputs':inputs,'will_start':a.start,'will_send':False},indent=2))
 if not a.start:return
 if state.get('last_run_id'):
  prior=clay('workflows','runs','get',wf,state['last_run_id'])
  if prior['status'] not in ['completed','failed','cancelled']:raise ValueError('Prior run is unresolved; inspect it before starting another')
 result=clay('workflows','runs','test',wf,'--inputs',json.dumps(inputs))
 state['last_run_id']=result['runId'];save(a.state,state);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
