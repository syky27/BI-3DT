#!/usr/bin/env python3
"""Deterministic stop-motion clips: one window frame after every pointer step, click and key, played at FPS.
rec2.py [clip...] -> clips2/<clip>.mp4"""
import sys, time, os, json, shutil, subprocess, math
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import shots as S
c,ex,esc,CK=S.c,S.ex,S.esc,S.CK
def open_(path):
    S.open_(path)
    h={x['name']:x for x in c('ui.handles')}
    if 'tab:MODEL' in h: c('ui.click',{'x':h['tab:MODEL']['x'],'y':h['tab:MODEL']['y']}); time.sleep(0.3)
OUT=os.path.dirname(HERE)+'/clips2'; os.makedirs(OUT,exist_ok=True)
FPS=10
class Clip:
    def __init__(self,name): self.name=name; self.dir=f'{OUT}/{name}.frames'; shutil.rmtree(self.dir,ignore_errors=True); os.makedirs(self.dir); self.n=0; self.pos=(720,450)
    def frame(self,k=1):
        from sc import control
        for _ in range(k):
            for attempt in range(4):
                r=control(S.P,'ui.screenshot',{'path':f'{self.dir}/f{self.n:05d}.png'})
                if r.get('ok'): break
                subprocess.run(['osascript','-e','tell application "SolidCraft" to activate']); time.sleep(0.6)
            else: raise RuntimeError('window stays hidden; keep the SolidCraft window visible while recording')
            self.n+=1
    def hold(self,sec): self.frame(int(sec*FPS))
    def handle(self,name):
        h={x['name']:x for x in c('ui.handles')}; x=h[name]; return (x['x'],x['y'])
    def world(self,p): return tuple(c('ui.worldToScreen',{'points':[p]})[0])
    def glide(self,to,sec=1.0):
        x0,y0=self.pos; x1,y1=to; n=max(2,int(sec*FPS))
        for i in range(1,n+1):
            t=i/n; t=t*t*(3-2*t)  # ease
            c('ui.move',{'x':x0+(x1-x0)*t,'y':y0+(y1-y0)*t}); self.frame()
        self.pos=to
    def click(self,to=None,sec=0.8,**kw):
        if to: self.glide(to,sec)
        c('ui.click',{'x':self.pos[0],'y':self.pos[1],**kw}); time.sleep(0.25); self.frame(2)
    def dblclick(self,to=None,sec=0.8):
        if to: self.glide(to,sec)
        c('ui.click',{'x':self.pos[0],'y':self.pos[1],'double':True}); time.sleep(0.3); self.frame(2)
    def type(self,text,sec=0.12):
        for ch in text: c('ui.text',{'text':ch}); self.frame(max(1,int(sec*FPS)))
    def key(self,k,**kw): c('ui.key',{'key':k,**kw}); time.sleep(0.25); self.frame(2)
    def done(self):
        subprocess.run(['ffmpeg','-loglevel','error','-y','-framerate',str(FPS),'-i',f'{self.dir}/f%05d.png','-vf','scale=1280:-2','-c:v','libx264','-preset','slow','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',f'{OUT}/{self.name}.mp4'],check=True)
        print(f'{self.name}: {self.n} frames = {self.n/FPS:.1f}s'); shutil.rmtree(self.dir)

    def handles(self): return {x['name']:x for x in c('ui.handles')}
    def find(self,sub):
        for n,x in self.handles().items():
            if sub in n: return (x['x'],x['y'])
        raise KeyError(sub)
    def at(self,**w): r=c('ui.at',w); return (r['x'],r['y']) if isinstance(r,dict) else tuple(r)
    def sk(self,p): return tuple(c('ui.sketchToScreen',{'points':[p]})[0])
    def field(self,name,text,enter=True,sec=0.8):
        self.click(self.handle(name),sec); self.key('a',cmd=True); self.type(text)
        if enter: self.key('Enter')
    def dropdown(self,name,option):
        self.click(self.handle(name),0.7); self.hold(0.4)
        opts=[n for n in self.handles() if n.startswith(name+':')]; print('  options',opts)
        pick=[n for n in opts if option.lower() in n.lower()][0]
        self.click(self.handle(pick),0.6); self.hold(0.3)
    def last_timeline(self):
        tl=[n for n in c('ui.handles') if n['name'].startswith('timeline:')]; return tl[-1]['name']
    def ok(self,fallback=None):
        d=c('ui.inspect').get('dialog')
        if d and (d.get('commands') is None or d.get('error')):
            print('  dialog not ready:',d.get('waiting'),d.get('error'),json.dumps(d.get('inputs'))[:300])
            if fallback: esc(2); fallback(); self.hold(0.5); return
        self.click(self.handle('dialog:OK'),0.6); self.hold(0.6)
    def fit(self,sec=1.2): c('ui.view',{'view':'fit','animate':True}); self.hold(sec)
