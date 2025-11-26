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
- 更改文件 %%edit <file>
- 删除文件 %%delete <file>  (使用%%run del)
- 新增文件 %%create <file>
- 新增目录 %%new_dir <dir>  (使用%%run mkdir)
- 重命名文件 %%rename <file> <new_name>  (使用%%run mv)
- 每个标记必须单独一行
- 文件内容从标记的下一行开始，到下一个标记或回复结束
- 任何文件路径都必须是绝对路径，禁用相对路径 (除了%%run dir)
- 在非必要情况下，尽量使用%%run <command>而非其他对文件操作 (除了%%edit和%%create)
- 所有文件路径的分隔符都需要使用反斜杠
- 你给出的所有命令都会在用户处请求同意，若用户不同意执行命令，你将会收到SYSTEM的提示，反之，你不会收到提示
- 给用户建议运行命令时，不需要使用%%run标记

**文件内容规则：**
- 在使用了%%edit或%%create后，若要输入文件内容，必须另起一行，用[file_start language]开始，[file_end]结束
- 不必转义任何内容

**示例：**
用户：请你帮我写一个hello world程序
AI：好的，我将为您创建一个Python的hello world程序。
%%create hello.py
[file_start python]
print("Hello, World!")
[file_end]

**命令说明规则：**
- 在解释性文字中描述命令时，不要使用%%run前缀
- 只有在你实际需要执行的时候才使用%%run标记

**正确示例：**
你可以使用以下命令运行程序：
python main.py

