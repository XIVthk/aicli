# AI Command Line Interface (aicli)

一个功能强大的AI命令行助手，基于Python和OpenAI API构建。

## 功能特性

- **AI交互**：集成OpenAI API，支持对话式交互
- **命令执行**：支持执行终端命令
- **文件操作**：创建、编辑、删除、重命名文件
- **目录管理**：支持切换和查看工作目录
- **项目上下文**：自动显示项目结构和Git状态
- **安全确认**：所有操作需用户确认后执行

## 安装指南

### 前置条件
- Python 3.8+
- OpenAI API密钥(设置环境变量API_KEY)

### 安装步骤
1. 克隆仓库：
```bash
git clone https://github.com/XIVthk/aicli.git
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 设置API密钥：
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

### 示例交互

#### 示例1：查看文件内容
```
ASK C:/project>>> 请显示main.py的内容
```
AI会自动读取并显示文件内容

#### 示例2：创建新文件
```
ASK C:/project>>> 请创建一个test.py文件，内容为打印"Hello World"
```
AI会创建文件并请求确认

#### 示例3：执行命令
```
ASK C:/project>>> /ls-la
```
直接执行ls命令并显示结果

#### 示例4：切换目录
```
ASK C:/project>>> /cd ../new_directory
```
切换到新目录并更新上下文

#### 示例5：Git操作
```
ASK C:/project>>> /git add .
ASK C:/project>>> /git commit -m "Update project files"
```
直接执行Git命令

### 高级功能

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
- `AI.py` - OpenAI API交互模块
- `command_executor.py` - 命令执行模块
- `cwd_manager.py` - 工作目录管理
- `files.py` - 文件操作组件
- `main.py` - 主程序入口
- `parse_airtn.py` - AI响应解析器
- `project_context.py` - 项目上下文组件

### 测试
运行测试：
```bash
python -m pytest
```

## 常见问题

1. **API密钥无效**
   - 确保已设置API_KEY环境变量
   - 确保密钥有足够额度

2. **命令执行失败**
   - 检查命令拼写
   - 确保有足够权限

3. **文件操作失败**
   - 检查文件路径是否正确
   - 确保文件未被占用

## 贡献
欢迎提交Pull Request或Issue

## 许可证
MIT License