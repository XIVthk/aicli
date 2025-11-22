#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
当前工作目录管理模块
=======================
说明：
    当AI输出命令时，会在command_executor.py中调用命令，而cwd_manager.py就是管理工作目录的
    因为切换工作目录一般使用 cd 命令，所以在此处做了 cd 命令的解析，且只做了 cd 的解析，其他命令解析应交给command_executor或别的模块
    工作状态: Done
"""
import os
from pathlib import Path
import re
import platform


class Manager:
    def __init__(self, whereami: str | Path = os.getcwd()):
        self.whereami = whereami
        self.new_whereami = None
        self.err = None
    
    def parse_cd(self, cmd: str | list[str]):
        """
        解析 cd 命令
        """
        if not isinstance(cmd, (str, list)):
            raise TypeError("Expected str or list, got", type(cmd))
        if cmd == "cd ..": cmd = "cd.."
        if not re.match(r"^cd(?:\s+.*|$)", cmd) and cmd != "cd..":
            raise ValueError("Expected cd command, got", cmd)
        
        if re.match(r"^cd(?:\s+.*|$)", cmd):
            cd, *parts = cmd.split(" ")
            parts = [part.strip().replace("~", os.path.expanduser("~")) for part in parts]
            if Path(os.path.join(self.whereami, *parts)).exists():
                self.new_whereami = os.path.join(self.whereami, *parts)
            else:
                self.err = f"cd: {os.path.join(self.whereami, *parts)}: No such file or directory"
                return
        
        elif cmd == "cd..":
            if platform.system().lower() == "windows":
                if re.match(r"^\s*[a-zA-Z]:\\\s*$", self.whereami.strip(), re.IGNORECASE):
                    self.err = "cd: ..: No such file or directory"
                    return
                else:
                    self.new_whereami = os.path.dirname(self.whereami)
            else:
                if self.whereami == os.path.abspath(os.sep):
                    self.err = "cd: ..: No such file or directory"
                    return
                else:
                    self.new_whereami = os.path.dirname(self.whereami)
        elif cmd == "cd":
            self.new_whereami = self.whereami
        
        self.update()
    
    def update(self):
        self.whereami = self.new_whereami
        self.new_whereami = None
        self.err = None

    def __str__(self):
        return self.whereami
