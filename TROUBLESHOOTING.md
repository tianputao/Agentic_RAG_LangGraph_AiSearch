# 故障排除指南 (Troubleshooting Guide)

## 常见问题及解决方案

### 1. 安装问题 (Installation Issues)

#### 问题: "Cannot import 'setuptools.build_meta'"
```bash
# 解决方案 1: 使用快速修复脚本
./quick_fix.sh

# 解决方案 2: 手动修复
rm -rf venv
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel build
pip install -r requirements.txt
```

#### 问题: pip 安装失败
```bash
# 升级 pip 和构建工具
python -m pip install --upgrade pip setuptools wheel

# 使用 --no-cache-dir 参数
pip install --no-cache-dir -r requirements.txt

# 逐个安装包
pip install streamlit python-dotenv pydantic
```

#### 问题: Python 版本不兼容
```bash
# 检查 Python 版本
python3 --version

# 需要 Python 3.9 或更高版本
# 在 Ubuntu/Debian 上安装:
sudo apt update
sudo apt install python3.9 python3.9-venv python3.9-dev

# 在 CentOS/RHEL 上安装:
sudo yum install python39 python39-venv python39-devel
```

### 2. 运行时问题 (Runtime Issues)

#### 问题: Azure 服务连接失败
```bash
# 检查 .env 文件配置
cat .env

# 确保设置了正确的环境变量:
# AZURE_OPENAI_API_KEY
# AZURE_OPENAI_ENDPOINT
# AZURE_SEARCH_API_KEY
# AZURE_SEARCH_SERVICE_NAME
```

#### 问题: Streamlit 无法启动
```bash
# 检查端口是否被占用
netstat -tulpn | grep :8501

# 使用不同端口启动
streamlit run src/app.py --server.port 8502

# 检查防火墙设置
sudo ufw allow 8501
```

#### 问题: 模块导入错误
```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 检查 Python 路径
python -c "import sys; print(sys.path)"

# 确保在项目根目录
pwd
ls -la src/
```

### 3. 性能问题 (Performance Issues)

#### 问题: 搜索响应慢
- 检查网络连接到 Azure 服务
- 减少搜索结果数量 (修改 config.py 中的 top_k)
- 启用并发搜索 (默认已启用)

#### 问题: 内存使用高
- 减少对话历史长度 (修改 config.py 中的 max_history)
- 限制文档片段大小
- 使用流式响应

### 4. Azure 配置问题 (Azure Configuration Issues)

#### 问题: Azure OpenAI 配额超限
```bash
# 检查配额使用情况
az cognitiveservices account list-usage \
  --name YOUR_OPENAI_RESOURCE_NAME \
  --resource-group YOUR_RESOURCE_GROUP
```

#### 问题: Azure Search 索引不存在
```bash
# 列出所有索引
az search index list \
  --service-name YOUR_SEARCH_SERVICE \
  --resource-group YOUR_RESOURCE_GROUP
```

#### 问题: API 密钥无效
```bash
# 获取 Azure OpenAI 密钥
az cognitiveservices account keys list \
  --name YOUR_OPENAI_RESOURCE_NAME \
  --resource-group YOUR_RESOURCE_GROUP

# 获取 Azure Search 密钥
az search admin-key show \
  --service-name YOUR_SEARCH_SERVICE \
  --resource-group YOUR_RESOURCE_GROUP
```

### 5. 开发模式 (Development Mode)

#### 使用模拟数据进行开发
```bash
# 在 .env 文件中设置
USE_MOCK=true

# 或者通过环境变量
export USE_MOCK=true
streamlit run src/app.py
```

#### 启用调试模式
```bash
# 在 .env 文件中设置
LOG_LEVEL=DEBUG

# 查看详细日志
tail -f logs/app.log
```

### 6. 测试问题 (Testing Issues)

#### 运行系统测试
```bash
# 激活虚拟环境
source venv/bin/activate

# 运行测试
python src/test_system.py

# 运行特定测试
python -m pytest src/test_system.py::test_config_creation -v
```

#### 测试 Azure 连接
```bash
# 测试 Azure OpenAI 连接
python -c "
from src.config import ConfigManager
config = ConfigManager()
print('Azure OpenAI Config:', config.azure_openai)
"

# 测试 Azure Search 连接
python -c "
from src.azure_search import AzureSearchClient
from src.config import ConfigManager
config = ConfigManager()
client = AzureSearchClient(config.azure_search)
print('Search client created successfully')
"
```

## 快速诊断脚本

```bash
#!/bin/bash
# 运行此脚本进行快速诊断

echo "=== 系统诊断 ==="

echo "1. Python 版本:"
python3 --version

echo "2. 虚拟环境状态:"
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✓ 虚拟环境已激活: $VIRTUAL_ENV"
else
    echo "✗ 虚拟环境未激活"
fi

echo "3. 关键包检查:"
python -c "import streamlit; print('✓ Streamlit')" 2>/dev/null || echo "✗ Streamlit"
python -c "import pydantic; print('✓ Pydantic')" 2>/dev/null || echo "✗ Pydantic"
python -c "import dotenv; print('✓ Python-dotenv')" 2>/dev/null || echo "✗ Python-dotenv"

echo "4. 配置文件检查:"
[ -f ".env" ] && echo "✓ .env 文件存在" || echo "✗ .env 文件不存在"
[ -f "requirements.txt" ] && echo "✓ requirements.txt 存在" || echo "✗ requirements.txt 不存在"

echo "5. 项目结构检查:"
[ -d "src" ] && echo "✓ src 目录存在" || echo "✗ src 目录不存在"
[ -f "src/app.py" ] && echo "✓ app.py 存在" || echo "✗ app.py 不存在"

echo "=== 诊断完成 ==="
```

## 联系支持

如果以上解决方案都无法解决问题，请收集以下信息：

1. 操作系统和版本
2. Python 版本
3. 错误的完整堆栈跟踪
4. .env 文件内容（隐藏敏感信息）
5. 运行 `pip list` 的输出

### 获取详细错误信息
```bash
# 启用详细日志
export LOG_LEVEL=DEBUG
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 运行应用并捕获错误
python src/app.py 2>&1 | tee error.log
```

### 重置到初始状态
```bash
# 完全重置项目
./setup.sh clean
./quick_fix.sh
```
