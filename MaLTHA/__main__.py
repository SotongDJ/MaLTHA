"""Module providingFunction site generator"""
import argparse
import shutil

from MaLTHA.convert import Convertor
from MaLTHA.database import Formator
from MaLTHA.generate import Generator

parser = argparse.ArgumentParser(
    prog="python -m MaLTHA",
    description="MaLTHA static site generator — converts Markdown/HTML content into a deployable website.",
)
parser.add_argument(
    "--skip",
    help="skip steps 1-2: do not clear and rebuild docs/ from static_files/",
    action="store_true",
)
parser.add_argument(
    "--debug",
    help="disable base_url substitution (useful for inspecting output locally)",
    action="store_true",
)
args = parser.parse_args()

if args.skip:
    print("note: skip step 1 and step 2")
else:
    print("step 1: remove docs recursively")
    shutil.rmtree("docs", ignore_errors=True)
    print("step 2: copy static_files as docs recursively")
    shutil.copytree("static_files", "docs")

print("step 3: remove mid_files recursively")
shutil.rmtree("mid_files", ignore_errors=True)

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
