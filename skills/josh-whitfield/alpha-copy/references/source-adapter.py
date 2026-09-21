# Installer injects SETTINGS and FIELD_MAP above this code for an audience installation.
import json

def handler(context):
 raw=context.get_input('source_record')
 raw=json.loads(raw) if isinstance(raw,str) else raw
 if not isinstance(raw,dict):raise ValueError('Source record must be an object')
 values=dict(SETTINGS)
 for target,path in FIELD_MAP.items():
  value=raw
  # Deliberately support only documented object-key paths; no inferred associations.
  if not isinstance(path,str) or not path.startswith('$.'):raise ValueError('Field maps require $.object.key paths')
  for key in path[2:].split('.'):
   if not isinstance(value,dict) or key not in value:
    raise ValueError('Source field is missing: '+path)
   value=value[key]
  if isinstance(value,(dict,list)):raise ValueError('Map scalar source values only: '+target)
  values[target]='' if value is None else str(value)
 if not values.get('company_domain'):raise ValueError('Map the actual employer company domain')
 if not values.get('source_record_id'):raise ValueError('Map a stable source record ID')
 values['source_kind']='audience'
 return values
