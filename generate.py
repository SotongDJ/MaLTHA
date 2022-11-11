# %%
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

from format import formator


class generator:
    def __init__(self,format=formator()) -> None:
        self.base_info = json.load(open("mid_files/base.json"))
        self.categories_info = json.load(open("mid_files/categories.json"))
        self.pages_dict = json.load(open("mid_files/page.json"))
        self.posts_list = json.load(open("mid_files/post.json"))
        self.format = format
        self.currentISO = datetime.now(tz=timezone(timedelta(hours=8),name="UTC+8")).isoformat()  # type: ignore
        print(F"Current time: {self.currentISO}")

    def get(self,input_str:str) -> str:
        return self.format.structure[input_str]

    def template(self,input_str:str,input_dict:dict) -> str:
        return self.format.structure[input_str].format(**input_dict)

    def post(self) -> None:
        for post_dict in self.posts_list:
            # post_dict = self.posts_list[0]
            base_dict = dict()
            base_dict.update(self.format.structure)
            base_dict["layout_content"] = self.get("layout_post")
            base_dict.update(self.base_info)
            base_dict.update(post_dict)
            base_dict["canonical_url"] = post_dict["post_url"]
            base_dict["post_content"] = post_dict["content_full"]
            base_str = self.get("layout_default").format(**base_dict).format(**base_dict)
            short_canonical_str = post_dict["short_canonical"]
            if "{" in base_str:
                print(F"ERROR: need more formatting {short_canonical_str}")
            url_list = ["docs"+n.replace(self.base_info["base_url"],"") for n in post_dict["post_urls"]]
            for path_str in url_list:
                Path(path_str).mkdir(parents=True,exist_ok=True)
                with open(F"{path_str}/index.html","w") as target:
                    target.write(base_str)

    def page(self) -> None:
        keys_list = sorted(list(self.pages_dict.keys()))
        pages_list = [self.pages_dict[n] for n in keys_list]
        # page_dict = self.pages_dict["🔖 關於 About"]
        for page_dict in pages_list:
            if "page_content" in page_dict.keys():
                base_dict = dict()
                base_dict.update(self.format.structure)
                base_dict["layout_content"] = self.get("layout_page")
                base_dict.update(self.base_info)
                base_dict.update(page_dict)
                base_dict["canonical_url"] = page_dict["page_url"]
                base_dict["current_iso8601"] = self.currentISO
                frame_str = base_dict["page_content"] if "base" in base_dict.keys() else self.get("layout_default")
                base_str = frame_str.format(**base_dict).format(**base_dict)
                short_canonical_str = page_dict["page_title"]
                if "frame" in page_dict.keys() or "layout" in page_dict.keys():
                    base_str = base_str.format(**base_dict)
                if "{" in base_str:
                    print(F"ERROR: need more formatting {short_canonical_str}")
                normal_str = self.template("format_pages_in_sidebar",page_dict)
                active_str = self.template("format_active_pages_in_sidebar",page_dict)
                if normal_str in base_str:
                    base_str = base_str.replace(normal_str,active_str)
                url_list = ["docs"+n.replace(self.base_info["base_url"],"") for n in page_dict["page_urls"]]
                for path_str in url_list:
                # path_str = url_list[0]
                    filename_str = str()
                    if path_str.split("/")[-1] == "":
                        Path(path_str).mkdir(parents=True,exist_ok=True)
                        filename_str = "index.html"
                    elif "." in path_str.split("/")[-1]:
                        Path(path_str).parent.mkdir(parents=True,exist_ok=True)
                        filename_str = str()
                    else:
                        Path(path_str).mkdir(parents=True,exist_ok=True)
                        filename_str = "/index.html"
                    with open(F"{path_str}{filename_str}","w") as target:
                        target.write(base_str)

    def category(self):
        for category_dict in self.categories_info.values():
            base_dict = dict()
            base_dict.update(self.format.structure)
            base_dict["layout_content"] = self.get("layout_category")
            base_dict.update(self.base_info)
            base_dict.update(category_dict)
            base_str = self.get("layout_default").format(**base_dict).format(**base_dict)
            short_canonical_str = category_dict["category_title"]
            if "{" in base_str:
                print(F"ERROR: need more formatting {short_canonical_str}")
            url_str = "docs"+category_dict["category_url"].replace(self.base_info["base_url"],"")
            Path(url_str).mkdir(parents=True,exist_ok=True)
            with open(F"{url_str}/index.html","w") as target:
                target.write(base_str)

    def pagination(self):
        posts_list = self.base_info["post_member_list"]
        paginate_format = self.base_info["paginate_format"]
        paginate_count = len(posts_list)
        paginate_number = self.base_info["paginate_number"]
        paginate_left = paginate_count%paginate_number
        paginate_ceil = math.ceil(paginate_count/paginate_number)
        paginate_dict = dict()
        for pag_num in range(paginate_ceil):
            pag_cond = ((pag_num == paginate_ceil - 1) and (paginate_left > 0))
            paginate_length = paginate_left if pag_cond else paginate_number
            self.start_num = pag_num*paginate_number
            self.end_num = (pag_num*paginate_number)+paginate_length
            paginate_dict[pag_num] = [posts_list[pos_num] for pos_num in range(self.start_num,self.end_num)]
        for page_num, pag_list in paginate_dict.items():
            page_hold = paginate_format.format(num=page_num+1)
            post_dict = dict()
            post_dict.update(self.format.structure)
            post_dict.update(self.base_info)
            post_dict["title"] = self.base_info["base_title"]
            post_dict["layout_content"] = self.get("layout_pagination")
            post_dict["pagination_content_list"] = "".join(pag_list)
            post_dict["canonical_url"] = self.base_info["base_url"]+page_hold
            if page_num == len(paginate_dict)-1:
                post_dict["pagination_older_button"] = self.get("format_pagination_older_froze")
            else:
                old_hold = paginate_format.format(num=page_num+2)
                post_dict["pagination_older_button"] = self.get("format_pagination_older_active").format(old_hold)
            url_list = list()
            if page_num == 0:
                post_dict["pagination_newer_button"] = self.get("format_pagination_newer_froze")
                url_list.append("docs/")
            elif page_num == 1:
                post_dict["pagination_newer_button"] = self.get("format_pagination_newer_active").format("/")
            else:
                new_hold = paginate_format.format(num=page_num-1)
                post_dict["pagination_newer_button"] = self.get("format_pagination_newer_active").format(new_hold)
            base_str = self.get("layout_default").format(**post_dict).format(**post_dict)
            url_list.append("docs"+page_hold)
            for path_str in url_list:
                Path(path_str).mkdir(parents=True,exist_ok=True)
                with open(F"{path_str}/index.html","w") as target:
                    target.write(base_str)

# %%
if __name__ == "__main__":
    Generate = generator()
# %%
