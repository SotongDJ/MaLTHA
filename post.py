from pathlib import Path
from markdown import markdown
from datetime import datetime
import json, tomlkit
config_dict = dict()
config_dict.update(tomlkit.load(open("config.toml")))
baseurl_str = config_dict["base_url"]
category_in_post_str = config_dict["format_categories_in_post"]
member_in_categories_str = config_dict["format_member_in_categories"]
def convert():
    posts_dict = dict()
    categories_dict = dict()
    for post_path in Path("post_files").glob('*.md'):
        content_list = open(post_path).read().split(config_dict["separator_header"])
        header_dict = dict()
        header_dict.update(tomlkit.loads(content_list[1]))
        canonical_str = header_dict["short"][0]
        date_obj = datetime.fromisoformat(header_dict["date"])
        datetime_str = date_obj.strftime("%Y/%m/%d")

        category_parent_dict = dict()
        category_content_list = list()
        for category_str in header_dict["categories"]:
            category_child_dict = {
                "category_title" : category_str,
                "category_url" : F"{baseurl_str}/category/{category_str}/",
            }
            category_parent_dict[category_str] = category_child_dict
            category_content_list.append(category_in_post_str.format(**category_child_dict))
            category_detail_dict = categories_dict.get(category_str,dict())
            category_detail_dict.update(category_child_dict)
            categories_dict[category_str] = category_detail_dict

        categories_str = "/".join(header_dict["categories"])
        url_list = [F"{baseurl_str}/{categories_str}/{datetime_str}/{n}/" for n in header_dict["short"]] # type: ignore
        url_list.extend([F"{baseurl_str}/{categories_str}/{n}/" for n in header_dict["short"]]) # type: ignore
        url_list.extend([F"{baseurl_str}/{datetime_str}/{n}/" for n in header_dict["short"]]) # type: ignore
        url_list.extend([F"{baseurl_str}/{n}/" for n in header_dict["short"]]) # type: ignore
        content_str = markdown(content_list[2])
        preview_str = content_str.split(config_dict["separator_preview"])[0]
        post_dict = {
            "title" : header_dict["title"],
            "short_list" : header_dict["short"],
            "short_canonical" : canonical_str,
            "categories_dict" : category_parent_dict,
            "date_iso" : header_dict["date"],
            "date_show" : date_obj.strftime("%a, %b %-d, %Y"),
            "date_822" : date_obj.strftime("%a, %d %b %y %T %z"),
            "post_urls" : url_list,
            "post_url" : F"{baseurl_str}/{datetime_str}/{canonical_str}/",
            "post_categories": "\n".join(category_content_list),
            "content_full" : content_str,
            "content_preview" : preview_str,
        }
        if canonical_str in posts_dict.keys():
            print(F"ERROR: duplicate canonical_str [{canonical_str}]")
        else:
            for category_str in post_dict["categories_dict"].keys():
                category_detail_dict = categories_dict.get(category_str,dict())
                category_member_dict = category_detail_dict.get("member",dict())
                category_member_dict[canonical_str] = {
                    "member_title" : post_dict["title"],
                    "member_url" : post_dict["post_url"],
                }
                category_detail_dict["member"] = category_member_dict
                categories_dict[category_str] = category_detail_dict
            posts_dict[canonical_str] = post_dict
    with open("mid_files/post.json","w") as t:
        json.dump(posts_dict,t,indent=0)
    for category_str in categories_dict.keys():
        category_detail_dict = categories_dict[category_str]
        content_list = list()
        for member_dict in category_detail_dict["member"].values():
            content_list.append(member_in_categories_str.format(**member_dict))
        category_detail_dict["category_content"] = "\n".join(content_list)
        categories_dict[category_str] = category_detail_dict
    with open("mid_files/categories.json","w") as t:
        json.dump(categories_dict,t,indent=0)
