# AI Command Line Interface (aicli)

一个基于Python的AI命令行助手，可以与OpenAI API交互，执行文件和命令操作。

## 功能特性

- **AI交互**：集成OpenAI API，支持对话式交互
- **命令执行**：支持执行终端命令
- **文件操作**：创建、编辑、删除、重命名文件
- **目录管理**：支持切换和查看工作目录
- **项目上下文**：自动显示项目结构和Git状态
- **安全确认**：所有操作需用户确认后执行

## 系统架构

项目包含以下核心模块：

1. `AI.py` - OpenAI API交互模块
2. `command_executor.py` - 命令执行器
3. `cwd_manager.py` - 工作目录管理器
4. `files.py` - 文件操作组件
5. `main.py` - 主程序入口
6. `parse_airtn.py` - AI响应解析器
7. `project_context.py` - 项目上下文管理器

## 安装使用

### 前置条件
- Python 3.8+
- OpenAI API密钥(设置环境变量API_KEY)

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行项目
```bash
python main.py
```

## 使用说明

1. 启动程序后，直接输入问题与AI交互
2. 使用命令前缀：
   - `/cd <path>` 切换目录
   - `/readfiles` 读取当前目录所有文件内容
   - `/<command>` 直接执行命令
3. AI输出的命令会先请求确认再执行

## 贡献指南

欢迎提交Pull Request或Issue报告问题。

## 许可证

MIT License