from pathlib import Path
# from pyStaticGen.post import convert
import post
Path("mid_files").mkdir(parents=True,exist_ok=True)
for post_path in Path("mid_files").glob('*'):
    Path(post_path).unlink()
post.convert()
