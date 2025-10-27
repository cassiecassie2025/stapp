# API 配置说明

本系统同时支持 **OpenAI** 和 **DeepSeek** 两种 AI 服务提供商。

## 🎯 推荐方式：界面配置（无需修改代码）

### 启动应用

```bash
streamlit run app.py
```

### 在界面配置

1. **打开左侧边栏**，找到 "⚙️ AI配置"
2. **选择API提供商**：
   - 选择 `OpenAI` 或 `DeepSeek`
3. **输入API Key**：
   - OpenAI: 输入以 `sk-proj-` 或 `sk-` 开头的Key
   - DeepSeek: 输入以 `sk-` 开头的Key
4. **选择模型**（仅OpenAI需要）：
   - 推荐 `gpt-4o-mini`（性价比高）
   - 其他选项：`gpt-4o`, `gpt-4`, `gpt-3.5-turbo`
5. **等待加载**：系统会自动加载数据并初始化

---

## 📝 方式2：环境变量配置

如果你希望永久保存配置，可以使用 `.env` 文件：

### OpenAI 配置

创建 `.env` 文件：

```bash
# OpenAI配置
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT=30
OPENAI_MAX_RETRIES=3
```

### DeepSeek 配置

创建 `.env` 文件：

```bash
# DeepSeek配置
DEEPSEEK_API_KEY=sk-your-deepseek-key-here
OPENAI_MODEL=deepseek-chat
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_TIMEOUT=30
OPENAI_MAX_RETRIES=3
```

### 同时配置两个（可在界面切换）

```bash
# 同时配置OpenAI和DeepSeek
OPENAI_API_KEY=sk-your-openai-key-here
DEEPSEEK_API_KEY=sk-your-deepseek-key-here

# 启动后在界面选择使用哪个
```

---

## 🔑 如何获取 API Key

### OpenAI

1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 注册/登录账号
3. 进入 [API Keys](https://platform.openai.com/api-keys) 页面
4. 点击 "Create new secret key"
5. 复制 Key（以 `sk-` 开头）

### DeepSeek

1. 访问 [DeepSeek 开放平台](https://platform.deepseek.com/)
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的 API Key
5. 复制 Key（以 `sk-` 开头）

---

## 💰 费用对比

| 提供商 | 模型 | 价格（输入） | 价格（输出） | 特点 |
|--------|------|-------------|-------------|------|
| OpenAI | gpt-4o-mini | $0.15/1M tokens | $0.60/1M tokens | 速度快，性价比高 |
| OpenAI | gpt-4o | $5/1M tokens | $15/1M tokens | 能力强，成本较高 |
| DeepSeek | deepseek-chat | ¥1/1M tokens | ¥2/1M tokens | **极高性价比，推荐** |

> 💡 **推荐**：如果追求性价比，使用 DeepSeek；如果追求速度和稳定性，使用 OpenAI gpt-4o-mini

---

## ⚡ 快速测试

### 测试 OpenAI

```bash
# 创建 .env
echo "OPENAI_API_KEY=sk-your-key" > .env

# 启动应用
streamlit run app.py

# 在界面选择 OpenAI，输入Key
```

### 测试 DeepSeek

```bash
# 创建 .env
echo "DEEPSEEK_API_KEY=sk-your-key" > .env

# 启动应用
streamlit run app.py

# 在界面选择 DeepSeek，输入Key
```

---

## 🔧 常见问题

### Q: 提示 "No module named 'openai'"
```bash
pip install openai==1.10.0
```

### Q: DeepSeek API 调用失败
- 检查 API Key 是否正确
- 确认账户余额是否充足
- 检查网络连接

### Q: 想切换API提供商
- 直接在界面左侧边栏切换即可
- 无需重启应用

### Q: 如何查看实际使用的配置
- 启动应用后，在终端会显示：
  ```
  AI引擎初始化完成 - 模型: gpt-4o-mini, Base URL: OpenAI默认
  ```
  或
  ```
  AI引擎初始化完成 - 模型: deepseek-chat, Base URL: https://api.deepseek.com/v1
  ```

---

## 🎉 开始使用

```bash
# 1. 启动应用
streamlit run app.py

# 2. 在界面选择API提供商并输入Key

# 3. 开始体验智能运营闭环！
```

**推荐使用 DeepSeek，性价比极高！** 🚀
