#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析AI回复的函数
=======================
说明：
    没有处理%%cd这样的逻辑，而是在其他模块中，检测到 type="run", command[0] = "cd"的时候再处理
    换句话说，那不是这个模块干的活
    工作状态: Done
"""
from dataclasses import dataclass

@dataclass
class Operation:
    """
    操作类
    """
    type: str
    command: str | list[str] = None
    kwargs: dict[str, str] = None
    file: str = None
    content: str = None
    new_name: str = None
    dir: str = None

def parse_ai_response(response: str) -> list[Operation | str]:
    parts = response.split("\n")
    ops = []
    edit = False
    create = False
    in_block = False
    contents = []
    for line in parts:
        if edit or create:
            if line.startswith("```"):
                if not in_block: in_block = True; continue
                else: in_block = False
            if in_block:
                contents.append(line.replace("```", ""))
                continue
        elif line.startswith("%%"):
            _op, *args = line.split(" ")
            match _op:
                case "%%run":
                    cmd = []; kwargs = {}
                    for cmdpart in args:
                        if "=" in cmdpart:
                            key, value = cmdpart.split("=")
                            if key.startswith("["): key = key[1:]
                            if value.endswith("]"): value = value[:-1]
                            if value.endswith(","): value = value[:-1]
                            if value.isdigit(): value = int(value)
                            if value == "True": value = True
                            if value == "False": value = False
                            kwargs[key] = value
                        else: cmd.append(cmdpart)
                    ops.append(Operation(
                        type="run",
                        command=cmd,
                        kwargs=kwargs
                    ))
                    continue
                case "%%read":
                    file = args[0]
                    ops.append(Operation(
                        type="read",
                        file=file
                    ))
                    continue
                case "%%edit":
                    file = args[0]
                    edit = True
                    continue
                case "%%create":
                    file = args[0]
                    create = True
                    continue
                case "%%delete":
                    file = args[0]
                    ops.append(Operation(
                        type="delete",
                        file=file
                    ))
                    continue
                case "%%new_dir":
                    dir = args[0]
                    ops.append(Operation(
                        type="new_dir",
                        dir=dir
                    ))
                    continue
                case "%%rename":
                    file = args[0]
                    new_name = args[1]
                    ops.append(Operation(
                        type="rename",
                        file=file,
                        new_name=new_name
                    ))
                    continue
        if not in_block and (edit or create):
            if contents:
                ops.append(Operation(
                    type="edit" if edit else "create",
                    file=file,
                    content="\n".join(contents).replace("\\`", "`")
                ))
            contents = []; create, edit = False, False
            continue
        
        if not (edit or create or in_block) and line.strip():
            ops.append(line)
    return ops

if __name__ == "__main__":
    print(parse_ai_response("""
%%create hello.md
```markdown
\\`\\`\\`bash
???
\\`\\`\\`
```"""))