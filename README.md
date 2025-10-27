# 会员智能运营闭环 Demo

## 项目简介

这是一个基于AI的会员运营智能闭环系统Demo，展示AI如何将会员运营从「拍脑袋决策」变成「数据+智能驱动」。

### 核心场景

1. **异常响应** 🔍: AI自动分析边现下降原因并给出行动建议（10秒内）
2. **策略制定** 💡: AI推荐完整运营策略（人群+内容+资源位+优惠+KPI预测）
3. **复盘总结** 📊: AI自动生成复盘报告 + 策略执行模板（15秒内，可直接复用）⭐NEW

## 快速启动

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑.env文件，填入你的OpenAI API Key
```

或者直接在`.env`文件中添加：
```
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. 生成模拟数据

```bash
cd /Users/chocho/Downloads/IOP
python scripts/generate_data.py
```

输出：
```
✅ 生成日报数据: 30 行
✅ 生成用户分层: 6 行
✅ 生成历史活动: 6 行
✅ 生成资源位容量: 3 行
🎉 所有数据生成完成！
```

### 4. 运行应用

```bash
streamlit run app.py
```

浏览器会自动打开 http://localhost:8501

## 功能模块

### 页面1: 🎯 目标规划
- 设定运营目标（指标/提升幅度/人群/周期）
- AI可行性分析
- 边现趋势预测图表
- 目标拆解树

### 页面2: 👥 人群策略（核心）
- AI智能策略推荐
  - 目标人群圈选
  - 内容策略配比
  - 资源位配置
  - 优惠方案
  - KPI预测（边现提升/置信度/ROI）
- 预算模拟器（实时调整参数）
- 下载执行模板

### 页面3: 📈 实时监控（核心）
- AI异常预警卡片
- 多指标监控面板（DAU/收入/边现/转化率）
- 智能异常检测（剔除日历效应）
- AI异常解释（核心原因/数据洞察/行动建议）
- 下载行动清单

### 页面4: 🧠 AI复盘（已增强）⭐NEW
- 选择复盘周期
- AI自动生成复盘报告（三个tab展示）
  - **📊 完整报告**: 活动总结 + 执行模板 + 优化建议 + 策略沉淀
  - **🎯 执行模板**: 可直接复用的策略模板（人群/内容/资源位/优惠/KPI/行动清单）
  - **📈 数据可视化**: ROI排行 + 趋势图 + 详细数据表
- 双下载功能
  - 下载完整复盘报告
  - 下载执行模板（精简版）

### 页面5: 📚 经验库（核心）
- RAG检索相似活动（BM25算法）
- 展示相似案例（ROI/边现提升/相似度）
- AI复用建议
- 一键下载复用模板
- 知识库统计

## 技术栈

- **Web框架**: Streamlit 1.31.0
- **AI引擎**: OpenAI GPT-4o-mini
- **数据处理**: Pandas 2.1.4, Numpy 1.26.3
- **可视化**: Plotly 5.18.0
- **RAG检索**: BM25 (rank-bm25 + jieba分词)
- **数据校验**: Pydantic 2.5.0
- **日志**: Loguru 0.7.2

## 项目结构

```
IOP/
├── app.py                          # Streamlit主程序
├── requirements.txt                # 依赖包
├── .env.example                    # 环境变量模板
├── README.md                       # 本文件
│
├── pages/                          # 5个功能页面
│   ├── 01_🎯_目标规划.py
│   ├── 02_👥_人群策略.py
│   ├── 03_📈_实时监控.py
│   ├── 04_🧠_AI复盘.py
│   └── 05_📚_经验库.py
│
├── modules/                        # 核心模块
│   ├── ai_engine.py                # AI引擎（策略推荐/异常解释/复盘报告）
│   ├── data_loader.py              # 数据加载
│   ├── charts.py                   # Plotly图表生成
│   ├── rag_search.py               # BM25检索
│   ├── anomaly_detector.py         # 异常检测
│   └── budget_simulator.py         # 预算模拟
│
├── utils/                          # 工具模块
│   ├── config.py                   # 配置管理
│   └── validators.py               # Pydantic数据模型
│
├── data/                           # 数据文件（生成后）
│   ├── daily_metrics.csv           # 日报数据（30天）
│   ├── user_segments.csv           # 用户分层（6个）
│   ├── campaign_history.csv        # 历史活动（6个）
│   └── resource_capacity.csv       # 资源位容量（3个）
│
└── scripts/                        # 脚本
    └── generate_data.py            # 数据生成脚本
```

## 核心功能特性

### 1. AI容错机制（三层防护）
- **L1**: Pydantic模型校验
- **L2**: 智能JSON提取（支持代码块）
- **L3**: 降级兜底（默认策略模板）

### 2. 异常检测算法
- 剔除日历效应（周末/节假日归一化）
- 滚动窗口动态阈值（7日MA±1.5σ）
- 多维度交叉验证（避免DAU突增误判）
- 异常分级（轻微/中度/严重）

### 3. RAG经验检索
- 中文分词（jieba）
- BM25相似度算法
- 自动归一化评分

## 演示流程（5分钟）

1. **目标规划** (30秒): 设定"提升家庭向收入15%"
2. **策略推荐** (90秒): AI推荐人群+内容+资源位+KPI
3. **异常监控** (60秒): 查看异常点 → AI解释原因
4. **自动复盘** (30秒): 生成活动报告
5. **经验召回** (45秒): RAG检索相似活动

## 常见问题

### Q: 如何获取OpenAI API Key？
A: 访问 [OpenAI Platform](https://platform.openai.com/) 注册并创建API Key

### Q: 数据从哪里来？
A: 运行 `python scripts/generate_data.py` 生成模拟数据

### Q: AI调用失败怎么办？
A: 系统内置降级机制，会自动返回默认策略模板

### Q: 如何修改异常检测阈值？
A: 在 `utils/config.py` 中修改 `ANOMALY_THRESHOLD`

## 后续升级

### V1.5（1周内）
- 接入StarRocks实时数据
- 增加A/B测试模拟器

### V2.0（1个月内）
- AI Agent自主决策
- 实时预警推送（钉钉/企微）
- 多维度归因分析

### V3.0（3个月内）
- 强化学习策略优化
- 因果推断模型
- 跨平台联合运营

## 许可证

MIT License

## 联系方式

如有问题，请提Issue或联系项目维护者

---

**🎉 开始体验AI驱动的会员运营闭环吧！**
