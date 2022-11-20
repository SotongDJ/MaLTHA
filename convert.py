"""Module providingFunction convert markdown/HTML/plain text into JSON"""
import json
from datetime import datetime
from pathlib import Path, PosixPath

from database import Formator


class Convertor:
    """convert"""
    def __init__(self,bu_b=True,fmt=Formator()):
        self.fmt = fmt
        self.bs_d = {}
        self.bs_d.update(self.fmt.base)
        self.bu_s = self.bs_d["base_url"] if bu_b else str()
        self.pos_l = [] # posts_list
        self.cts_d = {} # categories_dict
        self.cts_c_l = [] # categories_content_list
        self.pgs_d = {} # pages_dict
    def template(self,input_str:str,input_dict:dict) -> str:
        """template"""
        return self.fmt.structure[input_str].format(**input_dict)
    def is_target(self,folder:PosixPath) -> bool:
        """for skip folder"""
        output = folder.is_dir()
        folder_name = str(folder.name)
        if folder_name[0] in {".","_"}:
            output = False
        if "_files" in folder_name:
            output = False
        if folder_name in {"docs","run"}:
            output = False
        return output
    def json(self,input_obj,target_path):
        """output as json"""
        with open(target_path,"w",encoding="utf-8") as target_handle:
            json.dump(input_obj,target_handle,indent=0)
    def post_ct(self,categories_list):
        """"Prepare category member dictionary from post"""
        category_parent_dict = {}
        category_content_list = []
        for category_str in categories_list:
            opengraph_description_str = self.bs_d["category_preview"].format(category_str)
            category_child_dict = {
                "title" : "·".join([category_str,self.bs_d["base_title"]]),
                "category_title" : category_str,
                "category_url" : self.bu_s+F"/category/{category_str}/",
                "canonical_url" : self.bu_s+F"/category/{category_str}/",
                "opengraph_description" : opengraph_description_str,
            }
            category_parent_dict[category_str] = category_child_dict
            tfc_str = self.template("format_categories_in_post",category_child_dict)
            category_content_list.append(tfc_str)
            #
            category_detail_dict = self.cts_d.get(category_str,{})
            category_detail_dict.update(category_child_dict)
            self.cts_d[category_str] = category_detail_dict
        return category_parent_dict,category_content_list
    def ct_member(self,post_dict):
        """Generate category member dictionary from post_ct()"""
        for category_str in post_dict["categories_dict"].keys():
            category_detail_dict = self.cts_d.get(category_str,{})
            category_member_dict = category_detail_dict.get("member",{})
            title_str = post_dict["post_title"]
            title_short_str = title_str[:15]+"..." if len(title_str) > 18 else title_str
            category_member_dict[post_dict["short_canonical"]] = {
                "member_title" : title_str,
                "member_short" : title_short_str,
                "member_url" : post_dict["post_url"],
                "member_date" : post_dict["date_show"],
            }
            category_detail_dict["member"] = category_member_dict
            self.cts_d[category_str] = category_detail_dict
    def path(self):
        """collect path for post"""
        post_paths = []
        for post_folder_posix_path in Path.cwd().iterdir():
            if self.is_target(post_folder_posix_path):
                post_paths.extend(sorted(list(post_folder_posix_path.glob('*.*'))))
        return post_paths
    def post(self):
        """convert func. for post"""
        for post_path in self.path():
            name_list = post_path.name.split(".")
            if len(name_list) > 1 and name_list[-1] in ["md","html"]:
                content_dict = self.fmt.parse(open(post_path,"r",encoding="utf-8").read())
                head_d = {}
                head_d.update(content_dict["header"])
                date_obj = datetime.fromisoformat(head_d["date"])
                dt_s = date_obj.strftime("%Y/%m/%d")
                # ct_p_d: category_parent_dict
                # ct_c_l: category_content_list
                ct_p_d,ct_c_l = self.post_ct(head_d["categories"])
                cts_s = "/".join(head_d["categories"])
                url_l = [self.bu_s+F"/{cts_s}/{dt_s}/{n}/" for n in head_d["short"]] # type: ignore
                url_l.extend([self.bu_s+F"/{cts_s}/{n}/" for n in head_d["short"]]) # type: ignore
                url_l.extend([self.bu_s+F"/{dt_s}/{n}/" for n in head_d["short"]]) # type: ignore
                url_l.extend([self.bu_s+F"/{n}/" for n in head_d["short"]]) # type: ignore
                url_l.append(self.bu_s+"/post/"+head_d["short"][0]+"/")
                post_url_str = self.bu_s+F"/{dt_s}/"+head_d["short"][0]+"/"
                content_split_list = content_dict["content"].split(self.bs_d["separator_preview"])
                if len(content_split_list) == 1:
                    more_word_str = self.bs_d["read_original"]
                else:
                    more_word_str = self.bs_d["read_more"]
                po_d = {} # po_d
                po_d.update(head_d)
                po_d.update({
                    "title" : " · ".join([head_d["title"],self.bs_d["base_title"]]),
                    "short_list" : head_d["short"],
                    "short_canonical" : head_d["short"][0],
                    "categories_dict" : ct_p_d,
                    "date_iso" : head_d["date"],
                    "date_show" : date_obj.strftime("%a, %b %-d, %Y"),
                    "date_822" : date_obj.strftime("%a, %d %b %Y %T %z"),
                    "date_8601" : date_obj.isoformat(),
                    "post_title" : head_d["title"],
                    "post_urls" : url_l,
                    "post_url" : post_url_str,
                    "post_categories": "".join(ct_c_l),
                    "content_full" : content_dict["content"],
                    "content_preview" : self.fmt.oneline(content_split_list[0]),
                    "more_element" : F"<a href=\"{post_url_str}\">{more_word_str}</a>",
                })
                self.ct_member(po_d)
                self.pos_l.append(po_d)
        self.check_post()
    def check_post(self):
        """Check post if duplicate or not"""
        pos_l = [post_dict["short_canonical"] for post_dict in self.pos_l]
        dup_l = [po for po in set(pos_l) if pos_l.count(po) > 1]
        if len(dup_l) > 0:
            print(F"ERROR: duplicate id; {dup_l}")
    def category(self):
        """prepare categories"""
        for category_str,detl_d in self.cts_d.items():
            content_list = []
            section_list = []
            for member_dict in detl_d["member"].values():
                content_list.append(self.template("format_member_in_category_content",member_dict))
                section_list.append(self.template("format_member_in_category_section",member_dict))
            detl_d["category_content"] = "".join(content_list)
            detl_d["category_section"] = "".join(section_list)
            self.cts_d[category_str] = detl_d
            self.cts_c_l.append(self.template("format_categories_by_section",detl_d))
        self.bs_d["categories_content_list"] = "".join(self.cts_c_l)
    def relate(self):
        """prepare related section"""
        frm_s = "format_related_member"
        pos_d = {po_d["short_canonical"]:i for i,po_d in enumerate(self.pos_l)}
        for pos, po_d in enumerate(self.pos_l):
            rlt_d = {} # related_dict
            for category_str in po_d["categories_dict"].keys():
                category_member_dict = self.cts_d[category_str]["member"]
                rlt_d.update({x:self.template(frm_s,y) for x,y in category_member_dict.items()})
            rlt_od_d = {pos_d[n]:n for n in rlt_d if n != po_d["short_canonical"]}
            rlt_od_l = [rlt_d[rlt_od_d[n]] for n in sorted(list(rlt_od_d.keys()),reverse=True)]
            related_list = rlt_od_l[:3] if len(rlt_od_l) > 3 else rlt_od_l
            related_str = "".join(related_list)
            # po_d["related_order_list"] = rlt_od_l
            frf_s = "format_related_frame"
            if frf_s in self.fmt.structure.keys():
                po_d["related_content"] = self.template(frf_s,{"related_posts_list":related_str})
            self.pos_l[pos] = po_d
    def atom(self):
        """prepare atom/preview section"""
        post_member_list = []
        post_atom_list = []
        rv_od_l = [self.pos_l[pos] for pos in range(len(self.pos_l)-1, -1, -1)]
        for post_dict in rv_od_l:
            if post_dict["content_full"] == post_dict["content_preview"]:
                post_member_list.append(self.template("format_post_container_full",post_dict))
            else:
                post_member_list.append(self.template("format_post_container_preview",post_dict))
            atom_dict = {}
            atom_dict.update(post_dict)
            atom_bool = self.bs_d["base_url"] in post_dict["post_url"]
            atom_dict["base_url"] = str() if atom_bool else self.bs_d["base_url"]
            post_atom_list.append(self.template("format_atom_post",atom_dict))
        self.bs_d["post_member_list"] = post_member_list
        self.bs_d["post_content_list"] = "".join(post_member_list)
        self.bs_d["post_atom_list"] = post_atom_list
        self.bs_d["atom_content_list"] = "".join(post_atom_list)
    def page(self):
        """convert func. for page"""
        for page_path in sorted(list(Path("page_files").glob('*.*'))):
            content_dict = self.fmt.parse(open(page_path,encoding="utf-8").read())
            head_d = {}
            head_d.update(content_dict["header"])
            url_l = [self.bu_s+F"{n}" for n in head_d["path"]]
            url_str = url_l[0]
            if head_d.get("skip","") != "content":
                url_l.append(self.bu_s+F"/pages{url_str}")
            page_detail_dict = {
                "title" : " · ".join([head_d["title"],self.bs_d["base_title"]]),
                "page_title" : head_d["title"],
                "page_urls" : url_l,
                "page_url" : url_str,
            }
            page_dict = {}
            page_dict.update(head_d)
            page_dict.update(page_detail_dict)
            type_list = ["base","layout","frame"]
            type_in_head_l = [n for n in type_list if n in head_d]
            frm_d = content_dict.get("frame",{})
            type_in_content_list = [n for n in type_in_head_l if head_d[n] in frm_d]
            if head_d.get("skip","") != "content":
                if "content" in content_dict.keys():
                    page_dict["page_content"] = content_dict["content"]
                elif len(type_in_content_list) > 0:
                    type_str = type_in_content_list[0]
                    page_dict["page_content"] = content_dict["frame"][head_d[type_str]]
                else:
                    print("ERROR: can't get content from "+head_d["title"])
            if "layout" in head_d:
                if head_d["layout"] in content_dict["frame"].keys():
                    page_dict["layout_content"] = content_dict["frame"][head_d["layout"]]
                else:
                    print("ERROR: can't get layout from "+head_d["title"])
            page_dict.update({n:head_d[n] for n in type_in_head_l})
            if head_d.get("skip","") == "list":
                page_dict["skip_list"] = ""
            if head_d["title"] in self.pgs_d:
                print("ERROR: duplicate canonical id ["+head_d["title"]+"]")
            else:
                self.pgs_d[head_d["title"]] = page_dict
        side_page_list = [n for n in self.pgs_d.values() if "skip_list" not in n.keys()]
        page_content_list = [self.template("format_pages_in_sidebar",n) for n in side_page_list]
        self.bs_d["page_content_list"] = "".join(page_content_list)
    def output(self):
        """output JSON files"""
        Path("mid_files").mkdir(exist_ok=True)
        self.json(self.bs_d,"mid_files/base.json")
        self.json(self.pos_l,"mid_files/post.json")
        pos_d = {po_d["short_canonical"]:i for i,po_d in enumerate(self.pos_l)}
        self.json(pos_d,"mid_files/post_pos.json")
        self.json(self.cts_d,"mid_files/categories.json")
        self.json(self.pgs_d,"mid_files/page.json")
