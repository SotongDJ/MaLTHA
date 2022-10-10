from pathlib import Path
# from pyStaticGen.post import convert
from post import convert
Path("mid_files").mkdir(parents=True,exist_ok=True)
for post_path in Path("mid_files").glob('*'):
    Path(post_path).unlink()
convert()