**错误示例：**
你可以使用以下命令运行程序：
%%run python main.py


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
        self.rules = {
            "command": False
        }
        self.asks = {}
        self.change_files = {}
    
    def question(self):
        self.console.print(f"[bold blue]ASK {self.whereami}>>> [/bold blue]", end="")
        ques = self.console.input()
        if not ques.strip(): return
        if not ques.startswith("/") and not self.rules["command"]:
            self.ques = self.after_question + ques
            self.ask()
        else:
            ques = ques[1:] if (not self.rules["command"]) else ques
            if ques.startswith("cd"):
                self.cwd_manager.parse_cd(ques)
                if self.cwd_manager.err:
                    self.console.print(f"[bold red][-] {self.cwd_manager.err}[/bold red]")
                    return
                self.whereami = self.cwd_manager.whereami
                return
            elif ques == "readfiles":
                for file in os.listdir(self.whereami):
                    if os.path.isdir(file):
                        continue
                    self.ai._add_history("system", "FILE " + file + "\n" + FileChanger(file).read())
                    self.console.print(f"[bold green][+] FILE {file} added.[/bold green]")
                return
            elif ques.startswith("readfile"):
                try:
                    temp, file = ques.split(" ") 
                except Exception as e:
                    self.console.print(f"[bold red][-] Wrong syntax: {ques.strip()}[/bold red]")
                    self.console.print(f"[bold yellow][*] Usage: /readfile <file>[/bold yellow]")
                    return
                if not os.path.isfile(file):
                    self.console.print(f"[bold red][-] File not found: {file}[/bold red]")
                    return
                self.ai._add_history("system", "FILE " + file + "\n" + FileChanger(file).read())
                self.console.print(f"[bold green][+] FILE {file} added.[/bold green]")
                return
            elif ques == "clearfiles":
                self.ai._clear_history_withstartswith(startswith="FILE ")
                self.console.print("[bold green][+] All files cleared.[/bold green]")
                return
            elif ques in ["cls", "clear", "clearscreen"]:
                self.console.clear()
                return
            elif ques == "exit":
                self.console.print("[bold yellow][*] Exiting...[/bold yellow]")
                time.sleep(1)
                exit(0)
            elif ques.startswith("rule"):
                try:
                    temp, rule, value = ques.split(" ") 
                except Exception as e:
                    self.console.print(f"[bold red][-] Wrong syntax: {ques.strip()}[/bold red]")
                    self.console.print(f"[bold yellow][*] Usage: /rule <rulename> <true|false>[/bold yellow]")
                    return
                if rule not in self.rules:
                    self.console.print(f"[bold red][-] Unknown rule: {rule}[/bold red]")
                    self.console.print(f"[bold yellow][*] Available rules: {', '.join(self.rules.keys())}[/bold yellow]")
                    return
                if value.strip().lower() not in ["true", "1", "false", "0"]:
                    self.console.print(f"[bold red][-] Wrong value: {value.strip()}[/bold red]")
                    self.console.print(f"[bold yellow][*] Usage: /rule <rulename> <true|false>[/bold yellow]")
                    return
                self.rules[rule] = value.strip().lower() in ["true", "1"]
                self.console.print(f"[bold green][+] Rule {rule} set to {self.rules[rule]}[/bold green]")
                return
            result = self.command_executor.execute(ques[1:], cwd=self.whereami)
            if result.returncode == 0:
                self.console.print("[bold green][+][/bold green] " + result.stdout if result.stdout else "[bold green][+] Done[/bold green]")
            else:
                self.console.print(f"[bold red][-] {result.stderr}[/bold red]")
    
    def ask(self):
        self.response = parse_ai_response(self.ai.ask(self.ques))
        self.submit_op_prep()
    
    def submit_op_prep(self):
        def _generate_runstr(cmd: str | list[str]) -> str:
            cmd_str = cmd if isinstance(cmd, str) else " ".join(cmd)
            run_s = f"[bold yellow] {'-' * 20} Execute? ([bold green]y[/bold green]/[bold red]n[/bold red]) {'-' * 20}\n"
            run_s += f"|  {cmd_str.ljust(len(run_s.splitlines()[0]) - 62)}|\n"
            run_s += f" {'-' * (len(run_s.splitlines()[0]) - 60)}\n"
            return run_s
        
        def _generate_filestr(filename: str, change_type: tuple[str, str | None]) -> str:
            file_s = f"[bold yellow]{'-' * 20} FileChange? ([bold green]y[/bold green]/[bold red]n[/bold red]) {'-' * 20}\n"
            file_s += f"|  {f'{change_type[0]} {filename}'.ljust(len(file_s.splitlines()[0]) - 64)}|\n"
            if change_type[0] in ["edit", "create"]:
                file_s += f"|     └── {change_type[1].ljust(len(file_s.splitlines()[0]) - 71)}|\n"
            file_s += f" {'-' * (len(file_s.splitlines()[0]) - 60)}\n"
            return file_s
        
        self.asks = {}
        self.change_files = {}

        op_counter = 0
        
        for op in self.response:
            if isinstance(op, str):
                self.console.print(op)
            elif isinstance(op, Operation):
                match op.type:
                    case "run":
                        key = f"run_{op_counter}"
                        display_str = _generate_runstr(op.command)
                        self.asks[key] = (display_str, "run", op.command)
                        op_counter += 1
                    
                    case "read":
                        self.ai._add_history("system", "FILE " + op.file + "\n" + FileChanger(op.file).read())
                    
                    case "edit":
                        relfilename = op.file.split("\\")[-1]
                        temp_filename = f"{self.whereami}\\tempfile{relfilename}"
                        with open(temp_filename, "w", encoding="utf-8") as f:
                            f.write(op.content.replace("\\`", "`"))
                        display_str = _generate_filestr(relfilename, ("edit", temp_filename))
                        self.asks[op.file] = (display_str, "file", ("edit", temp_filename))
                        self.change_files[op.file] = ("edit", temp_filename)
                    
                    case "delete":
                        relfilename = op.file.split("\\")[-1]
                        display_str = _generate_filestr(relfilename, ("delete", None))
                        self.asks[op.file] = (display_str, "file", ("delete", None))
                        self.change_files[op.file] = ("delete", None)
                    
                    case "create":
                        relfilename = op.file.split("\\")[-1]
                        temp_filename = f"{self.whereami}\\tempfile{relfilename}"
                        with open(temp_filename, "w", encoding="utf-8") as f:
                            f.write(op.content.replace("\\`", "`"))
                        display_str = _generate_filestr(relfilename, ("create", temp_filename))
                        self.asks[op.file] = (display_str, "file", ("create", temp_filename))
                        self.change_files[op.file] = ("create", temp_filename)
                    
                    case "new_dir":
                        relfilename = op.dir.split("\\")[-1]
                        display_str = _generate_filestr(relfilename, ("new_dir", op.dir))
                        self.asks[op.dir] = (display_str, "file", ("new_dir", op.dir))
                        self.change_files[op.dir] = ("new_dir", op.dir)
                    
                    case "rename":
                        relfilename = op.file.split("\\")[-1]
                        display_str = _generate_filestr(relfilename, ("rename", op.new_name))
                        self.asks[op.file] = (display_str, "file", ("rename", op.new_name))
                        self.change_files[op.file] = ("rename", op.new_name)

        self.ask_for_changes()

    def ask_for_changes(self):
        if not self.asks:
            return
        
        ask_for_all = "-" * 20 + " All Operations " + "-" * 20 + "\n"
        for key in self.asks:
            display_str, op_type, op_data = self.asks[key]
            if op_type == "run":
                if isinstance(op_data, list): cmd_display = " ".join(op_data)
                else: cmd_display = op_data
                ask_for_all += f"|  Command: {cmd_display.ljust(len(ask_for_all.splitlines()[0]) - 14)}  |\n"
            else:  # file operation
                change_type, change_data = op_data
                if change_type == "edit":
                    ask_for_all += f"|  FC: edit {key.ljust(len(ask_for_all.splitlines()[0]) - 14)}  |\n"
                elif change_type == "delete":
                    ask_for_all += f"|  FC: delete {key.ljust(len(ask_for_all.splitlines()[0]) - 7)}  |\n"
                elif change_type == "create":
                    ask_for_all += f"|  FC: create {key.ljust(len(ask_for_all.splitlines()[0]) - 7)}  |\n"
                elif change_type == "new_dir":
                    ask_for_all += f"|  FC: create directory {key.ljust(len(ask_for_all.splitlines()[0]) - 17)}  |\n"
                elif change_type == "rename":
                    ask_for_all += f"|  FC: rename {(key + "->" + change_data).ljust(len(ask_for_all.splitlines()[0]) - 7)}  |\n"
        
        ask_for_all += "-" * len(ask_for_all.splitlines()[0]) + "\n"
        self.console.print(f"[bold yellow]{ask_for_all}[/bold yellow]")
        
        self.console.print("[bold blue]DECISION (a=agree all, c=cancel all, o=one-by-one, default=a) >>> [/bold blue]", end="")
        decision = self.console.input().strip().lower()
        
        keys_to_process = list(self.asks.keys())
        
        match decision:
            case "c":
                self.console.print("[bold red][-] All operations canceled.[/bold red]")
                self.ai._add_history("system", "All operations canceled by user")
                self.asks.clear()
                for temp in self.change_files:
                    if self.change_files[temp][0] == "create" or self.change_files[temp][0] == "edit":
                        os.remove(self.change_files[temp][1])
                self.change_files.clear()
            
            case "o":
                for key in keys_to_process:
                    if key not in self.asks:
                        continue
                    
                    display_str, op_type, op_data = self.asks[key]
                    self.console.print(display_str)
                    self.console.print("[bold blue]CONFIRM (y/n/s=skip(remain files), default=y) >>> [/bold blue]", end="")
                    confirm = self.console.input().strip().lower()
                    
                    if confirm == "s":
                        self.console.print("[bold yellow][!] Operation skipped but the file remains.[/bold yellow]")
                        self.ai._add_history("system", f"Operation {key} skipped but the file remains")
                        del self.asks[key]
                        if key in self.change_files:
                            del self.change_files[key]
                    elif confirm == "n":
                        self.console.print("[bold red][-] Operation canceled.[/bold red]")
                        self.ai._add_history("system", f"Operation {key} canceled by user")
                        if op_type == "create" or op_type == "edit":
                            os.remove(self.change_files[key][1])
                        del self.asks[key]
                        if key in self.change_files:
                            del self.change_files[key]
                    else:  
                        if op_type == "run":
                            self._run_cmd(op_data)
                        else:
                            self._change_file(key, op_data)
                        del self.asks[key]
                        if key in self.change_files:
                            del self.change_files[key]

            case _:
                for key in keys_to_process:
                    if key not in self.asks:
                        continue
                    display_str, op_type, op_data = self.asks[key]
                    if op_type == "run":
                        self._run_cmd(op_data)
                    else:
                        self._change_file(key, op_data)
                    del self.asks[key]
                    if key in self.change_files:
                        del self.change_files[key]

    def _run_cmd(self, cmd: str | list[str]):
        result = self.command_executor.execute(cmd, cwd=self.whereami)
        if result.returncode == 0:
            output = result.stdout if result.stdout else "Done"
            self.console.print(f"[bold green][+] {output}[/bold green]")
        else:
            self.console.print(f"[bold red][-] {result.stderr}[/bold red]")

    def _change_file(self, file: str, change_type_data: tuple[str, str | None]):
        change_type, change_data = change_type_data
        
        match change_type:
            case "edit" | "create":
                with open(change_data, "r", encoding="utf-8") as f:
                    content = f.read()
                FileChanger(file).rewrite(content)
                if os.path.exists(change_data):
                    os.remove(change_data)
            
            case "delete":
                FileChanger(file).delete()
            
            case "new_dir":
                os.makedirs(os.path.join(self.whereami, change_data), exist_ok=True)
            
            case "rename":
                FileChanger(file).rename(change_data)
    
    def update(self):
        self.ques, self.response = None, None
        self.project_viewer = ProjectContexter(self.whereami)
        self.after_question = self.project_viewer.display_project_context()
        self.change_files = {}

    def run(self, working: bool = True):
        ASCIItext = r"""
  _____                          _                              ____   _       ___ 
 |  ___|   ___    _   _   _ __  | |_    ___    ___   _ __      / ___| | |     |_ _|
 | |_     / _ \  | | | | | '__| | __|  / _ \  / _ \ | '_ \    | |     | |      | | 
 |  _|   | (_) | | |_| | | |    | |_  |  __/ |  __/ | | | |   | |___  | |___   | | 
 |_|      \___/   \__,_| |_|     \__|  \___|  \___| |_| |_|    \____| |_____| |___|
"""
        self.console.print("[bold blue]" + ASCIItext + "[/bold blue]")
        while working:
            try:
                self.question()
                self.update()
            except Exception as e:
                self.console.print(f"[bold red]<#!> Fatal Error captured: {e}[/bold red]")
                raise e

if __name__ == "__main__":
    cli = CLI()
    cli.run(True)
