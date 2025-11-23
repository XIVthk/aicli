# AI Command Line Interface (aicli)

一个功能强大的AI命令行助手，基于Python和OpenAI API构建。

## 功能特性

### 核心功能
- **AI交互**：集成OpenAI API，支持对话式交互
- **命令执行**：支持执行终端命令(Powershell/Bash)
- **文件操作**：创建、编辑、删除、重命名文件
- **目录管理**：支持切换和查看工作目录
- **项目上下文**：自动显示项目结构和Git状态
- **安全确认**：所有操作需用户确认后执行

### 高级功能
- **批量操作**：支持一次性确认多个操作
- **历史回溯**：可查看和回滚历史对话
- **错误处理**：智能识别和处理API错误
- **自定义配置**：可调整AI模型和参数

## 安装指南

### 前置条件
- Python 3.8+
- OpenAI API密钥(设置环境变量API_KEY)
- Git(可选，用于版本控制)

### 安装步骤
1. 克隆仓库：
```bash
git clone https://github.com/XIVthk/aicli.git
cd aicli
```

2. 创建并激活虚拟环境(推荐)：
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 设置API密钥：
```bash
export API_KEY=your_api_key_here  # Linux/macOS
set API_KEY=your_api_key_here     # Windows
```

## 使用方法

### 启动程序
```bash
python main.py
```

### 基本交互
程序启动后会显示项目上下文信息，然后您可以：
1. 直接输入问题与AI交互
2. 输入以"/"开头的命令直接执行终端命令
3. 使用"/cd"命令切换目录

### 命令示例
#### 文件操作
```
ASK C:/project>>> 请显示main.py的内容
ASK C:/project>>> 请创建一个test.py文件，内容为打印"Hello World"
```

#### 目录操作
```
ASK C:/project>>> /cd ../new_directory
```

#### Git操作
```
ASK C:/project>>> /git status
ASK C:/project>>> /git add .
ASK C:/project>>> /git commit -m "Update files"
```

### 高级用法
1. **批量操作确认**：
   - 当AI建议多个操作时，可以选择：
     - `a`：同意所有操作
     - `c`：取消所有操作
     - `o`：逐个确认操作

2. **项目上下文**：
   - 每次交互前会自动显示：
     - 当前目录结构
     - Git状态
     - 最近更改历史

3. **安全模式**：
   - 所有文件修改和命令执行都需要确认
   - 提供操作预览功能

## 开发指南

### 项目结构
| 文件 | 说明 |
|------|------|
| `AI.py` | OpenAI API交互模块 |
| `command_executor.py` | 命令执行模块 |
| `cwd_manager.py` | 工作目录管理 |
| `files.py` | 文件操作组件 |
| `main.py` | 主程序入口 |
| `parse_airtn.py` | AI响应解析器 |
| `project_context.py` | 项目上下文组件 |

### 代码规范
- 遵循PEP 8风格指南
- 使用类型注解(Type Hints)
- 重要函数添加docstring
- 使用try-except处理潜在错误

### 扩展功能
1. 添加新的命令解析器：
   - 修改`parse_airtn.py`
   - 添加新的`Operation`类型

2. 集成新的AI服务：
   - 修改`AI.py`
   - 实现新的API接口

3. 增强安全功能：
   - 在`command_executor.py`中添加命令白名单
   - 实现更细粒度的权限控制

## 常见问题

### API相关问题
Q: API密钥无效怎么办？
A: 请检查：
1. 是否正确设置API_KEY环境变量
2. 密钥是否有足够额度
3. API服务是否可用

### 运行问题
Q: 命令执行失败？
A: 请检查：
1. 命令拼写是否正确
2. 是否有足够权限
3. 所需程序是否已安装

### 文件问题
Q: 文件操作失败？
A: 请检查：
1. 文件路径是否正确
2. 文件是否被其他程序占用
3. 是否有写入权限

## 贡献指南
1. Fork项目仓库
2. 创建特性分支(`git checkout -b feature/your-feature`)
3. 提交更改(`git commit -am 'Add some feature'`)
4. 推送到分支(`git push origin feature/your-feature`)
5. 创建Pull Request

## 许可证
MIT License

Copyright (c) 2024 XIVthk

Permission is hereby granted...