CLIPS={}
def clip(f): CLIPS[f.__name__.replace('_','-')]=f; return f

@clip
def new_sketch():
    c('ui.documents',{'action':'new'}); c('ui.view',{'view':'iso'}); c('ui.camera',{'target':[0,0,0],'distance':150}); k=Clip('new-sketch'); k.hold(0.8)
    k.click(k.handle('button:sketch.create')); k.hold(1.0)
    k.glide(k.at(plane='XY'),1.0); k.hold(0.6); k.click(); k.hold(1.8)
    k.done()

@clip
def draw_dimension():
    c('ui.documents',{'action':'new'}); ex('sketch.create',{'plane':'XY','name':'Plate outline'}); c('ui.camera',{'target':[0,0,0],'distance':110}); k=Clip('draw-dimension'); k.hold(0.6)
    k.click(k.handle('button:sketch.rectangle.two_point')); k.hold(0.4)
    k.click(k.sk([-30,-20]),1.0); k.hold(0.3); k.type('60'); k.key('Tab'); k.type('40'); k.key('Enter'); k.hold(0.8)
    print('  after rect:', c('ui.inspect').get('sketch'))
    k.click(k.handle('button:sketch.circle.center')); k.hold(0.3)
    k.click(k.sk([21,11]),1.0); k.hold(0.3); k.type('4.5'); k.key('Enter'); k.hold(0.8)
    k.click(k.handle('button:sketch.dimension')); k.hold(0.3)
    k.click(k.sk([21,11]),0.8); k.click(k.sk([30,2]),0.8); k.click(k.sk([36,16]),0.6); k.hold(0.3); k.type('9'); k.key('Enter'); k.hold(0.6)
    k.click(k.sk([21,11]),0.8); k.click(k.sk([5,20]),0.8); k.click(k.sk([21,26]),0.6); k.hold(0.3); k.type('9'); k.key('Enter'); k.hold(0.6)
    k.key('Escape'); k.hold(1.2)
    print('  dims:', len(c('ui.selection').get('dimensions') or []), 'sketch:', c('ui.inspect').get('sketch'))
    k.done()

@clip
def extrude():
    open_(CK+'/plate/plate-01-sketch.sc'); c('ui.camera',{'target':[0,0,0],'distance':130}); k=Clip('extrude'); k.hold(0.8)
    k.click(k.handle('button:solid.extrude')); k.hold(1.2)
    k.click(k.world([15,0,0]),1.0); k.hold(1.2)
    k.field('dialog:Distance','4'); k.hold(0.6); k.fit(1.5)
    k.glide(k.handle(k.last_timeline()),1.0); k.hold(1.0)
    k.done()

@clip
def edit_timeline():
    open_(CK+'/plate/plate-03-fillets.sc'); k=Clip('edit-timeline'); k.hold(0.8)
    k.dblclick(k.handle('timeline:Plate'),1.2); k.hold(1.2)
    k.field('dialog:Distance','12'); k.hold(1.5)
    k.glide(k.handle('timeline:Corners'),1.0); c('ui.menu',{'target':{'type':'timeline','feature':'Corners'}}); time.sleep(0.3); k.hold(1.5); k.key('Escape'); k.hold(0.6)
    k.done()

