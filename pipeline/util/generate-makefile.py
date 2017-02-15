#!/usr/bin/env python3

__author__ = 'cjm'

import argparse
import yaml
from json import dumps

def main():

    parser = argparse.ArgumentParser(description='GO Metadata'
                                                 '',
                                     formatter_class=argparse.RawTextHelpFormatter)

    print("## AUTOGENERATED MAKEFILE\n")
    parser.add_argument('files',nargs='*')
    args = parser.parse_args()
    artifacts = []
    artifacts_by_dataset = {}
    for fn in args.files:
        f = open(fn, 'r') 
        obj = yaml.load(f)
        artifacts.extend(obj['datasets'])
        f.close()
    for a in artifacts:
        if 'source' not in a:
            # TODO
            print("## WARNING: no source for: {}".format(a['id']))
            continue
        ds = a['dataset']
        if ds == 'paint':
            print("## WARNING: Skipping PAINT: {}".format(a['id']))
            # TODO
            continue
        if ds == 'rnacentral':
            print("## WARNING: Skipping RNAC: {}".format(a['id']))
            # TODO
            continue
        
        if ds not in artifacts_by_dataset:
            artifacts_by_dataset[ds] = []
        artifacts_by_dataset[ds].append(a)
    for (ds,alist) in artifacts_by_dataset.items():
        generate_targets(ds, alist)
    targets = [all(ds) for ds in artifacts_by_dataset.keys()]
    rule('all_gafs', ' '.join(targets), 'echo done')
        
def generate_targets(ds, alist):
    types = [a['type'] for a in alist]

    print("## --------------------")
    print("## {}".format(ds))
    print("## --------------------")
    if 'gaf' not in types and 'gpad' not in types:
        print("# Metadata incomplete\n")
        rule(all(ds), '','echo no metadata')
        return
    
    rule(all(ds), targetdir(ds)+" "+filtered_gaf(ds)+" "+filtered_gpad(ds)+" "+gpi(ds))

    rule(targetdir(ds),'',
         'mkdir $@')
    
    # for now we assume everything comes from a GAF
    if 'gaf' in types:
        [gaf] = [a for a in alist if a['type']=='gaf']
        url = gaf['source']
        # GAF from source
        rule(src_gaf(ds),'',
             'wget --no-check-certificate {url} -O $@.tmp && mv $@.tmp $@ && touch $@'.format(url=url))
    rule(filtered_gaf(ds),src_gaf(ds),
         './util/filter-gaf.pl -i $< -w > $@.tmp && mv $@.tmp $@')
    rule(filtered_gpad(ds),filtered_gaf(ds),
         'owltools --gaf $< --write-gpad -o $@.tmp && mv $@.tmp $@')
    rule(gpi(ds),filtered_gaf(ds),
         'owltools --gaf $< --write-gpi -o $@.tmp && mv $@.tmp $@')

def targetdir(ds):
    return 'target/{ds}/'.format(ds=ds)
def all(ds):
    return 'all_'+ds
def src_gaf(ds):
    return '{dir}{ds}-src.gaf.gz'.format(dir=targetdir(ds),ds=ds)
def filtered_gaf(ds):
    return '{dir}{ds}-filtered.gaf'.format(dir=targetdir(ds),ds=ds)
def filtered_gpad(ds):
    return '{dir}{ds}-filtered.gpad'.format(dir=targetdir(ds),ds=ds)
def gpi(ds):
    return 'target/{ds}.gpi'.format(dir=targetdir(ds),ds=ds)

def rule(tgt,dep,ex='echo done'):
    s = "{tgt}: {dep}\n\t{ex}\n".format(tgt=tgt,dep=dep,ex=ex)
    print(s)

if __name__ == "__main__":
    main()
    