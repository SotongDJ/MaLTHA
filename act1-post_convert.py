from pathlib import Path
from markdown import markdown
from datetime import datetime
import json, tomlkit
config_doc = tomlkit.load(open("config.toml"))
baseurl_str = config_doc["base.url"]
for post_path in Path("post_files").glob('*.md'):
    content_list = open(post_path).read().split("---")
    header_dict = tomlkit.loads(content_list[1])
    content_str = markdown(content_list[2])
    output_dict = dict()
    output_dict.update(header_dict)
    date_obj = datetime.fromisoformat(output_dict["date"])
    output_dict["post.date"] = date_obj.strftime("%a, %b %-d, %Y")
    categories_str = "/".join(output_dict["categories"])
    datetime_str = date_obj.strftime("%Y/%m/%d")
    url_list = [F"{categories_str}/{datetime_str}/{n}/" for n in header_dict["short"]] # type: ignore
    url_list.extend([F"{categories_str}/{n}/" for n in header_dict["short"]]) # type: ignore
    url_list.extend([F"{datetime_str}/{n}/" for n in header_dict["short"]]) # type: ignore
    url_list.extend([F"{n}/" for n in header_dict["short"]]) # type: ignore
    output_dict["post.url"] = url_list
    output_dict["content"] = content_str
    with open(str(post_path).replace(".md",".json").replace("post_files/","mid_post_files/"),"w") as t:
        json.dump(output_dict,t,indent=0)
