"""Choose a native Clay source and save one shared brief. Never runs a batch."""
import argparse, json, subprocess, sys
from pathlib import Path
from install import clay, save

DEFAULT_OFFER='We implement Clay workflows that research buying signals, qualify accounts, enrich prospect data, and create evidence-backed outreach for revenue teams.'

def source_page(kind,cursor=None):
 args=['audiences','list','--entity-type','people'] if kind=='audience' else ['tables','list','--limit','50']
 if cursor:args+=['--cursor',cursor]
 return clay(*args)

def select_source(kind):
 cursor=None
 while True:
  page=source_page(kind,cursor);rows=page.get('data',[])
  if not rows:raise ValueError('No sources found on this page')
  for i,row in enumerate(rows,1):
   parent=(row.get('workbook') or {}).get('name','')
   print(str(i)+'. '+row['name']+(' / '+parent if parent else '')+' ['+str(row['id'])+']')
  answer=input('Choose a number'+(' or n for next page' if page.get('cursor') else '')+': ').strip()
  if answer=='n' and page.get('cursor'):cursor=page['cursor'];continue
  if answer.isdigit() and 1<=int(answer)<=len(rows):return rows[int(answer)-1]
  print('Choose one of the displayed sources.')

def ask(label,default=''):
 result=input(label+(' ['+default+']' if default else '')+': ').strip()
 return default if not result else result

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--kind',choices=['audience','table'],required=True)
 p.add_argument('--output',type=Path,required=True,help='Private setup folder outside the portable skill')
 p.add_argument('--source-id',help='Skip the numbered picker and inspect this exact source')
 p.add_argument('--brief',type=Path,help='Reuse a shared brief instead of prompting')
 p.add_argument('--field-map',type=Path,help='Confirmed audience trigger paths; required for --install')
 p.add_argument('--exa-account',help='Optional Clay HTTP header account ID storing your Exa key, not the key itself')
 p.add_argument('--install',action='store_true',help='Create a new audience draft; never publish or run')
 a=p.parse_args();package=Path(__file__).resolve().parents[1]
 if a.output.resolve().is_relative_to(package):raise ValueError('Keep private setup outside the portable package')
 if a.install and (a.kind!='audience' or not a.field_map):raise ValueError('--install requires audience and a confirmed --field-map')
 identity=clay('whoami');workspace=identity['workspace'];print('Workspace:',workspace['name'],workspace['id'])
 if a.source_id:
  source=clay('audiences','get',a.source_id) if a.kind=='audience' else clay('tables','get',a.source_id)
  if a.kind=='audience' and source.get('entityType')!='people':raise ValueError('Choose a people segment')
 else:source=select_source(a.kind)
 if not source.get('id'):raise ValueError('Source did not return a stable ID')
 if a.kind=='audience':
  details=clay('audiences','get',source['id'])
  if details.get('entityType')!='people':raise ValueError('Choose a people segment')
  count=clay('audiences','records','search-count','--entity-type','people','--audience-id',source['id'])
  save(a.output/'source-count.json',count)
  save(a.output/'people-fields.json',clay('audiences','fields','list','--entity-type','people'))
 else:
  save(a.output/'source-columns.json',clay('tables','columns','get',source['id']))
 if a.brief:brief=json.loads(a.brief.read_text())
 else:
  brief={'offer':ask('Offer sentence (type NONE for ICP-only research)',DEFAULT_OFFER),
         'icp':ask('ICP, buyer criteria and exclusions'),
         'sender_name':ask('Sender name'),
         'greeting':ask('Greeting; type NONE for no greeting','Hi {{first_name}},'),
         'cta':ask('Exact CTA; blank lets Clay propose one question'),
         'signature':ask('Signature; use \\n for a line break').replace('\\n','\n'),
         'comparison_mode':ask('Comparison: auto or before_after','before_after'),
         'comparison_as_of':ask('Historical cutoff YYYY-MM-DD; blank uses each row receipt'),
         'comparison_focus':ask('Change to look for','Positioning or audience emphasis'),
         'batch_id':ask('Batch/version label')}
  if brief['greeting']=='NONE':brief['greeting']=''
  if brief['offer']=='NONE':brief['offer']=''
 if not isinstance(brief,dict):raise ValueError('Brief must be an object')
 if any(any(word in key.lower() for word in ['api_key','apikey','token','secret','authorization']) for key in brief):raise ValueError('Keep credentials in the Clay secure header account, not the shared brief')
 if brief.get('comparison_mode','auto') not in ['auto','before_after']:raise ValueError('Invalid comparison mode')
 if not (brief.get('offer') or brief.get('icp')):raise ValueError('Enter an offer or ICP')
 # Per-person values always come from the source; never share one person's receipts or identity.
 forbidden={'company_domain','company_name','recipient_name','recipient_role','source_record_id','evidence_json','past_observation_json','current_observation_json'}
 if forbidden & set(brief):raise ValueError('Shared brief contains per-person fields: '+', '.join(sorted(forbidden & set(brief))))
 brief.update(source_kind=a.kind,source_id=source['id'])
 save(a.output/'brief.json',brief)
 save(a.output/'source.json',{'workspace_id':str(workspace['id']),'kind':a.kind,'id':source['id'],'name':source['name'],'connected':False,'batch_started':False})
 if a.install:
  exa_args=['--exa-account',a.exa_account] if a.exa_account else []
  subprocess.run([sys.executable,str(package/'scripts/install.py'),'--workspace',str(workspace['id']),'--state',str(a.output/'installation.json'),'--audience',source['id'],'--entity-type','CONTACT','--brief',str(a.output/'brief.json'),'--field-map',str(a.field_map),'--create']+exa_args,check=True)
  print('Audience draft created. Confirm its source paths and test selected contacts before activation.')
 else:print('Saved source selection and brief. No source connected and no batch started.')
 print('Table: use Invoke Workflow in the selected table. Audience: supply confirmed field-map and --install. See references/sources.md.')

if __name__=='__main__':main()
