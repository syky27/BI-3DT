#!/usr/bin/env python3
"""Stop-motion clips of SolidCraft tools: the agent cursor glides to the button and the picks while the
window is screenshotted ~4x per second. clips.py [name...]  -> clips/<name>.mp4"""
import sys, time, json, os, threading, subprocess, shutil
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from sc import control
import shots as S
P=27900; SP=os.path.dirname(HERE); CK=SP+'/media/ckpt'; OUT=SP+'/clips'
os.makedirs(OUT,exist_ok=True)
c,ex,open_,esc=S.c,S.ex,S.open_,S.esc
class Rec:
    def __init__(self,name):
        self.dir=f'{OUT}/{name}.frames'; shutil.rmtree(self.dir,ignore_errors=True); os.makedirs(self.dir)
        self.stop=False; self.n=0; self.t0=None
        self.th=threading.Thread(target=self.loop); 
    def loop(self):
        self.t0=time.time()
        while not self.stop:
            control(P,'ui.screenshot',{'path':f'{self.dir}/f{self.n:05d}.png'}); self.n+=1
            time.sleep(0.02)
    def __enter__(self): self.th.start(); time.sleep(0.6); return self
    def __exit__(self,*a):
        time.sleep(1.5); self.stop=True; self.th.join(); dur=time.time()-self.t0
        fps=max(1.0,self.n/dur)
        subprocess.run(['ffmpeg','-loglevel','error','-y','-framerate',f'{fps:.3f}','-i',f'{self.dir}/f%05d.png','-vf','scale=1280:-2','-c:v','libx264','-preset','slow','-crf','26','-pix_fmt','yuv420p','-movflags','+faststart',self.dir.replace('.frames','.mp4')],check=True)
        print(f'{os.path.basename(self.dir)}: {self.n} frames, {dur:.1f}s, {fps:.1f} fps'); shutil.rmtree(self.dir)
def cursor(on=True,speed=1): c('ui.agent_cursor',{'show':on,'speed':speed})
def hold(s): time.sleep(s)
def start(cmd):
    """click a toolbar button for real (dialog shows), pointer glides there first"""
    h={x['name']:x for x in c('ui.handles')}; b=h.get('button:'+cmd) or h.get('toolbar:'+cmd)
    if b: c('ui.move',{'x':b['x'],'y':b['y']}); hold(0.4); c('ui.click',{'x':b['x'],'y':b['y']})
    else: c('ui.start',{'command':cmd})
CLIPS={}
def clip(f): CLIPS[f.__name__.replace('_','-')]=f; return f

@clip
def new_sketch():
    close=c('ui.documents',{'action':'new'}); c('ui.view',{'view':'iso'})
    with Rec('new-sketch'):
        ex('sketch.create',{'plane':'XY','name':'Plate outline'}); hold(1.0)
@clip
def draw_dimension():
    c('ui.documents',{'action':'new'}); ex('sketch.create',{'plane':'XY','name':'Plate outline'}); c('ui.camera',{'target':[0,0,0],'distance':110}); hold(0.5)
    with Rec('draw-dimension'):
        ex('sketch.rectangle.center',{'center':[0,0],'corner':[30,20]}); hold(0.6)
        ex('sketch.dimension',{'entities':['l1'],'type':'length','value':60,'text_at':[0,-26]}); hold(0.6)
        ex('sketch.dimension',{'entities':['l2'],'type':'length','value':40,'text_at':[38,0]}); hold(0.6)
        ex('sketch.circle.center',{'center':[21,11],'diameter':4.5}); hold(0.6)
        ex('sketch.dimension',{'entities':['c1'],'type':'diameter','value':4.5,'text_at':[26,6]}); hold(0.4)
        ex('sketch.dimension',{'entities':['c1.center','l2'],'type':'distance','value':9,'text_at':[25,15]}); hold(0.4)
        ex('sketch.dimension',{'entities':['c1.center','l3'],'type':'distance','value':9,'text_at':[15,15]}); hold(1.2)
@clip
def extrude():
    open_(CK+'/plate/plate-01-sketch.sc')
    with Rec('extrude'):
        start('solid.extrude'); hold(1.2); esc(1); hold(0.3)
        ex('solid.extrude',{'sketch':'Plate outline','distance':4,'name':'Plate'}); hold(0.5); c('ui.view',{'view':'fit','animate':True}); hold(1.2)
@clip
def edit_timeline():
    open_(CK+'/plate/plate-03-fillets.sc')
    with Rec('edit-timeline'):
        c('ui.editFeature',{'feature':'Plate'}); hold(1.5); esc(2); hold(0.3)
        ex('timeline.edit',{'feature':'Plate','set':{'extent':{'distance':'12'}}}); hold(1.5)
        ex('edit.undo'); hold(0.8)