@clip
def name_parameter():
    open_(CK+'/plate/plate-03-fillets.sc'); k=Clip('name-parameter'); k.hold(0.6)
    k.dblclick(k.handle('timeline:Plate outline'),1.0); time.sleep(0.5); c('ui.camera',{'target':[0,0,0],'distance':110}); k.hold(0.8)
    dims={d['id']:(d['x'],d['y']) for d in c('ui.selection').get('dimensions')}
    k.dblclick(dims['k7'],1.0); k.hold(0.3); k.key('a',cmd=True); k.type('width = 60'); k.key('Enter'); k.hold(0.8)
    k.dblclick(dims['k8'],1.0); k.hold(0.3); k.key('a',cmd=True); k.type('length = 40'); k.key('Enter'); k.hold(0.8)
    k.click(k.handle('button:sketch.finish'),1.0); k.hold(0.6)
    k.click(k.handle('button:parameters.change'),1.0); k.hold(1.5)
    k.field('param:width','90'); k.hold(1.2)
    k.click(k.handle('dialog:close'),0.8); k.fit(1.2)
    k.done()

@clip
def parameter_change_rebuild():
    open_(CK+'/plate/plate-04-parametric.sc'); k=Clip('parameter-change-rebuild'); k.hold(0.6)
    k.click(k.handle('button:parameters.change'),1.0); k.hold(1.2)
    for n,v in (('width','100'),('length','30'),('thickness','8'),('hole_d','12')):
        k.field('param:'+n,v); k.hold(1.0)
    k.click(k.handle('dialog:close'),0.8); k.fit(1.5)
    k.done()

@clip
def shell():
    open_(CK+'/box/box-01-body.sc'); k=Clip('shell'); k.hold(0.6)
    k.click(k.handle('button:solid.shell'),1.0); k.hold(1.0)
    k.click(k.world([0,0,30]),1.0); k.hold(1.0)
    k.field('dialog:Thickness','wall'); k.hold(0.8)
    c('ui.camera',{'pitch':0.95}); k.hold(1.5)
    k.done()

@clip
def offset_plane():
    open_(CK+'/box/box-02-shell.sc')
    for n,e in (('lid_h','8'),('clearance','0.3'),('lid_gap','15')): ex('parameters.add',{'name':n,'expression':e,'unit':'mm'})
    k=Clip('offset-plane'); k.hold(0.6)
    k.click(k.handle('button:construct.plane.offset'),1.0); k.hold(0.8)
    k.click(k.handle('row:XY'),1.0); k.hold(0.8)
    k.field('dialog:Distance','box_h + lid_gap'); k.hold(1.0)
    k.click(k.handle('button:sketch.create'),1.0); k.hold(0.6)
    k.click(k.world([0,0,45]),1.0); k.hold(1.0)
    ex('sketch.rectangle.center',{'center':[0,0],'corner':['box_w / 2 + wall + clearance','box_l / 2 + wall + clearance']}); k.hold(0.8)
    k.click(k.handle('button:sketch.finish'),1.0); k.hold(0.5)
    k.click(k.handle('button:solid.extrude'),1.0); k.hold(0.6)
    k.click(k.world([0,0,45]),1.0); k.hold(0.8)
    k.dropdown('dialog:Operation','New Body')
    k.field('dialog:Distance','lid_h'); k.hold(0.5); c('ui.camera',{'yaw':-0.785,'pitch':0.615,'fit':True}); k.hold(1.5)
    k.done()

