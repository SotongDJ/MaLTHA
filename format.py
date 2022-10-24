from pathlib import Path

import tomlkit
from markdown2 import markdown


class formator:
    def __init__(self) -> None:
        self.structure = dict()
        self.base = dict()
        self.base.update(tomlkit.load(open("config.toml")))

    def parse(self,input_str:str) -> dict:
        parsed_dict = dict()
        input_list = [n.split(" content-->") for n in input_str.replace("+++\n","").split("<!--break ") if n != ""]
        for do_list in input_list:
            if len(do_list) == 2:
                note_str, content_str = do_list
                note_list = [n.split(":") for n in note_str.split(" ") if n != ""]
                note_dict = {x:y for x,y in note_list}
                if note_dict["type"] == "header":
                    parsed_dict["header"] = tomlkit.loads(content_str)
                elif note_dict["type"] == "content":
                    current_str = markdown(content_str) if note_dict["format"] == "md" else content_str
                    parsed_dict["content"] = current_str
                else:
                    type_dict = parsed_dict.get(note_dict["type"],dict())
                    stored_str = type_dict.get(note_dict["title"],str())
                    combined_str = stored_str + content_str
                    simple_str = self.oneline(combined_str)
                    type_dict[note_dict["title"]] = simple_str
                    parsed_dict[note_dict["type"]] = type_dict
            else:
                print(F"WARN: {do_list}")
        return parsed_dict

    def load(self) -> None:
        target_list = list()
        for folder_str in ["include_files","layout_files","page_files"]:
            target_list.extend(sorted(list(Path(folder_str).glob('*.*ml'))))
        for target_path in target_list:
            target_dict = self.parse(open(target_path).read())
            for type_str in ["include","layout","format"]:
                if type_str in target_dict.keys():
                    self.structure.update({F"{type_str}_{x}":y for x,y in target_dict[type_str].items()})

    def export(self):
        Path("mid_files").mkdir(exist_ok=True)
        with open("mid_files/structure.toml","w") as toml_handle:
            tomlkit.dump(self.structure,toml_handle)

    def oneline(self,input_str:str) -> str:
        return input_str.replace("\n","").replace("    ","")