@clip
def name_parameter():
    open_(CK+'/plate/plate-03-fillets.sc')
    with Rec('name-parameter'):
        ex('parameters.change',{'name':'d1','expression':'width = 60'}); hold(0.8)
        ex('parameters.change',{'name':'d2','expression':'length = 40'}); hold(0.8)
        start('parameters.change'); hold(2.0); esc(2); hold(0.3)
        ex('parameters.change',{'name':'width','expression':'90'}); hold(0.6); c('ui.view',{'view':'fit','animate':True}); hold(1.2)
@clip
def shell():
    open_(CK+'/box/box-01-body.sc')
    with Rec('shell'):
        ex('solid.shell',{'faces':[[0,0,30]],'thickness':'wall','name':'Hollow'}); hold(0.6)
        c('ui.camera',{'pitch':0.9}); hold(1.2)
@clip
def offset_plane():
    open_(CK+'/box/box-02-shell.sc')
    with Rec('offset-plane'):
        ex('parameters.add',{'name':'lid_h','expression':'8','unit':'mm'}); ex('parameters.add',{'name':'clearance','expression':'0.3','unit':'mm'}); ex('parameters.add',{'name':'lid_gap','expression':'15','unit':'mm'})
        ex('construct.plane.offset',{'base':'XY','offset':'box_h + lid_gap','name':'Lid plane'}); hold(0.8)
        ex('sketch.create',{'plane':'Lid plane','name':'Lid outline'}); hold(0.5)
        ex('sketch.rectangle.center',{'center':[0,0],'corner':['box_w / 2 + wall + clearance','box_l / 2 + wall + clearance']}); hold(0.5)
        ex('sketch.finish'); hold(0.3)
        ex('solid.extrude',{'distance':'lid_h','operation':'new_body','name':'Lid body','body_name':'Lid'}); hold(0.5); c('ui.view',{'view':'iso','animate':True}); c('ui.view',{'view':'fit','animate':True}); hold(1.2)
@clip
def pattern():
    open_(CK+'/box/box-03-lid.sc')
    for n,e,u in (('vent_w','2','mm'),('vent_pitch','vent_w * 3','mm'),('vent_margin','wall * 3','mm'),('vent_count','floor((box_w - 2 * wall - vent_pitch) / vent_pitch)','')):
        ex('parameters.add',{'name':n,'expression':e,'unit':u})
    with Rec('pattern'):
        ex('sketch.create',{'plane':'XZ','name':'Vent slot'}); hold(0.4)
        ex('sketch.rectangle.center',{'center':[0,'-box_h / 2'],'corner':['vent_w / 2','-(box_h - vent_margin)']}); hold(0.5)
        ex('sketch.finish'); hold(0.3)
        ex('solid.extrude',{'through_all':True,'direction':'symmetric','operation':'cut','targets':['Box'],'name':'Vent'}); hold(0.6); c('ui.view',{'view':'iso','animate':True}); hold(0.6)
        ex('solid.pattern.rectangular',{'features':['Vent'],'dir1':[1,0,0],'count1':'vent_count','spacing1':'vent_pitch','alignment':'center','name':'Vents'}); hold(1.0)
        ex('parameters.change',{'name':'box_w','expression':'90'}); c('ui.view',{'view':'fit','animate':True}); hold(1.5)
@clip
def section():
    open_(CK+'/box/box-05-finished.sc')
    with Rec('section'):
        ex('inspect.section',{'plane':'XZ','flip':True}); hold(0.8)
        c('ui.camera',{'yaw':0.2,'pitch':0.3}); hold(0.8); c('ui.camera',{'yaw':-0.8,'pitch':0.5}); hold(1.0)
        ex('inspect.section',{'clear':True}); hold(0.6)
@clip
def config_activate():
    open_(CK+'/comb/comb-04-configs.sc')
    with Rec('config-activate'):
        start('config.table'); hold(2.0); esc(2); hold(0.3)
        for r in ('S','L','M'):
            ex('config.activate',{'row':r}); c('ui.view',{'view':'fit','animate':True}); hold(1.3)
@clip
def parameter_change_rebuild():
    open_(CK+'/plate/plate-04-parametric.sc')
    with Rec('parameter-change-rebuild'):
        for n,v in (('width','100'),('length','30'),('thickness','8'),('hole_d','12')):
            ex('parameters.change',{'name':n,'expression':v}); c('ui.view',{'view':'fit','animate':True}); hold(1.2)
if __name__=='__main__':
    names=sys.argv[1:] or list(CLIPS)
    cursor(True,1)
    for n in names:
        try: CLIPS[n]()
        except Exception as e: print('FAILED',n,e)
        esc(2); c('ui.menu',{'close':True},quiet=True)
    cursor(False)
