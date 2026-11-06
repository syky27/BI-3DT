#!/usr/bin/env python3
"""Reproducible stills for the BI-3DT SolidCraft pages. Needs SolidCraft running with --control 27900."""
import sys, time, json, os
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from sc import control
P=27900; SP=os.path.dirname(HERE); OUT=SP+'/shots'; CK=SP+'/media/ckpt'
os.makedirs(OUT,exist_ok=True)
def c(m,p=None,quiet=False):
    r=control(P,m,p)
    if not r.get('ok') and not quiet: print('ERR',m,json.dumps(r)[:300])
    return r.get('result')
def ex(cmd,params=None): return c('engine.execute',{'command':cmd,'params':params or {}})
def toast():
    for _ in range(3):
        h={x['name']:x for x in (c('ui.handles') or [])}
        t=h.get('toast:status:close')
        if not t: return
        c('ui.click',{'x':t['x'],'y':t['y']}); time.sleep(0.2)
def shot(name,wait=0.6):
    time.sleep(wait); toast(); time.sleep(0.2); c('ui.screenshot',{'path':f'{OUT}/{name}.png'}); print('shot',name)
def close_all():
    d=c('ui.documents')
    for i in range(len(d['documents'])-1,-1,-1): c('ui.documents',{'action':'close','index':i,'force':True})
def open_(path):
    close_all(); c('ui.file',{'path':path})
    for _ in range(200):
        if not c('ui.inspect')['file_busy']: break
        time.sleep(0.1)
    time.sleep(0.6); c('ui.view',{'view':'iso'}); c('ui.view',{'view':'fit'}); time.sleep(0.4)
def esc(n=2):
    for _ in range(n): c('ui.key',{'key':'Escape'}); time.sleep(0.2)
    c('ui.menu',{'close':True},quiet=True)
which=sys.argv[1:] or (['all'] if __name__=='__main__' else [])
def want(n): return 'all' in which or n in which

if want('start'):
    close_all(); c('ui.home',{'open':True}); shot('start'); c('ui.home',{'open':False})
if want('window'):
    open_(CK+'/plate/plate-04-parametric.sc'); shot('window')
    c('ui.view',{'view':'front'}); shot('view-front',0.8); c('ui.view',{'view':'top'}); shot('view-top',0.8); c('ui.view',{'view':'iso'}); c('ui.view',{'view':'fit'})
if want('browser'):
    open_(CK+'/plate/plate-04-parametric.sc'); ex('browser.expand_all'); shot('browser-expanded'); 
if want('sketch'):
    open_(CK+'/plate/plate-01-sketch.sc'); c('ui.editFeature',{'feature':'Plate outline'}); time.sleep(0.8); c('ui.camera',{'target':[0,0,0],'distance':95}); shot('sketch-mode',0.8)
    # hover a dimension? just the palette
    esc(2)
if want('extrude'):
    open_(CK+'/plate/plate-02-extruded.sc'); c('ui.editFeature',{'feature':'Plate'}); shot('extrude-dialog',1.0); esc(2)
if want('fillet'):
    open_(CK+'/plate/plate-03-fillets.sc'); c('ui.editFeature',{'feature':'Corners'}); shot('fillet-dialog',1.0); esc(2)
if want('timeline'):
    open_(CK+'/plate/plate-04-parametric.sc'); c('ui.editFeature',{'feature':'Plate'}); shot('timeline-edit',1.0); esc(2)
    c('ui.menu',{'target':{'type':'timeline','feature':'Corners'}}); shot('timeline-menu',0.6); esc(1)
if want('parameters'):
    open_(CK+'/plate/plate-04-parametric.sc'); c('ui.start',{'command':'parameters.change'}); shot('parameters-dialog',1.0); esc(2)
    ex('parameters.change',{'name':'width','expression':'100'}); c('ui.view',{'view':'fit'}); shot('parameters-width-100',0.8); ex('edit.undo')
if want('file'):
    open_(CK+'/plate/plate-04-parametric.sc'); h={x['name']:x for x in c('ui.handles')}; f=h['appbar:file']; c('ui.click',{'x':f['x'],'y':f['y']}); shot('file-menu',0.6); esc(1)
    c('ui.start',{'command':'file.export'}); shot('export-dialog',1.0); esc(2)
if want('box'):
    open_(CK+'/box/box-02-shell.sc'); c('ui.editFeature',{'feature':'Hollow'}); shot('shell-dialog',1.0); esc(2)
    open_(CK+'/box/box-03-lid.sc'); c('ui.editFeature',{'feature':'Lid plane'}); shot('offset-plane-dialog',1.0); esc(2)
    open_(CK+'/box/box-04-vents.sc'); c('ui.editFeature',{'feature':'Vents'}); shot('pattern-dialog',1.0); esc(2)
    open_(CK+'/box/box-05-finished.sc'); ex('inspect.section',{'plane':'XZ','flip':True}); shot('section-view',1.0); ex('inspect.section',{'clear':True})
    c('ui.editFeature',{'feature':'Lid chamfer'}); shot('chamfer-dialog',1.0); esc(2)
    c('ui.editFeature',{'feature':'Vent'}); shot('vent-sketch-extrude',1.0); esc(2)
if want('comb'):
    open_(CK+'/comb/comb-04-configs.sc'); c('ui.start',{'command':'config.table'}); shot('config-table',1.0); esc(2)
    ex('config.activate',{'row':'L'}); c('ui.view',{'view':'fit'}); shot('config-L',0.8); ex('config.activate',{'row':'S'}); c('ui.view',{'view':'fit'}); shot('config-S',0.8); ex('config.activate',{'row':'M'})
    r=ex('parameters.change',{'name':'comb_w','expression':'20'}); print(json.dumps(r)[:300]); c('ui.view',{'view':'fit'}); c('ui.menu',{'target':{'type':'timeline','feature':'Corners'}}); shot('feature-error',1.0); esc(1); c('ui.messages',{'open':True}); shot('feature-error-messages',0.8); c('ui.messages',{'open':False}); ex('edit.undo'); c('ui.view',{'view':'fit'})
    c('ui.start',{'command':'inspect.parameter_sweep'}); shot('sweep-dialog',1.0); esc(2)
    c('ui.editFeature',{'feature':'Slots'}); shot('comb-pattern-dialog',1.0); esc(2)
if want('prefs'):
    open_(CK+'/plate/plate-04-parametric.sc'); c('ui.prefs',{'open':True}); shot('preferences',1.0); esc(2)
if want('search'):
    c('ui.palette',{'text':'fillet','open':True}); shot('command-search',0.6); c('ui.palette',{'open':False})
if want('measure'):
    open_(CK+'/plate/plate-04-parametric.sc'); c('ui.start',{'command':'inspect.measure'}); shot('measure-dialog',1.0); esc(2)
print('done')
