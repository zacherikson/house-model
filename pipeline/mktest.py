import sys
src,dst=sys.argv[1],sys.argv[2]
s=open(src).read()
s=s.replace('https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.min.js','./lib/three.module.min.js').replace('https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/','./lib/jsm/')
s=s.replace('<link rel="stylesheet" href="https://fonts.googleapis.com','<link rel="x" href="https://fonts.googleapis.com')
open(dst,'w').write('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'+s+'</html>')
