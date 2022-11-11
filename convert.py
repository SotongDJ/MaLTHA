import json
from datetime import datetime
from pathlib import Path, PosixPath

from format import formator


class convertor:
    def __init__(self,baseurl_bool=True,format=formator()):
        self.format = format
        self.base_dict = dict()
        self.base_dict.update(self.format.base)
        self.baseurl_str = self.base_dict["base_url"] if baseurl_bool else str()
    #
    def template(self,input_str:str,input_dict:dict) -> str:
        return self.format.structure[input_str].format(**input_dict)
    #
    def is_target(self,folder:PosixPath) -> bool:
        output = folder.is_dir()
        folder_name = str(folder.name)
        if folder_name[0] == ".":
            output = False
        if folder_name[0] == "_":
            output = False
        if "_files" in folder_name:
            output = False
        if folder_name == "run":
            output = False
        if folder_name == "docs":
            output = False
        return output
    #
    def post(self):
        posts_list = list()
        posts_dict = dict()
        categories_dict = dict()
        post_member_list = list()
        post_atom_list = list()
        post_folder_list = [n for n in Path.cwd().iterdir() if self.is_target(n)]  # type: ignore
        post_files_list = list()
        for post_folder_PosixPath in post_folder_list:
            post_files_list.extend(sorted(list(post_folder_PosixPath.glob('*.*'))))
        for post_path in post_files_list:
            name_list = post_path.name.split(".")
            extention_str = name_list[-1]
            if len(name_list) > 1 and extention_str in ["md","html"]:
                content_dict = self.format.parse(open(post_path).read())
                header_dict = dict()
                header_dict.update(content_dict["header"])
                canonical_str = header_dict["short"][0]
                date_obj = datetime.fromisoformat(header_dict["date"])
                datetime_str = date_obj.strftime("%Y/%m/%d")
                #
                category_parent_dict = dict()
                category_content_list = list()
                for category_str in header_dict["categories"]:
                    category_child_dict = {
                        "title" : "·".join([category_str,self.base_dict["base_title"]]),
                        "category_title" : category_str,
                        "category_url" : F"{self.baseurl_str}/category/{category_str}/",
                        "opengraph_description" : self.base_dict["category_preview"].format(category_str),
                    }
                    category_parent_dict[category_str] = category_child_dict
                    category_content_list.append(self.template("format_categories_in_post",category_child_dict))
                    #
                    category_detail_dict = categories_dict.get(category_str,dict())
                    category_detail_dict.update(category_child_dict)
                    categories_dict[category_str] = category_detail_dict
                #
                categories_str = "/".join(header_dict["categories"])
                url_list = [F"{self.baseurl_str}/{categories_str}/{datetime_str}/{n}/" for n in header_dict["short"]] # type: ignore
                url_list.extend([F"{self.baseurl_str}/{categories_str}/{n}/" for n in header_dict["short"]]) # type: ignore
                url_list.extend([F"{self.baseurl_str}/{datetime_str}/{n}/" for n in header_dict["short"]]) # type: ignore
                url_list.extend([F"{self.baseurl_str}/{n}/" for n in header_dict["short"]]) # type: ignore
                url_list.append(F"{self.baseurl_str}/post/{canonical_str}/")
                post_url_str = F"{self.baseurl_str}/{datetime_str}/{canonical_str}/"
                content_str = content_dict["content"]
                content_split_list = content_str.split(self.base_dict["separator_preview"])
                preview_str = self.format.oneline(content_split_list[0])
                more_word_str = self.base_dict["read_original"] if len(content_split_list) == 1 else self.base_dict["read_more"]
                more_url_str = """<a href="{}">{}</a>""".format(post_url_str,more_word_str)
                post_detail_dict = {
                    "title" : " · ".join([header_dict["title"],self.base_dict["base_title"]]),
                    "short_list" : header_dict["short"],
                    "short_canonical" : canonical_str,
                    "categories_dict" : category_parent_dict,
                    "date_iso" : header_dict["date"],
                    "date_show" : date_obj.strftime("%a, %b %-d, %Y"),
                    "date_822" : date_obj.strftime("%a, %d %b %Y %T %z"),
                    "date_8601" : date_obj.isoformat(),
                    "post_title" : header_dict["title"],
                    "post_urls" : url_list,
                    "post_url" : post_url_str,
                    "post_categories": "".join(category_content_list),
                    "content_full" : content_str,
                    "content_preview" : preview_str,
                    "more_element" : more_url_str,
                }
                post_dict = dict()
                post_dict.update(header_dict)
                post_dict.update(post_detail_dict)
                if canonical_str in posts_dict.keys():
                    print(F"ERROR: duplicate canonical_str [{canonical_str}]")  # type: ignore
                else:
                    for category_str in post_dict["categories_dict"].keys():
                        category_detail_dict = categories_dict.get(category_str,dict())
                        category_member_dict = category_detail_dict.get("member",dict())
                        title_str = post_dict["post_title"]
                        title_short_str = title_str[:15]+"..." if len(title_str) > 18 else title_str
                        category_member_dict[canonical_str] = {
                            "member_title" : title_str,
                            "member_short" : title_short_str,
                            "member_url" : post_dict["post_url"],
                            "member_date" : post_dict["date_show"],
                        }
                        category_detail_dict["member"] = category_member_dict
                        categories_dict[category_str] = category_detail_dict
                    posts_list.append(post_dict)
                    posts_dict[canonical_str] = len(posts_list)-1
        #
        categories_content_list = list()
        for category_str in categories_dict.keys():
            category_detail_dict = categories_dict[category_str]
            content_list = list()
            section_list = list()
            for member_dict in category_detail_dict["member"].values():
                content_list.append(self.template("format_member_in_category_content",member_dict))
                section_list.append(self.template("format_member_in_category_section",member_dict))
            category_detail_dict["category_content"] = "".join(content_list)
            category_detail_dict["category_section"] = "".join(section_list)
            categories_dict[category_str] = category_detail_dict
            categories_content_list.append(self.template("format_categories_by_section",category_detail_dict))
        self.base_dict["categories_content_list"] = "".join(categories_content_list)
        #
        for post_pos, post_dict in enumerate(posts_list):
            canonical_str = post_dict["short_canonical"]
            releted_dict = dict()
            for category_str in post_dict["categories_dict"].keys():
                category_member_dict = categories_dict[category_str]["member"]
                releted_dict.update({x:self.template("format_related_member",y) for x,y in category_member_dict.items()})
            related_order_dict = {posts_dict[n]:n for n in releted_dict.keys() if n != canonical_str}
            related_order_list = [releted_dict[related_order_dict[n]] for n in sorted(list(related_order_dict.keys()),reverse=True)]
            related_list = related_order_list[:3] if len(related_order_list) > 3 else related_order_list
            related_str = "".join(related_list)
            # post_dict["related_order_list"] = related_order_list
            if "format_related_frame" in self.format.structure.keys():
                post_dict["related_content"] = self.template("format_related_frame",{"related_posts_list":related_str})
            posts_list[post_pos] = post_dict
        #
        reversed_posts_dict = {y:x for x,y in posts_dict.items()}
        reversed_order_list = [posts_list[post_pos] for post_pos in sorted(reversed_posts_dict.keys(),reverse=True)]
        for post_dict in reversed_order_list:
            if post_dict["content_full"] == post_dict["content_preview"]:
                post_member_list.append(self.template("format_post_container_full",post_dict))
            else:
                post_member_list.append(self.template("format_post_container_preview",post_dict))
            atom_dict = dict()
            atom_dict.update(post_dict)
            atom_bool = self.base_dict["base_url"] in post_dict["post_url"]
            atom_dict["base_url"] = str() if atom_bool else self.base_dict["base_url"]
            post_atom_list.append(self.template("format_atom_post",atom_dict))
        self.base_dict["post_member_list"] = post_member_list
        self.base_dict["post_content_list"] = "".join(post_member_list)
        self.base_dict["post_atom_list"] = post_atom_list
        self.base_dict["atom_content_list"] = "".join(post_atom_list)
        #
        #
        Path("mid_files").mkdir(exist_ok=True)
        with open("mid_files/post.json","w") as t:
            json.dump(posts_list,t,indent=0)
        with open("mid_files/post_pos.json","w") as t:
            json.dump(posts_dict,t,indent=0)
        with open("mid_files/categories.json","w") as t:
            json.dump(categories_dict,t,indent=0)
        with open("mid_files/base.json","w") as t:
            json.dump(self.base_dict,t,indent=0)
    #
    def page(self):
        pages_dict = dict()
        for page_path in sorted(list(Path("page_files").glob('*.*'))):
            name_list = page_path.name.split(".")
            extention_str = name_list[-1]
            content_dict = self.format.parse(open(page_path).read())
            header_dict = dict()
            header_dict.update(content_dict["header"])
            canonical_str = header_dict["title"]
            url_list = [F"{self.baseurl_str}{n}" for n in header_dict["path"]]
            url_str = url_list[0]
            if header_dict.get("skip","") != "content":
                url_list.append(F"{self.baseurl_str}/pages{url_str}")
            page_detail_dict = {
                "title" : " · ".join([canonical_str,self.base_dict["base_title"]]),
                "page_title" : canonical_str,
                "page_urls" : url_list,
                "page_url" : url_str,
            }
            page_dict = dict()
            page_dict.update(header_dict)
            page_dict.update(page_detail_dict)
            type_list = ["base","layout","frame"]
            type_in_header_list = [n for n in type_list if n in header_dict.keys()]
            type_in_content_list = [n for n in type_in_header_list if header_dict[n] in content_dict.get("frame",dict())]
            if header_dict.get("skip","") != "content":
                if "content" in content_dict.keys():
                    page_dict["page_content"] = content_dict["content"]
                elif len(type_in_content_list) > 0:
                    type_str = type_in_content_list[0]
                    page_dict["page_content"] = content_dict["frame"][header_dict[type_str]]
                else:
                    print(F"ERROR: can't get content from {canonical_str}")
            if "layout" in header_dict.keys():
                if header_dict["layout"] in content_dict["frame"].keys():
                    page_dict["layout_content"] = content_dict["frame"][header_dict["layout"]]
                else:
                    print(F"ERROR: can't get layout from {canonical_str}")
            page_dict.update({n:header_dict[n] for n in type_in_header_list})
            if header_dict.get("skip","") == "list":
                page_dict["skip_list"] = ""
            if canonical_str in pages_dict.keys():
                print(F"ERROR: duplicate canonical_str [{canonical_str}]")
            else:
                pages_dict[canonical_str] = page_dict
        side_page_list = [n for n in pages_dict.values() if "skip_list" not in n.keys()]
        page_content_list = [self.template("format_pages_in_sidebar",n) for n in side_page_list]
        self.base_dict["page_content_list"] = "".join(page_content_list)
        #
        Path("mid_files").mkdir(exist_ok=True)
        with open("mid_files/page.json","w") as t:
            json.dump(pages_dict,t,indent=0)
        with open("mid_files/base.json","w") as t:
            json.dump(self.base_dict,t,indent=0)
