"""Turn a Cowork/Claude Code session .jsonl into a readable Markdown transcript (user + Claude text only).
usage: python3 transcript_reference.py session.jsonl   (writes transcript.md next to PROJECT)"""
import os, sys
import json,re,html,datetime
SRC=sys.argv[1]  # path to the session .jsonl
NZ=datetime.timezone(datetime.timedelta(hours=13))
ev=[];frames={}
def clean(t):
    t=re.sub(r'<artifact-view-context.*?</artifact-view-context>\s*\(The JSON line above.*?\)\s*','',t,flags=re.S)
    t=re.sub(r'<artifact-view-context.*?</artifact-view-context>','',t,flags=re.S)
    t=re.sub(r'<system-reminder>.*?</system-reminder>','',t,flags=re.S)
    t=re.sub(r'\[Image: source: [^\]]*\]','[image]',t)
    t=re.sub(r'\[Image: original [^\]]*\]','',t)
    return t.strip()
SKIP=('Base directory for this skill','## Page contract','<command-','Caveat:')
for l in open(SRC):
    try:d=json.loads(l)
    except:continue
    if d.get('isSidechain'):continue
    t=d.get('type');ts=d.get('timestamp')
    if t=='frame-link' and d.get('frameUrl'):
        frames[d['frameUrl']]=(d.get('title') or '',ts)
    if t=='user':
        c=d['message'].get('content');parts=[];img=0
        if isinstance(c,str):parts=[c]
        else:
            for b in c:
                if b.get('type')=='text':parts.append(b['text'])
                elif b.get('type')=='image':img+=1
        txt=clean('\n'.join(parts))
        if txt.startswith('This session is being continued'):ev.append(('div',ts,'Session continued (context was summarised)'));continue
        if any(txt.startswith(s) for s in SKIP):continue
        if 'Tool loaded.' == txt: continue
        if txt.startswith('[Request interrupted'): continue
        if not txt and not img:continue
        if img and txt.count('[image]')<img: txt=(txt+'\n'+' '.join(['[image]']*(img-txt.count('[image]')))).strip()
        ev.append(('user',ts,txt))
    if t=='attachment':
        a=d['attachment']
        if a.get('type')=='queued_command':
            p=a.get('prompt');p=p if isinstance(p,str) else ' '.join(x.get('text','') for x in p if isinstance(x,dict))
            if p.lstrip().startswith('<agent-message') or '<task-notification' in p:continue
            p=clean(p)
            if p: ev.append(('user',ts,'(sent while Claude was working) '+p))
    if t=='assistant':
        for b in d['message'].get('content',[]):
            if b.get('type')=='text' and b['text'].strip():
                ev.append(('claude',ts,b['text'].strip()))
# merge consecutive claude
out=[]
for e in ev:
    if out and e[0]=='claude' and out[-1][0]=='claude': out[-1]=('claude',out[-1][1],out[-1][2]+'\n\n'+e[2])
    elif out and e[0]=='user' and out[-1][0]=='user' and out[-1][2]==e[2]: continue
    else: out.append(e)
def when(ts):
    try: return datetime.datetime.fromisoformat(ts.replace('Z','+00:00')).astimezone(NZ)
    except: return None
# markdown
md=['# MV Study with Claude: full session transcript','',
    'Phyo × Claude (Opus 5.5) in Cowork, 5–8 October 2026. Times are NZ (NZDT). Your messages and Claude\'s replies only; tool calls and file dumps are left out. "[image]" marks an image you attached.','']
if frames:
    md+=['## Artifacts made in this session','']
    for u,(ti,ts) in sorted(frames.items(),key=lambda x:x[1][1] or ''):
        md.append(f'- [{ti or u}]({u})')
    md.append('')
md+=['## Conversation','']
lastday=None;nu=0
for kind,ts,txt in out:
    w=when(ts)
    if w and w.date()!=lastday:
        lastday=w.date();md+=['',f'### {w.strftime("%A %-d %B %Y")}','']
    tm=w.strftime('%H:%M') if w else ''
    if kind=='div': md+=['',f'*— {txt} —*','']
    elif kind=='user':
        nu+=1;md+=[f'**Phyo** · {tm}','',('\n'.join('> '+x if x else '>' for x in txt.split('\n'))),'']
    else: md+=[f'**Claude** · {tm}','',txt,'','---','']
open('/tmp/tx/transcript.md','w').write('\n'.join(md))
json.dump({'events':[(k,(when(ts).isoformat() if when(ts) else ''),x) for k,ts,x in out],'frames':[(u,t[0]) for u,t in sorted(frames.items(),key=lambda x:x[1][1] or '')]},open('/tmp/tx/data.json','w'))
print(len(out),nu,len(frames),len('\n'.join(md)))
