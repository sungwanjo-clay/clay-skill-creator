"""Add an optional Exa-key path using native Clay HTTP nodes and explicit account binding."""
from pathlib import Path
import copy
HTTP_PACKAGE='4299091f-3cd3-4d68-b198-0143575f471d'
HTTP_ACTION='http-api-v2'
ENDPOINT='https://api.exa.ai/contents'

def extend(graph,account_id):
 if not isinstance(account_id,str) or not account_id.startswith(('aa_','app_','tct_')) or any(c.isspace() for c in account_id):
  raise ValueError('Select a Clay HTTP header account ID or an inspected Exa-bound tool ID, not an Exa API key')
 g=copy.deepcopy(graph);root=Path(__file__).resolve().parents[1]
 g['trigger']['inputSchema']['properties']['comparison_page_path']={'type':'string','description':'Optional same-company page path to compare, e.g. / or /pricing. Default /. No query parameters.'}
 first=g['nodes'][0]
 assert first['key']=='validate'
 first['spec']['inputSchema']['properties']['comparison_page_path']={'type':'string','sourceNodeId':'NODE:trigger','sourcePath':'$.comparison_page_path'}
 # Preserve the path through validation so audience adapters use the same contract.
 # Prepare reads the path from the trigger or source adapter, independent of validation output.
 def ins(**mapping):return {'type':'object','properties':{k:{'type':'string','sourceNodeId':'NODE:'+v[0],'sourcePath':v[1]} for k,v in mapping.items()}}
 def edge(k):return [{'sourceNode':'NODE:'+k}]
 prepare={'key':'exa_prepare','spec':{'nodeType':'code','name':'Exa · Choose page and historical cutoff','code':(root/'references/exa-prepare.py').read_text(),'inputSchema':ins(contract_json=('validate','$.contract_json'),evidence_json=('validate','$.evidence_json'),comparison_page_path=('trigger','$.comparison_page_path')),'incomingEdges':edge('validate')}}
 def http(key,name,body,parent):
  return {'key':key,'spec':{'nodeType':'tool','name':name,'inputSchema':ins(body=('exa_prepare','$.'+body)),
   'tools':[{'toolType':'clay_action','actionKey':HTTP_ACTION,'actionPackageId':HTTP_PACKAGE,**({'toolId':account_id} if account_id.startswith('tct_') else {'appAccountId':account_id}),
    'inputMappingConfig':{'method':{'type':'static','value':'POST'},'url':{'type':'static','value':ENDPOINT},
      'body':{'type':'reference','expression':'{{body}}'},'headers':{'type':'map','entries':{'Content-Type':{'type':'static','value':'application/json'}}},
      'followRedirects':{'type':'static','value':False},'shouldRetry':{'type':'static','value':False},
      'returnResponseMetadata':{'type':'static','value':False},'responseTimeout':{'type':'static','value':90000}}}],
   'incomingEdges':edge(parent)}}
 normalize={'key':'exa_normalize','spec':{'nodeType':'code','name':'Exa · Verify and preserve both observations','code':(root/'references/exa-normalize.py').read_text(),
  'inputSchema':ins(contract_json=('exa_prepare','$.contract_json'),request_url=('exa_prepare','$.request_url'),requested_as_of=('exa_prepare','$.requested_as_of'),past_response=('exa_past','$'),current_response=('exa_current','$')),'incomingEdges':edge('exa_current')}}
 for row in g['nodes'][1:]:
  for prop in row['spec'].get('inputSchema',{}).get('properties',{}).values():
   if prop.get('sourceNodeId')=='NODE:validate' and prop.get('sourcePath') in ['$.contract_json','$.evidence_json']:prop['sourceNodeId']='NODE:exa_normalize'
  if row['key']=='research':row['spec']['incomingEdges']=edge('exa_normalize')
 g['nodes'][1:1]=[prepare,http('exa_past','Exa · Retrieve the historical observation','past_body','exa_prepare'),http('exa_current','Exa · Retrieve the current observation','current_body','exa_past'),normalize]
 return g
