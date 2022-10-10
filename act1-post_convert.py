from pathlib import Path
from markdown import markdown
import json, tomlkit
for post_path in Path("post_files").glob('*.md'):
    content_list = open(post_path).read().split("---")
    header_dict = tomlkit.loads(content_list[1])
    content_str = markdown(content_list[2])
    output_dict = dict()
    output_dict.update(header_dict)
    output_dict["content"] = content_str
    with open(str(post_path).replace(".md",".json").replace("post_files/","mid_post_files/"),"w") as t:
        json.dump(output_dict,t,indent=0)
