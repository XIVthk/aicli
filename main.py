#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序入口
工作状态: Done
"""
import os, time
from rich.console import Console

from command_executor import Commandor
from cwd_manager import Manager
from AI import AI
from files import FileChanger
from project_context import ProjectContexter
from parse_airtn import parse_ai_response, Operation

api_key = os.environ.get("API_KEY")
if not api_key:
    raise ValueError("API_KEY环境变量未设置")

base_url="https://api.siliconflow.cn/v1"

console = Console()

command_executor = Commandor()
cwd_manager = Manager()

system_prompt = """
你是一个AI编程助手，专门帮助用户在命令行中完成编程任务。
用户会给你项目上下文和具体请求，你需要提供可执行的计划。

请使用以下标记格式来组织你的回复：

**标记规则：**
- 执行终端(Powershell/Bash)命令 %%run <command> [**kwargs, e.g. check=False, capture_output=True, text=True]
- 读取文件 %%read <file> ，这会在用户的下一次问题前将文件内容插入对话。
- 更改文件 %%edit <file>  (使用%%run echo)
- 删除文件 %%delete <file>  (使用%%run del)
- 新增文件 %%create <file>
- 新增目录 %%new_dir <dir>  (使用%%run mkdir)
- 重命名文件 %%rename <file> <new_name>  (使用%%run mv)
- 每个标记必须单独一行
- 文件内容从标记的下一行开始，到下一个标记或回复结束
- 使用edit或create后，若要输入，必须另起一行并把输入内容用反引号包裹
- 任何文件路径都必须是绝对路径，禁用相对路径
- 在非必要情况下，尽量使用%%run <command>而非其他对文件操作
- 所有文件路径的分隔符都需要使用反斜杠
- 你给出的所有命令都会在用户处请求同意，若用户不同意执行命令，你将会收到SYSTEM的提示，反之，你不会收到提示
- 给出的所有文件中，若含有```markdown标记，则需要用\转义，即\\`\\`\\`

**示例：**

用户：请你帮我重命名文件main.py为main2.py
AI：好的，我将为您更改文件名字。
%%run mv main.py main2.py

用户：请你帮我写一个hello world程序
AI：好的，我将为您创建一个Python的hello world程序。
%%create hello.py
```python
print("Hello, World!")
```

用户：请运行测试
AI：我将运行测试命令。
%%run python -m pytest [check=True, capture_output=True, text=True]

用户：请看一遍这些代码。
AI：%%read code.py
SYSTEM：[CODES]
用户：请总结一下这个代码文件。
AI：这个代码文件……

用户：请你帮我创建一个test.txt文件。
AI：%%create test.txt
我已经帮您创建了test.txt文件。

