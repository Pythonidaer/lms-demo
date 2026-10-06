"""Inventory local upstream checkouts. Mapping is not a claim of full-page review.

Usage: python3 scripts/inventory-sources.py /path/to/TypeScript-Website /path/to/mdn-content
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

root = Path(__file__).resolve().parents[1]
ts_root, mdn_root = map(Path, sys.argv[1:3])
course = json.loads((root/'course.json').read_text())
direct = {}
for section in course['sections']:
    for source in section['sources']:
        direct.setdefault(source['url'].split('#')[0].rstrip('/'), []).append(section['id'])

def sha(path):
    return subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()

ts_sha, mdn_sha = sha(ts_root), sha(mdn_root)
documents = []
categories = {
    'get-started': ['ts-sec-orientation','ts-sec-everyday'],
    'handbook-v2': ['ts-sec-everyday','ts-sec-objects','ts-sec-narrowing','ts-sec-states','ts-sec-functions','ts-sec-generics','ts-sec-operators','ts-sec-transformations','ts-sec-classes','ts-sec-modules','ts-sec-declarations'],
    'reference': ['ts-sec-utilities','ts-sec-classes','ts-sec-specialized','ts-sec-advanced-runtime'],
    'modules-reference': ['ts-sec-modules'],
    'declaration-files': ['ts-sec-declarations'],
    'project-config': ['ts-sec-configuration'],
    'javascript': ['ts-sec-migration'],
    'tutorials': ['ts-sec-orientation','ts-sec-configuration','ts-sec-migration','ts-sec-async-dom','ts-sec-specialized']
}
for base in ['packages/documentation/copy/en','packages/tsconfig-reference/copy/en']:
    for file in sorted((ts_root/base).rglob('*.md')):
        if '/diagrams/' in str(file): continue
        relative=file.relative_to(ts_root).as_posix()
        text=file.read_text()
        permalink=re.search(r'^permalink:\s*[\'"]?([^\n\'"]+)',text,re.M)
        title=re.search(r'^(?:title|display):\s*[\'"]?([^\n\'"]+)',text,re.M)
        if permalink:
            url='https://www.typescriptlang.org'+permalink[1].strip()
        elif base.endswith('tsconfig-reference/copy/en') and '/options/' in relative:
            url='https://www.typescriptlang.org/tsconfig/#'+file.stem
        else:
            url='https://github.com/microsoft/TypeScript-Website/blob/'+ts_sha+'/'+quote(relative)
        group=file.relative_to(ts_root/base).parts[0]
        mapped=direct.get(url.rstrip('/'),[])
        status='linked-source' if mapped else 'reference-only'
        related=mapped or (['ts-sec-configuration'] if 'tsconfig-reference' in base else categories.get(group,[]))
        if group=='handbook-v1': status='superseded-reference'
        if group=='release-notes': status='historical-reference' if not mapped else 'linked-feature-reference'
        if '/categories/' in relative or '/sections/' in relative: status='reference-navigation'
        documents.append({'provider':'TypeScript','path':relative,'title':title[1].strip() if title else file.stem,'url':url,'sourceUrl':'https://github.com/microsoft/TypeScript-Website/blob/'+ts_sha+'/'+quote(relative),'sha256':hashlib.sha256(text.encode()).hexdigest(),'headingCount':len(re.findall(r'^#{1,6} ',text,re.M)),'coverage':status,'relatedSections':related,'reviewStatus':'selected-passages-and-topic-outline' if mapped else 'inventoried-not-fully-reviewed'})

# Inventory all English JavaScript Guide and Reference paths without requiring a full MDN checkout.
paths=subprocess.check_output(['git','-C',str(mdn_root),'ls-tree','-r','--name-only','HEAD'],text=True).splitlines()
for path in paths:
    if not path.endswith('/index.md') or not (path.startswith(('files/en-us/web/javascript/guide/','files/en-us/web/javascript/reference/')) or path == 'files/en-us/learn_web_development/core/scripting/network_requests/index.md'): continue
    file=mdn_root/path
    text=file.read_text() if file.exists() else ''
    slug=re.search(r'^slug:\s*(.*)',text,re.M)
    url='https://developer.mozilla.org/en-US/docs/'+(slug[1].strip() if slug else '/'.join(p.title() for p in path.removeprefix('files/en-us/').removesuffix('/index.md').split('/')))
    mapped=direct.get(url.rstrip('/'),[])
    documents.append({'provider':'MDN','path':path,'url':url if text else None,'sourceUrl':'https://github.com/mdn/content/blob/'+mdn_sha+'/'+path,'coverage':'linked-source' if mapped else 'reference-only','relatedSections':mapped,'reviewStatus':'selected-passages-and-topic-outline' if mapped else 'inventoried-not-fully-reviewed'})
manifest={'snapshotDate':'2026-10-06','scope':'English TypeScript documentation and TSConfig source files; English MDN JavaScript Guide and Reference paths plus the selected network-requests learning page. Not the unrelated HTML/CSS/HTTP/Web APIs documentation or every translation.','meaning':'Linked sources informed the curriculum. Related sections show subject areas, not full page-by-page coverage. Inventoried documents were not all read in full. This is a source catalog, not an offline corpus or RAG index.','snapshots':{'typescript':ts_sha,'mdn':mdn_sha},'documents':documents}
(root/'docs/source-inventory.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
from collections import Counter
print('Inventory:',len(documents),'documents;',dict(Counter(d['provider'] for d in documents)))
print('Coverage:',dict(Counter(d['coverage'] for d in documents)))