@clip
def pattern():
    open_(CK+'/box/box-03-lid.sc')
    for n,e,u in (('vent_w','2','mm'),('vent_pitch','vent_w * 3','mm'),('vent_margin','wall * 3','mm'),('vent_count','floor((box_w - 2 * wall - vent_pitch) / vent_pitch)','')): ex('parameters.add',{'name':n,'expression':e,'unit':u})
    ex('sketch.create',{'plane':'XZ','name':'Vent slot'}); ex('sketch.rectangle.center',{'center':[0,'-box_h / 2'],'corner':['vent_w / 2','-(box_h - vent_margin)']})
    c('ui.view',{'view':'iso'}); c('ui.view',{'view':'fit'}); k=Clip('pattern'); k.hold(0.8)
    k.click(k.handle('button:sketch.finish'),1.0); k.hold(0.5)
    k.click(k.handle('button:solid.extrude'),1.0); k.hold(0.6)
    k.click(k.world([0,0,15]),1.0); k.hold(0.8)
    k.dropdown('dialog:Direction','Symmetric'); k.dropdown('dialog:Extent Type','All'); k.dropdown('dialog:Operation','Cut'); k.hold(0.5)
    k.ok(lambda: ex('solid.extrude',{'through_all':True,'direction':'symmetric','operation':'cut','targets':['Box'],'name':'Vent'})); k.hold(0.8)
    ex('timeline.rename',{'feature':ex('timeline.inspect',{'feature':'Extrude3'}) and 'Extrude3','name':'Vent'}) if False else None
    k.click(k.handle('button:solid.pattern.rectangular'),1.0); k.hold(0.8)
    k.dropdown('dialog:Object Type','Features')
    h=k.handles(); tl=[n for n in h if n.startswith('timeline:')]; k.click(k.handle(tl[-1]),1.0); k.hold(0.6)
    k.click(k.handle('dialog:Direction'),0.6); k.click(k.handle('row:X'),1.0); k.hold(0.6)
    k.field('dialog:Quantity','vent_count',enter=False); k.field('dialog:Spacing','vent_pitch',enter=False); k.click(k.handle('dialog:Alignment:Center'),0.6); k.hold(0.8)
    k.ok(lambda: ex('solid.pattern.rectangular',{'features':[tl[-1].split(':',1)[1]],'dir1':[1,0,0],'count1':'vent_count','spacing1':'vent_pitch','alignment':'center','name':'Vents'})); k.hold(0.8)
    ex('parameters.change',{'name':'box_w','expression':'90'}); k.fit(1.5)
    k.done()

@clip
def section():
    open_(CK+'/box/box-05-finished.sc'); k=Clip('section'); k.hold(0.6)
    k.click(k.handle('tab:INSPECT'),0.8); k.hold(0.4)
    k.click(k.handle('button:inspect.section'),0.8); k.hold(0.8)
    k.click(k.handle('row:XZ'),1.0); k.hold(0.8)
    k.click(k.handle('dialog:Flip'),0.8); k.hold(0.8)
    k.ok(lambda: ex('inspect.section',{'plane':'XZ','flip':True})); k.hold(0.5)
    c('ui.camera',{'yaw':0.2,'pitch':0.3}); k.hold(1.0); c('ui.camera',{'yaw':-0.8,'pitch':0.5}); k.hold(1.2)
    ex('inspect.section',{'clear':True}); k.hold(0.6)
    k.done()

@clip
def config_activate():
    open_(CK+'/comb/comb-04-configs.sc'); k=Clip('config-activate'); k.hold(0.6)
    k.click(k.handle('button:config.table'),1.0); k.hold(1.5)
    for r in ('S','L','M'):
        k.click(k.handle('config:activate:'+r),1.0); k.hold(1.2)
    k.click(k.handle('dialog:close'),0.8); k.fit(1.2)
    k.done()

if __name__=='__main__':
    c('ui.agent_cursor',{'show':True,'speed':'instant'})
    for n in (sys.argv[1:] or list(CLIPS)):
        print('==',n)
        try: CLIPS[n]()
        except Exception as e: print('FAILED',n,repr(e))
        esc(2); c('ui.menu',{'close':True},quiet=True)
