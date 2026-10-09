"""Create small, complete STL jobs for mixed training and held-out evaluation."""
import argparse
import shutil
from pathlib import Path
import numpy as np
from run_pipeline import ROOT
from train import write_json
import trimesh

def make(out):
    out=Path(out).resolve()
    out.mkdir(parents=True,exist_ok=False)
    sample=ROOT.parent/'TEAM_PROJECT/week1/environment/examples/sample_job'
    template=trimesh.load_mesh(sample/'target.stl')
    definitions=[('single_train',[(0,0)],1,4),('islands_train',[(-150,0),(150,0)],1,2),
                 ('single_evaluation',[(0,0)],1,8),
                 ('islands_heldout',[(-140,-30),(140,30)],1,3),
                 ('layers_heldout',[(-140,-30),(140,30)],2,3)]
    cases={}
    for name,centers,layers,n in definitions:
        job=out/name
        job.mkdir()
        shutil.copy2(sample/'config.yaml',job/'config.yaml')
        meshes=[]
        records=[]
        for x,y in centers:
            mesh=template.copy()
            mesh.vertices[:,2]*=layers
            mesh.apply_translation((x,y,0))
            meshes.append(mesh)
        for layer in range(layers):
            for x,y in centers:
                xs=np.linspace(x-40,x+40,n+1)
                for a,b in zip(xs[:-1],xs[1:]):
                    records.append(dict(task_id=len(records),layer=layer,start_xyz_mm=[float(a),float(y),float(2*(layer+1))],
                                        end_xyz_mm=[float(b),float(y),float(2*(layer+1))]))
        trimesh.util.concatenate(meshes).export(job/'target.stl')
        write_json(job/'tasks.json',records)
        cases[name]=dict(name=name,job=name,tasks_json=name+'/tasks.json')
    data=dict(version=1,reach_margin_mm=1.,train=[cases['single_train'],cases['islands_train']],
              evaluation=[cases[n] for n in ('single_evaluation','islands_heldout','layers_heldout')])
    write_json(out/'dataset.json',data)
    return out/'dataset.json'

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    print(make(args.out))
