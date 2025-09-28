import re, hashlib, ipaddress, json
from pathlib import Path
from .config import TAGS_REG_PATH

def safe_filename(name: str) -> str:
  name = name.strip().replace('\x00','')
  name = re.sub(r'[\\/\r\n\t]+','_', name)
  return name or 'file'

def sha256_file(path: Path) -> str:
  h = hashlib.sha256()
  with open(path,'rb') as f:
    for chunk in iter(lambda:f.read(1024*1024), b''):
      h.update(chunk)
  return h.hexdigest()

PRIVATE_NETS=[
  ipaddress.ip_network('10.0.0.0/8'),
  ipaddress.ip_network('172.16.0.0/12'),
  ipaddress.ip_network('192.168.0.0/16'),
  ipaddress.ip_network('169.254.0.0/16'),
]
def is_private_ip(ip: str) -> bool:
  try:
    ip_addr = ipaddress.ip_address(ip)
    return any(ip_addr in n for n in PRIVATE_NETS)
  except Exception:
    return False

# Tag registry
def registry_list():
  try:
    data = json.loads(TAGS_REG_PATH.read_text('utf-8'))
    if isinstance(data, list):
      return sorted(set(x.strip() for x in data if isinstance(x, str) and x.strip()), key=str.lower)
  except Exception:
    pass
  return []

def registry_add(name: str):
  name = name.strip()
  if not name: return registry_list()
  tags = registry_list()
  if name not in tags: tags.append(name)
  TAGS_REG_PATH.write_text(json.dumps(tags, ensure_ascii=False))

def registry_del(name: str):
  name = name.strip()
  tags = registry_list()
  tags = [t for t in tags if t != name]
  TAGS_REG_PATH.write_text(json.dumps(tags, ensure_ascii=False))
