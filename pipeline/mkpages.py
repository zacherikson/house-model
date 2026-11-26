"""Builds the GitHub Pages site from site/.

site/index.html is written for the claude.ai artifact host, which wraps it in a document skeleton.
This script adds that skeleton so the same page works as a plain web page, and copies the data
and textures next to it.  Usage: python3 pipeline/mkpages.py _site
"""
import os, shutil, sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(root, '_site'))
site = os.path.join(root, 'site')

if os.path.isdir(out):
    shutil.rmtree(out)
os.makedirs(out)

page = open(os.path.join(site, 'index.html'), encoding='utf-8').read()
head = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n')
open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(head + page + '\n</html>\n')
shutil.copy(os.path.join(site, 'house.json'), out)
shutil.copytree(os.path.join(site, 'tex'), os.path.join(out, 'tex'))
print('Wrote', out)
