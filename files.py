#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对文件的操作组件
=======================
说明：
    该组件提供了对文件的基本操作，包括读取、写入、追加等。
    工作状态: Done
"""
import os


def _catch(func: callable) -> callable:
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
            return True
        except Exception as e:
            raise e
    return wrapper


class FileChanger:
    def __init__(self, file: str):
        self.file = file
        if not os.path.exists(self.file):
            with open(self.file, 'w', encoding='utf-8') as f:
                f.write('')
    
    def read(self) -> str:
        with open(self.file, 'r', encoding='utf-8') as f:
            return f.read()
    
    @_catch
    def append(self, s: str) -> bool:
        with open(self.file, 'a', encoding='utf-8') as f:
            f.write(s)
    
    @_catch
    def rewrite(self, s: str) -> bool:
        with open(self.file, 'w', encoding='utf-8') as f:
            f.write(s)
    
    @_catch
    def delete(self) -> bool:
        os.remove(self.file)
    
    @_catch
    def rename(self, s: str) -> bool:
        os.rename(self.file, s)
    
