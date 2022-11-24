"""Module providingFunction prepare dictionary for other scripts"""
from pathlib import Path

import tomlkit
from markdown2 import markdown


class Formator:
    """read and convert ToMH files to dictionary"""
    def __init__(self) -> None:
        self.structure = {}
        self.base = {}
        self.base.update(tomlkit.load(open("config.toml",encoding="utf-8")))
    def parse(self,input_str:str) -> dict:
        """parse ToMH into dictionary"""
        parsed_dict = {}
        input_split_list = input_str.replace("+++\n","").split("<!--break ")
        input_list = [n.split(" content-->") for n in input_split_list if n != ""]
        for do_list in input_list:
            if len(do_list) == 2:
                note_str, content_str = do_list
                note_list = [n.split(":") for n in note_str.split(" ") if n != ""]
                note_dict = {x:y for x,y in note_list}
                if note_dict["type"] == "header":
                    parsed_dict["header"] = tomlkit.loads(content_str)
                elif note_dict["type"] == "content":
                    if note_dict["format"] == "md":
                        current_str = markdown(content_str,extras=["fenced-code-blocks"])
                    else:
                        current_str = content_str
                    parsed_dict["content"] = current_str
                else:
                    type_dict = parsed_dict.get(note_dict["type"],{})
                    stored_str = type_dict.get(note_dict["title"],str())
                    combined_str = stored_str + content_str
                    simple_str = self.oneline(combined_str)
                    type_dict[note_dict["title"]] = simple_str
                    parsed_dict[note_dict["type"]] = type_dict
            else:
                print(F"WARN: {do_list}")
        return parsed_dict
    def load(self) -> None:
        """parse MoTH frame files"""
        target_list = []
        for folder_str in ["include_files","layout_files","page_files"]:
            target_list.extend(sorted(list(Path(folder_str).glob('*.*ml'))))
        for target_path in target_list:
            target_dict = self.parse(open(target_path,encoding="utf-8").read())
            for t_str in ["include","layout","format"]:
                if t_str in target_dict:
                    self.structure.update({F"{t_str}_{x}":y for x,y in target_dict[t_str].items()})
    def export(self):
        """export as TOML"""
        Path("mid_files").mkdir(exist_ok=True)
        with open("mid_files/structure.toml","w",encoding="utf-8") as toml_handle:
            tomlkit.dump(self.structure,toml_handle)
    def oneline(self,input_str:str) -> str:
        """shrink into one line string"""
        return input_str.replace("\n","").replace("    ","")
