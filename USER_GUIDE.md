# 使用指南 (User Guide)

## 🚀 快速开始

### 1. 首次安装
```bash
# 推荐方式：使用自动化安装脚本
./setup.sh

# 如果遇到问题，使用快速修复
./quick_fix.sh
```

### 2. 诊断问题
```bash
# 运行系统诊断
./diagnose.sh

# 查看详细故障排除指南
cat TROUBLESHOOTING.md
```

### 3. 启动应用
```bash
# 激活虚拟环境
source venv/bin/activate

# 启动 Streamlit 应用
streamlit run src/app.py
```

## 📚 脚本说明

### `setup.sh` - 主安装脚本
功能完整的自动化安装和配置脚本。

```bash
# 完整安装
./setup.sh

# 仅安装依赖
./setup.sh install

# 仅运行测试
./setup.sh test

# 验证环境
./setup.sh validate

# 清理环境
./setup.sh clean

# 修复常见问题
./setup.sh fix

# 查看帮助
./setup.sh help
```

### `quick_fix.sh` - 快速修复脚本
专门用于解决常见的安装和配置问题。

```bash
# 运行快速修复
./quick_fix.sh
```

**解决的问题:**
- setuptools.build_meta 导入错误
- pip 安装失败
- 虚拟环境问题
- 依赖冲突

### `diagnose.sh` - 系统诊断脚本
检测系统状态和潜在问题。

```bash
# 运行完整诊断
./diagnose.sh
```

**检查项目:**
- Python 版本兼容性
- 项目结构完整性
- 依赖安装状态
- 配置文件检查
- 网络端口状态
- 基本功能测试

## 🔧 配置指南

### 环境变量设置

创建 `.env` 文件：

```bash
# Azure OpenAI 配置
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# Azure AI Search 配置
AZURE_SEARCH_SERVICE_NAME=your_search_service_name_here
AZURE_SEARCH_API_KEY=your_search_api_key_here
AZURE_SEARCH_INDEX_NAME=your_index_name_here

# 应用配置
USE_MOCK=false  # 设置为 true 使用模拟数据进行开发
LOG_LEVEL=INFO
```

### 开发模式
在没有 Azure 服务的情况下进行开发：

```bash
# 在 .env 中设置
USE_MOCK=true

# 或通过环境变量
export USE_MOCK=true
streamlit run src/app.py
```

## 🧪 测试指南

### 运行系统测试
```bash
# 激活虚拟环境
source venv/bin/activate

# 运行完整测试套件
python src/test_system.py

# 使用 pytest（如果安装）
pytest src/test_system.py -v
```

### 测试特定功能
```bash
# 测试配置管理
python -c "import sys; sys.path.insert(0, 'src'); from config import ConfigManager; print('配置测试:', ConfigManager())"

# 测试 Azure Search 客户端
python -c "import sys; sys.path.insert(0, 'src'); from azure_search import AzureSearchClient; print('搜索测试: OK')"

# 测试 RAG 代理
python -c "import sys; sys.path.insert(0, 'src'); from rag_agent import AgenticRAGAgent; print('代理测试: OK')"
```

## 🚀 部署指南

### 本地部署
```bash
# 生产模式运行
streamlit run src/app.py --server.port 8501 --server.address 0.0.0.0
```

### Docker 部署
```bash
# 构建镜像
docker build -t agentic-rag .

# 运行容器
docker run -p 8501:8501 --env-file .env agentic-rag
```

### Azure 部署
参考 `DEPLOYMENT.md` 文件获取详细的 Azure 部署指南。

## 🛠️ 常用命令

### 环境管理
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 停用虚拟环境
deactivate

# 更新依赖
pip install --upgrade -r requirements.txt
```

### 应用管理
```bash
# 启动应用（默认端口 8501）
streamlit run src/app.py

# 使用自定义端口
streamlit run src/app.py --server.port 8080

# 允许外部访问
streamlit run src/app.py --server.address 0.0.0.0

# 调试模式
LOG_LEVEL=DEBUG streamlit run src/app.py
```

### 日志和监控
```bash
# 查看应用日志
tail -f logs/app.log

# 监控系统资源
htop  # 或 top

# 检查端口使用
netstat -tulpn | grep 8501
```

## 🔍 故障排除快速参考

### 安装问题
```bash
# setuptools 错误
./quick_fix.sh

# 依赖冲突
pip install --force-reinstall -r requirements.txt

# 权限问题
sudo chown -R $USER:$USER venv/
```

### 运行时问题
```bash
# 模块导入错误
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Azure 连接问题
# 检查 .env 文件中的 API 密钥和端点

# 端口占用
# 使用不同端口或停止占用进程
```

### 性能问题
```bash
# 内存使用监控
ps aux | grep python

# 清理缓存
rm -rf __pycache__/ .pytest_cache/

# 重启应用
pkill -f streamlit
streamlit run src/app.py
```

## 📞 获取帮助

1. **查看脚本帮助**
   ```bash
   ./setup.sh help
   ./diagnose.sh  # 自动诊断
   ```

2. **查看详细文档**
   ```bash
   cat TROUBLESHOOTING.md  # 故障排除
   cat DEPLOYMENT.md       # 部署指南
   cat PROJECT_SUMMARY.md  # 项目概述
   ```

3. **运行诊断**
   ```bash
   ./diagnose.sh  # 系统健康检查
   python src/test_system.py  # 功能测试
   ```

4. **重置环境**
   ```bash
   ./setup.sh clean
   ./quick_fix.sh
   ```

## 💡 最佳实践

1. **开发环境**
   - 始终使用虚拟环境
   - 定期运行 `./diagnose.sh` 检查系统状态
   - 使用 `USE_MOCK=true` 进行本地开发

2. **生产环境**
   - 确保所有 Azure 服务配置正确
   - 定期备份 `.env` 文件
   - 监控应用日志和性能

3. **故障排除**
   - 先运行 `./diagnose.sh` 识别问题
   - 查看 `TROUBLESHOOTING.md` 获取解决方案
   - 必要时使用 `./quick_fix.sh` 重置环境