请确保你的回复清晰且遵循这个格式，可以添加额外的解释文字。
"""
ai = AI(system_prompt, api_key, base_url, max_tokens=2048)

class CLI:
    def __init__(self):
        self.command_executor = command_executor
        self.cwd_manager = cwd_manager
        self.ai = ai
        self.console = console
        self.whereami = self.cwd_manager.whereami
        self.project_viewer = ProjectContexter(self.whereami)
        self.ques, self.response = None, None
        self.after_question = self.project_viewer.display_project_context()
        self.run_s, self.file_s = "", ""
        self.run_command, self.change_files = [], {}
    
    def question(self):
        self.console.print(f"[bold blue]ASK {self.whereami}>>> [/bold blue]", end="")
        ques = self.console.input()
        if not ques.strip(): return
        if not ques.startswith("/"):
            self.ques = self.after_question + ques
            self.ask()
        else:
            if ques.startswith("/cd"):
                self.cwd_manager.parse_cd(ques[1:])
                if self.cwd_manager.err:
                    self.console.print(f"[bold red][-] {self.cwd_manager.err}[/bold red]")
                    return
                self.whereami = self.cwd_manager.whereami
                return
            if ques == "/readfiles":
                for file in os.listdir(self.whereami):
                    if os.path.isdir(file):
                        continue
                    self.ai._add_history("system", "FILE " + file + "\n" + FileChanger(file).read())
                return
            result = self.command_executor.execute(ques[1:], cwd=self.whereami)
            if result.returncode == 0:
                self.console.print("[bold green][+][/bold green] " + result.stdout if result.stdout else "[bold green][+] Done[/bold green]")
            else:
                self.console.print(f"[bold red][-] {result.stderr}[/bold red]")
    
    def ask(self):
        self.console.print("[grey]AI thinking[/grey]", end="")
        self.thinking_dots()
        self.response = parse_ai_response(self.ai.ask(self.ques))
        self.submit_op_prep()
    
    def thinking_dots(self):
        for _ in range(3):
            self.console.print(".", end="")
            time.sleep(0.5)

    def submit_op_prep(self):
        self.run_command = []
        self.change_files = {}
        for op in self.response:
            if isinstance(op, str):
                self.console.print(op)
            elif isinstance(op, Operation):
                match op.type:
                    case "run":
                        self.run_command.append(op.command)
                    case "read":
                        self.ai._add_history("system", "FILE " + op.file + "\n" + FileChanger(op.file).read())
                    case "edit":
                        relfilename = op.file.split("\\")[-1]
                        with open((filename := f"{self.whereami}/tempfile{relfilename}"), "w", encoding="utf-8") as f:
                            f.write(op.content)
                        self.change_files[op.file] = ("edit", filename)
                    case "delete":
                        self.change_files[op.file] = ("delete", None)
                    case "create":
                        relfilename = op.file.split("\\")[-1]
                        with open((filename := f"{self.whereami}/tempfile{relfilename}"), "w", encoding="utf-8") as f:
                            f.write(op.content)
                        self.change_files[op.file] = ("create", filename)
                    case "new_dir":
                        self.change_files[op.dir] = ("new_dir", op.dir)
                    case "rename":
                        self.change_files[op.file] = ("rename", op.new_name)


        run_s = f"[bold yellow] {"-" * 20} Execute? ([bold green]y[/bold green]/[bold red]n[/bold red]) {"-" * 20}\n"
        for cmd in self.run_command:
            run_s += f"|  {" ".join(cmd).ljust(len(run_s.splitlines()[0]) - 62)}|\n"
        run_s += f" {"-" * (len(run_s.splitlines()[0]) - 60)}\n"
               
        file_s = f"[bold yellow]{"-" * 20} FileChange? ([bold green]y[/bold green]/[bold red]n[/bold red]) {"-" * 20}\n"
        for file, change_type in self.change_files.items():
            file_s += f"|  {f'{change_type[0]} {file}'.ljust(len(file_s.splitlines()[0]) - 64)}|\n"
            if change_type[0] == "edit" or change_type[0] == "create":
                file_s += f"|     └── {f"{change_type[1]}".ljust(len(file_s.splitlines()[0]) - 71)}|\n"
        file_s += f" {"-" * (len(file_s.splitlines()[0]) - 60)}\n"

        self.run_s, self.file_s = run_s, file_s
        self.ask_for_changes()

    def ask_for_changes(self):
        if self.run_command:
            self.console.print(self.run_s)
            self.console.print("[bold blue]CONFIRM >>> [/bold blue]", end="")
            run_confirm = self.console.input()
            if run_confirm.lower() == "y":
                self._run_cmds()
            else:
                self.console.print("[bold red][-] Canceled. [/bold red]")
                self.ai._add_history("system", "Command runs are canceled by user")
        if self.change_files:
            self.console.print(self.file_s)
            self.console.print("[bold blue]CONFIRM >>> [/bold blue]", end="")
            file_confirm = self.console.input()
            if file_confirm.lower() == "y":
                self._change_files()
            else:
                self.console.print("[bold red][-] Canceled. [/bold red]")
                self.ai._add_history("system", "File changes are canceled by user")

    def _run_cmds(self):
        for cmd in self.run_command:
            result = self.command_executor.execute(cmd)
            if result.returncode == 0:
                self.console.print("[bold green][+][/bold green] " + result.stdout if result.stdout else "[bold green][+] Done[/bold green]")
            else:
                self.console.print(f"[bold red][-] {result.stderr}[/bold red]")
    
    def _change_files(self):
        for file, change_type in self.change_files.items():
            match change_type[0]:
                case "edit":
                    with open(change_type[1], "r", encoding="utf-8") as f:
                        content = f.read()
                    FileChanger(file).rewrite(content)
                    FileChanger(change_type[1]).delete()
                case "create":
                    with open(change_type[1], "r", encoding="utf-8") as f:
                        content = f.read()
                    FileChanger(file).rewrite(content)
                    FileChanger(change_type[1]).delete()
                case "delete":
                    FileChanger(file).delete()
                case "new_dir":
                    os.mkdir(os.path.join(self.whereami, change_type[1]))
                case "rename":
                    FileChanger(file).rename(change_type[1])
    
    def update(self):
        self.ques, self.response = None, None
        self.project_viewer = ProjectContexter(self.whereami)
        self.after_question = self.project_viewer.display_project_context()
        self.run_s, self.file_s = "", ""
        self.run_command, self.change_files = [], {}

    def run(self, working: bool = True):
        while working:
            self.question()
            self.update()

if __name__ == "__main__":
    cli = CLI()
    cli.run(True)
