"""Module providingFunction site generator"""
import argparse
from subprocess import call

from MaLTHA.convert import Convertor
from MaLTHA.database import Formator
from MaLTHA.generate import Generator

parser = argparse.ArgumentParser(description="generate webpage for github pages")
parser.add_argument("--skip", help="skip docs process", action="store_true")
parser.add_argument("--debug", help="debug mode", action="store_true")
args = parser.parse_args()

if args.skip:
    print("note: skip step 1 and step 2")
else:
    print("step 1: remove docs recursively")
    call(["rm","-r","docs"])
    print("step 2: copy static_files as docs recursively")
    call(["cp","-r","static_files","docs"])

print("step 3: remove mid_files recursively")
call(["rm","-r","mid_files"])

print("step 4: load include and layout")
Format = Formator()
Format.load()

print("step 5: convert files into JSONs")
if args.debug:
    Convert = Convertor(fmt=Format,bu_b=False)
else:
    Convert = Convertor(fmt=Format)
Convert.post()
Convert.category()
Convert.relate()
Convert.atom()
Convert.page()
Convert.output()

print("step 6: generate webpages from JSONs")
Generate = Generator(fmt=Format)
print("step 6-1: generate posts")
Generate.post()
print("step 6-2: generate pages")
Generate.page()
print("step 6-3: generate categories")
Generate.category()
print("step 6-4: complete pagination")
if Generate.base_info["paginate_format"] != "":
    Generate.pagination()
