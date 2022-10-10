from pathlib import Path
from markdown import markdown
from datetime import datetime
import json, tomlkit
config_doc = tomlkit.load(open("config.toml"))
def convert():
    posts_dict = dict()
    categories_dict = dict()
    for post_path in Path("post_files").glob('*.md'):
        content_list = open(post_path).read().split("---")
        header_dict = tomlkit.loads(content_list[1])
        content_str = markdown(content_list[2])
        post_dict = dict()
        post_dict.update(header_dict)
        canonical_str = post_dict["short"][0]
        date_obj = datetime.fromisoformat(post_dict["date"])
        post_dict["post.date"] = date_obj.strftime("%a, %b %-d, %Y")
        datetime_str = date_obj.strftime("%Y/%m/%d")
        categories_str = "/".join(post_dict["categories"])
        url_list = [F"/{categories_str}/{datetime_str}/{n}/" for n in header_dict["short"]] # type: ignore
        url_list.extend([F"/{categories_str}/{n}/" for n in header_dict["short"]]) # type: ignore
        url_list.extend([F"/{datetime_str}/{n}/" for n in header_dict["short"]]) # type: ignore
        url_list.extend([F"/{n}/" for n in header_dict["short"]]) # type: ignore
        post_dict["post.urls"] = url_list
        post_dict["post.url"] = F"/{datetime_str}/{canonical_str}/"
        post_dict["content"] = content_str
        if canonical_str in posts_dict.keys():
            print(F"ERROR: duplicate canonical_str [{canonical_str}]")
        else:
            for category_str in post_dict["categories"]:
                category_list = categories_dict.get(category_str,list())
                category_list.append(post_dict["post.url"])
                categories_dict[category_str] = category_list
            posts_dict[canonical_str] = post_dict
    with open("mid_files/post.json","w") as t:
        json.dump(posts_dict,t,indent=0)
    with open("mid_files/categories.json","w") as t:
        json.dump(categories_dict,t,indent=0)
