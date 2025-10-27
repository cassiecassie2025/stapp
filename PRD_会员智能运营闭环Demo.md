# PRD - 会员智能运营闭环 Demo

## 文档信息

| 项目名称 | 会员智能运营闭环 Demo |
|---------|---------------------|
| 产品经理 | - |
| 开发团队 | - |
| 版本号 | v1.0 |
| 创建日期 | 2025-10-27 |
| 交付周期 | 3天 |
| 文档状态 | 终稿 |

---

## 一、项目概述

### 1.1 核心场景与价值

**展示价值**：AI 如何让会员运营从「拍脑袋决策」变成「数据 + 智能驱动」

**三大核心场景**：
1. 🔍 **异常响应**
   - 老板问："为什么这周边现下降了？"
   - AI答：自动分析原因 + 给出3条行动建议（10秒内）

2. 💡 **策略制定**
   - 运营问："如何提升家庭向会员收入？"
   - AI答：推荐完整策略组合（人群+内容+资源位+优惠+KPI预测）

3. 📊 **复盘总结**
   - 复盘会："上次活动效果怎么样？"
   - AI答：自动生成Markdown复盘报告（15秒内）

### 1.2 项目背景

传统会员运营三大痛点：
- **决策慢**：制定策略需要2天开会讨论
- **响应慢**：异常发现依赖周报，无法实时响应
- **经验散**：活动经验分散在PPT中，新人难以复用

### 1.3 项目目标

通过AI+数据驱动，打造会员运营智能闭环系统，实现：
- 策略制定从2天缩短至5分钟
- 异常响应从周报级提升至实时
- 活动复盘从半天人工整理缩短至10秒生成

### 1.4 核心价值

| 场景 | 传统方式 | AI方式 | 时间节省 |
|-----|---------|--------|---------|
| 策略制定 | 2天开会讨论 | 5分钟AI推荐 | 95% ⬇️ |
| 异常响应 | 周报才发现 | 实时解释+建议 | 当日处理 |
| 活动复盘 | 半天人工整理 | 10秒生成报告 | 99% ⬇️ |

### 1.5 成功标准

**技术可验收指标**：
- ✅ 5个完整Streamlit页面
- ✅ 3个AI调用场景（策略推荐/异常解释/复盘报告）
- ✅ 1个RAG知识库（历史活动检索）
- ✅ 全流程5分钟内演示完成
- ✅ AI响应时间<10秒
- ✅ 容错率100%（AI失败有降级方案）

**业务预期效果**：
- 策略效率提升60%
- 会员边现提升15-20%
- 活动ROI提升30%
- 投资回收期：1.4个月

---

## 二、产品架构

### 2.1 技术架构

```
member_ai_demo/
├── app.py                          # 主程序（150行）
├── .env.example                    # 环境变量模板
├── requirements.txt                # 依赖包
│
├── pages/                          # 5个页面
│   ├── 01_🎯_目标规划.py          (120行)
│   ├── 02_👥_人群策略.py          (200行)
│   ├── 03_📈_实时监控.py          (180行)
│   ├── 04_🧠_AI复盘.py            (100行)
│   └── 05_📚_经验库.py            (150行)
│
├── modules/
│   ├── ai_engine.py               (350行) - 核心AI引擎
│   ├── data_loader.py             (180行) - 数据加载
│   ├── charts.py                  (250行) - 图表生成
│   ├── rag_search.py              (120行) - RAG检索
│   ├── anomaly_detector.py        (100行) - 异常检测
│   └── budget_simulator.py        (80行)  - 预算模拟
│
├── utils/
│   ├── config.py                  (60行)  - 配置管理
│   ├── logger.py                  (40行)  - 日志埋点
│   └── validators.py              (50行)  - JSON校验
│
├── data/
│   ├── daily_metrics.csv
│   ├── user_segments.csv
│   ├── campaign_history.csv
│   └── resource_capacity.csv
│
└── scripts/
    ├── generate_data.py           # 数据生成脚本
    └── build_faiss_index.py       # FAISS索引构建
```

### 2.2 数据模型

#### 2.2.1 日报指标表（daily_metrics.csv）

**字段定义**：

| 字段 | 类型 | 说明 | 示例 |
|-----|------|-----|------|
| date | date | 日期 | 2025-10-01 |
| dau | int | 日活跃用户 | 4,720,000 |
| revenue | int | 会员收入(元) | 435,000 |
| new_members | int | 新增会员数 | 21,000 |
| renew_members | int | 续费会员数 | 65,000 |
| content_type | string | 内容类型 | 家庭剧/动漫/综艺 |
| platform | string | 平台 | TV |
| resource_position | string | 资源位 | 首页位1/首页位3 |
| discount_type | string | 优惠类型 | 10元券/5折月卡 |
| is_holiday | int | 节假日标识 | 0/1 |
| day_of_week | int | 星期几 | 0-6 |

**示例数据**（前3行）：
```csv
date,dau,revenue,new_members,renew_members,content_type,platform,resource_position,discount_type
2025-10-01,4720000,435000,21000,65000,家庭剧,TV,首页位3,10元券
2025-10-02,4810000,466700,23500,63000,动漫,TV,详情页推荐,5折月卡
2025-10-03,4650000,441200,19800,61500,综艺,TV,首页位1,免费试看
```

**计算指标（Python实现）**：
```python
# 基础指标
df['arpu'] = df['revenue'] / df['dau']  # 单DAU边现
df['arpu_change'] = df['arpu'].pct_change() * 100  # 边现变化率%
df['conversion_rate'] = (df['new_members'] + df['renew_members']) / df['dau'] * 100

# 异常检测用指标
df['arpu_ma7'] = df['arpu'].rolling(window=7, min_periods=1).mean()  # 7日均线
df['arpu_std7'] = df['arpu'].rolling(window=7, min_periods=1).std()  # 7日标准差
df['arpu_zscore'] = (df['arpu'] - df['arpu_ma7']) / df['arpu_std7']  # Z-Score
```

#### 2.2.2 用户分层表（user_segments.csv）

**字段定义**：

| 字段 | 类型 | 说明 |
|-----|------|-----|
| segment | string | 用户分层标签 |
| active_level | string | 活跃度(high/medium/low) |
| membership_status | string | 会员状态 |
| size | int | 人群规模 |
| content_preference | string | 内容偏好 |
| avg_watch_time | int | 平均观看时长(分钟) |
| price_sensitivity | string | 价格敏感度 |
| historical_cvr | float | 历史转化率 |
| avg_arpu_contribution | float | 人均边现贡献 |

**示例数据**（前3行）：
```csv
segment,active_level,membership_status,size,content_preference,avg_watch_time,price_sensitivity,historical_cvr,avg_arpu_contribution
家庭向高活跃,high,non_member,860000,家庭剧,180,low,0.185,0.012
动漫偏好沉默,low,expired,230000,动漫,45,high,0.082,0.005
轻活跃用户,medium,member,450000,综艺,90,medium,0.145,0.009
```

#### 2.2.3 历史活动表（campaign_history.csv）

**字段定义**：

| 字段 | 类型 | 说明 |
|-----|------|-----|
| campaign_id | string | 活动ID |
| start_date | date | 开始日期 |
| end_date | date | 结束日期 |
| strategy_tag | string | 策略标签 |
| target_segment | string | 目标人群 |
| content_mix | string | 内容组合 |
| resource_positions | string | 资源位 |
| discount | string | 优惠方案 |
| revenue_lift | string | 收入提升(+18%) |
| arpu_lift | string | 边现提升(+0.021) |
| roi | float | ROI |
| success_factors | string | 成功因素 |
| budget_used | int | 预算使用(万元) |
| resource_capacity | string | 资源位容量配置 |

**示例数据**（前2行）：
```csv
campaign_id,start_date,end_date,strategy_tag,target_segment,content_mix,resource_positions,discount,revenue_lift,arpu_lift,roi,success_factors
2024Q4_VIP,2024-10-15,2024-10-21,家庭剧促活,家庭向高活跃,家庭剧70%+动漫30%,首页位3+详情页,10元券,+18%,+0.021,1.34,周五高峰+资源位权重高
2025_SUMMER,2025-06-01,2025-06-05,动漫限免,儿童动画家长,动漫80%+综艺20%,首页位1,免费试看,+12%,+0.015,1.12,儿童节热点+内容匹配
```

#### 2.2.4 资源位容量表（resource_capacity.csv）

| 字段 | 类型 | 说明 |
|-----|------|-----|
| resource_position | string | 资源位名称 |
| max_capacity | float | 最大容量(0-1) |
| cost_per_10k | int | 每万次成本(元) |
| elasticity | float | 弹性系数 |

---

## 三、功能需求

### 3.1 页面1：目标规划 🎯

**功能目标**：运营设定目标，系统自动拆解可行性

#### 3.1.1 核心功能

| 功能模块 | 交互方式 | AI调用 | 优先级 |
|---------|---------|--------|--------|
| 目标输入表单 | 4个选择框 | ❌ | P0 |
| AI可行性分析 | 点击按钮 | ✅ (可选) | P1 |
| 趋势预测图表 | 自动显示 | ❌ | P0 |
| 目标拆解树 | 文本展示 | ❌ | P1 |

#### 3.1.2 界面布局

```
┌─────────────────────────────────────────┐
│ 🎯 目标规划与AI预测                      │
├─────────────────────────────────────────┤
│ 📝 设定运营目标                          │
│  [指标▼] [提升%] [人群▼] [周期▼]        │
│  [🤖 AI分析目标]                        │
├─────────────────────────────────────────┤
│ 📊 可行性评估 (AI生成)                   │
│  ✓ 难度评级: ⭐⭐⭐                     │
│  ⚠️ 风险提示: ...                        │
│  💡 执行建议: ...                        │
├─────────────────────────────────────────┤
│ 📈 边现趋势图 (Plotly)                   │
│ 🌳 目标拆解树 (代码块)                   │
└─────────────────────────────────────────┘
```

#### 3.1.3 验收标准

- [ ] 4个输入框可正常选择
- [ ] 趋势图正确显示30天数据
- [ ] 拆解树以Markdown格式展示
- [ ] AI分析按钮可选（不阻塞主流程）

---

### 3.2 页面2：人群策略 👥（核心页面）

**功能目标**：AI推荐完整运营策略，支持预算模拟

#### 3.2.1 核心功能

| 功能模块 | 交互方式 | AI调用 | 优先级 |
|---------|---------|--------|--------|
| 目标描述输入 | 文本框 | ❌ | P0 |
| AI策略推荐 | 点���按钮 | ✅ | P0 |
| 预算模拟器 | 滑块调整 | ❌ | P1 |
| 策略卡片展示 | 自动展开 | ❌ | P0 |
| 一键复用模板 | 下载按钮 | ❌ | P1 |

#### 3.2.2 AI策略推荐输出

**返回JSON Schema**（Pydantic模型）：

```python
class StrategyResponse(BaseModel):
    target_segment: str              # 推荐人群
    estimated_size: str              # 人群规模
    content_strategy: dict           # 内容策略
    resource_allocation: dict        # 资源位配置
    discount_recommendation: str     # 优惠建议
    kpi_forecast: KPIForecast       # KPI预测
    risk_alert: str                 # 风险提示
    historical_reference: str       # 参考活动
```

**展示卡片**：
1. 👥 推荐人群（规模/历史转化率/选择理由）
2. 🎬 内容策略（内容配比/饼图可视化）
3. 📺 资源位策略（投放位置/时段/预算分配）
4. 💰 优惠建议（优惠类型/有效期）
5. 📊 KPI预测（边现提升/置信度/ROI）
6. ⚠️ 风险提示 + 📚 参考活动

#### 3.2.3 预算模拟器

**功能**：
- 实时调整内容配比（滑块）
- 实时调整资源位使用率（滑块）
- 实时显示预估边现/ROI/预算使用
- 资源位容量预警（>80%显示⚠️）

**计算逻辑**：
```python
# 综合效应
arpu_lift = baseline * content_effect * resource_effect * budget_effect

# 容量惩罚
if usage > capacity * 0.8:
    penalty = 0.85
```

#### 3.2.4 一键复用模板

点击"生成执行模板"下载Markdown文件，包含：
- 📋 执行清单（人群/内容/资源位/优惠/KPI/监控指标）
- 📅 行动节点（D1/D3/D5/D7）
- 👥 负责人分配

#### 3.2.5 验收标准

- [ ] 点击"AI推荐"10秒内返回结果
- [ ] 6个卡片全部正确显示
- [ ] API失败时显示默认策略模板（降级）
- [ ] 滑块拖动时实时更新预估边现
- [ ] 资源位>80%时显示容量预警
- [ ] 可下载执行模板.md文件

---

### 3.3 页面3：实时监控 📈（核心页面）

**功能目标**：实时监控指标，AI解释异常原因

#### 3.3.1 核心功能

| 功能模块 | 交互方式 | AI调用 | 优先级 |
|---------|---------|--------|--------|
| AI预警卡片区 | 首屏展示 | ❌ | P0 |
| 多指标监控面板 | 自动刷新 | ❌ | P0 |
| 智能异常检测 | 自动标注 | ❌ | P0 |
| AI异常解释 | 点击按钮 | ✅ | P0 |
| 生成行动清单 | 点击按钮 | ✅ (可选) | P1 |
| 预警规则配置 | 滑块设置 | ❌ | P1 |

#### 3.3.2 智能异常检测算法

**特性**：
- 剔除日历效应（周末/节假日自动归一化）
- 滚动窗口动态阈值（7日MA±1.5σ）
- 多维度交叉验证（避免单点误判）

**异常级别**：
- 🔴 严重：|Z-Score| > 2.5
- 🟠 中度：|Z-Score| > 2.0
- 🟡 轻微：|Z-Score| > 1.5

**实现**：
```python
# 调整后的边现（剔除节假日效应）
arpu_adjusted = arpu - (weekend_mean - workday_mean) if is_holiday else arpu

# 滚动窗口Z-Score
arpu_zscore = (arpu_adjusted - arpu_ma7) / arpu_std7

# 交叉验证
is_anomaly = (abs(arpu_zscore) > 1.5) & (abs(dau_change) < 30%)
```

#### 3.3.3 AI异常解释输出

**Markdown格式**：
```markdown
### 核心原因
1. DAU激增12%但转化仅+4%
2. 动漫CTR下降15%

### 数据洞察
...

### 行动建议
1. 延长优惠期至10天
2. 调整动漫资源位至首页位3
```

#### 3.3.4 AI行动清单输出

**Markdown任务列表**：
```markdown
## 🎯 异常处理行动清单

### 立即执行（今日内）
- [ ] 延长10元券有效期：7天→10天
- [ ] 增加首页弹窗引导

### 24小时内
- [ ] 调整动漫资源位
- [ ] 分析用户流失漏斗

### 负责人
- 执行: [@运营负责人]
```

#### 3.3.5 验收标准

- [ ] 首屏显示AI预警卡片（如有异常）
- [ ] 多指标面板显示4个图表
- [ ] 至少检测到1个异常点（红色标注）
- [ ] 点击"生成AI分析"10秒内返回
- [ ] API失败时显示数据摘要（降级）
- [ ] 可下载行动清单.md文件（可选）

---

### 3.4 页面4：AI复盘 🧠

**功能目标**：自动生成活动复盘报告

#### 3.4.1 核心功能

| 功能模块 | 交互方式 | AI调用 | 优先级 |
|---------|---------|--------|--------|
| 周期选择 | 日期选择器 | ❌ | P0 |
| AI复盘报告 | 点击生成 | ✅ | P0 |
| ROI排行榜 | 自动展示 | ❌ | P0 |
| 报告下载 | 按钮 | ❌ | P0 |
| 历史记录查看 | 表格 | ❌ | P1 |

#### 3.4.2 AI复盘报告结构

**Markdown格式**：
```markdown
## 活动总结

### 核心成果
- 会员收入 +18.5%
- 新增会员 +2.1万

### 驱动因素
- 家庭剧内容贡献最大（ROI 1.45）
- 周五晚间流量高峰抓取成功

### 待优化项
- 动漫类响应偏低（ROI 0.98）
- 详情页资源位转化不足

### 下期建议
1. 继续加大家庭剧投入
2. 优化动漫内容选品
3. 增加首页位1预算
```

#### 3.4.3 ROI排行榜

**横向柱状图**：
- 家庭剧: 1.45（绿色）
- 综艺: 1.12（黄色）
- 动漫: 0.98（红色）

#### 3.4.4 验收标准

- [ ] 选择周期后点击"生成报告"15秒内返回
- [ ] 报告包含4个section
- [ ] ROI排行榜正确显示
- [ ] 可下载.md文件
- [ ] API失败时显示数据摘要（降级）

---

### 3.5 页面5：经验库 📚（核心页面）

**功能目标**：RAG检索历史活动，AI复用建议

#### 3.5.1 核心功能

| 功能模块 | 交互方式 | AI调用 | 优先级 |
|---------|---------|--------|--------|
| 场景描述输入 | 文本框 | ❌ | P0 |
| RAG检索 | 点击按钮 | ✅ (embedding) | P0 |
| 案例卡片展示 | 自动展开 | ❌ | P0 |
| AI复用建议 | 自动生成 | ✅ (可选) | P1 |
| 一键复用 | 下载模板 | ❌ | P1 |
| 知识库统计 | 图表 | ❌ | P1 |

#### 3.5.2 RAG技术方案

**方案A：FAISS（推荐）**
- 模型：sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- 索引：FAISS IndexFlatL2
- 相似度：余弦相似度

**方案B：BM25（网络受限时）**
- 模型：rank-bm25
- 分词：jieba
- 检索速度更快，无需下载模型

#### 3.5.3 案例卡片展示

每个案例显示：
- 📌 活动ID + 策略标签
- 成功因素
- ROI + 边现提升
- 相似度评分
- [📥 一键复用] [📖 查看详情]

#### 3.5.4 AI复用建议

基于最佳案例生成：
```markdown
💡 基于 2024Q4_VIP, 建议:
1. ✅ 沿用策略: 家庭剧70%+动漫30%
2. ✅ 资源位: 首页位3 + 详情页推荐
3. ⚠️ 优化点: 增加10%预算投首页位1
4. 📅 最佳时段: 周五19-22点+周末全天
5. 🎯 预期ROI: 1.32 (置信度80%)
```

#### 3.5.5 验收标准

- [ ] 输入查询后返回≥2个案例
- [ ] 相似度评分有区分（不全是100%）
- [ ] 案例卡片显示完整
- [ ] AI复用建议正确生成（可选）
- [ ] 可下载执行模板.md文件
- [ ] BM25/FAISS任一方案可用

---

## 四、风险防护策略

### 4.1 AI调用容错（核心）

#### 4.1.1 三层防护机制

| 防护层 | 技术方案 | 代码位置 |
|-------|---------|---------|
| L1: Schema约束 | Pydantic模型校验 | utils/validators.py |
| L2: 智能解析 | 提取JSON代码块 | ai_engine.py |
| L3: 降级兜底 | 默认策略模板 | ai_engine.py |

#### 4.1.2 降级策略

**策略推荐降级**：返回历史最佳活动模板
**异常解释降级**：返回数据摘要 + 规则建议
**复盘报告降级**：返回统计数据表格

#### 4.1.3 实现示例

```python
def parse_strategy_safe(response_text: str) -> StrategyResponse:
    try:
        # 提取JSON
        json_str = extract_json_block(response_text)
        # Pydantic校验
        data = json.loads(json_str)
        return StrategyResponse(**data)
    except Exception as e:
        logger.warning(f"解析失败，使用降级方案: {e}")
        return get_default_strategy()  # 返回模板
```

### 4.2 OpenAI客户端配置

#### 4.2.1 重试机制

```python
client = OpenAI(
    api_key=Config.OPENAI_API_KEY,
    timeout=30,
    max_retries=3
)

# 指数退避：1s, 2s, 4s
wait_time = 2 ** attempt
```

#### 4.2.2 环境变量

```bash
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT=30
OPENAI_MAX_RETRIES=3
```

### 4.3 数据生成注意事项

#### 4.3.1 固定随机种子

```python
np.random.seed(42)  # 确保异常点可复现
```

#### 4.3.2 人工注入异常点

```python
anomaly_dates = ['2025-10-05', '2025-10-12', '2025-10-21']
for date in anomaly_dates:
    df.loc[idx, 'arpu'] *= 0.85  # 下降15%
```

### 4.4 异常检测优化

#### 4.4.1 日历效应剔除

```python
# 归一化处理
arpu_adjusted = arpu - (weekend_mean - workday_mean) if is_holiday else arpu
```

#### 4.4.2 多维度交叉验证

```python
is_anomaly = (abs(zscore) > 1.5) & (abs(dau_change) < 30%)
```

---

## 五、技术规格

### 5.1 依赖包

```
streamlit==1.31.0
pandas==2.1.4
numpy==1.26.3
plotly==5.18.0
openai==1.10.0
python-dotenv==1.0.0
pydantic==2.5.0
loguru==0.7.2

# 方案A: FAISS
faiss-cpu==1.7.4
sentence-transformers==2.3.1

# 方案B: BM25（轻量级）
# rank-bm25==0.2.2
```

### 5.2 性能指标

| 指标 | 目标值 | 验收方式 |
|-----|--------|---------|
| AI响应时间 | <10秒 | 手动测试 |
| 页面加载时间 | <2秒 | Chrome DevTools |
| 异常检测率 | ≥2个异常点 | 固定种子验证 |
| RAG召回数 | ≥2个案例 | 手动查询测试 |
| 容错率 | 100% | API失败测试 |

### 5.3 兼容性

- Python: >=3.9
- 浏览器: Chrome/Safari/Edge 最新版
- 操作系统: macOS/Windows/Linux
- 网络: 需访问OpenAI API

---

## 六、交付计划

### 6.1 时间规划（2天）

#### Day 1 上午（4小时）- 基础框架

| 时间 | 任务 | 具体操作 | 产出 | 验收标准 |
|-----|------|---------|-----|---------|
| 09:00-09:30 | 项目结构搭建 | 创建文件夹+requirements.txt | 完整目录树 | `tree member_ai_demo/` 显示完整结构 |
| 09:30-10:30 | 生成CSV数据 | 执行generate_data.py | 4个CSV文件 | 打开CSV确认30行数据 |
| 10:30-11:30 | data_loader.py | 实现DataLoader类 | 数据加载模块 | `df = loader.load_daily_metrics()` 成功 |
| 11:30-12:00 | config.py + validators.py | 配置管理+JSON校验 | 工具模块 | 读取.env成功 |

**验收点**：
```bash
python -c "from modules.data_loader import DataLoader; print(len(DataLoader().load_daily_metrics()))"
# 输出: 30
```

#### Day 1 下午（4小时）- Streamlit框架

| 时间 | 任务 | 具体操作 | 产出 | 验收标准 |
|-----|------|---------|-----|---------|
| 13:30-14:30 | Streamlit主框架 | app.py + 侧边栏配置 | 主程序 | `streamlit run app.py` 成功启动 |
| 14:30-15:30 | charts.py | 实现ChartGenerator类 | 图表生成器 | 趋势图+多指标面板可显示 |
| 15:30-17:00 | 页面1+2框架 | 页面布局（无AI） | 2个页面文件 | 可切换页面，表单可操作 |
| 17:00-17:30 | Day1测试 | 全量测试 | 测试报告 | 前2页无报错 |

**验收点**：
- [ ] 主页显示4个指标卡片
- [ ] 侧边栏显示数据概览
- [ ] 页面1的趋势图正确显示
- [ ] 页面2的表单可输入

#### Day 2 上午（4小时）- AI核心

| 时间 | 任务 | 具体操作 | 产出 | 验收标准 |
|-----|------|---------|-----|---------|
| 09:00-10:30 | ai_engine.py | 实现AIStrategyEngine类 | AI引擎 | 3个方法可调用 |
| 10:30-11:00 | 测试AI调用 | 独立测试脚本 | 验证GPT | API返回正常JSON |
| 11:00-11:30 | 页面2接入AI | 集成策略推荐 | 策略推荐功能 | 点击按钮返回6个卡片 |
| 11:30-12:00 | budget_simulator.py | 预算模拟器 | 模拟器模块 | 滑块调整实时更新 |

**验收点**：
```python
# 测试AI调用
from modules.ai_engine import AIStrategyEngine
engine = AIStrategyEngine(api_key="sk-xxx")
result = engine.recommend_strategy("提升家庭向收入", df, segments_df)
assert "target_segment" in result
```

#### Day 2 下午（4小时）- 完成全部功能

| 时间 | 任务 | 具体操作 | 产出 | 验收标准 |
|-----|------|---------|-----|---------|
| 13:30-14:30 | 页面3完成 | 异常检测+AI解释 | 监控页面 | 检测到≥1个异常 |
| 14:30-15:15 | 页面4完成 | AI复盘报告 | 复盘页面 | 生成完整Markdown报告 |
| 15:15-16:00 | RAG实现 | BM25或FAISS | 经验检索模块 | 返回≥2个案例 |
| 16:00-16:45 | 页面5完成 | 经验库UI | 经验库页面 | RAG检索正常工作 |
| 16:45-17:30 | 全流程测试 | 5页全量测试 | 最终交付 | 全部验收点通过 |

**最终验收清单**：
- [ ] 5个页面全部可正常切换
- [ ] AI策略推荐<10秒返回
- [ ] AI异常解释<10秒返回
- [ ] AI复盘报告<15秒返回
- [ ] RAG检索返回≥2个案例
- [ ] 容错机制全部生效（测试API失败场景）

### 6.2 里程碑

| 里程碑 | 时间点 | 验收标准 |
|-------|--------|---------|
| M1: 数据+框架 | Day1 17:00 | 前2页可运行 |
| M2: AI核心 | Day2 11:30 | 策略推荐可用 |
| M3: 全部完成 | Day2 17:30 | 5页全可用 |
| M4: 演示就绪 | Day2 18:30 | 完整预演 |

---

## 七、演示脚本

### 7.1 时间分配（5分钟）

| 环节 | 时长 | 关键点 |
|-----|------|--------|
| 开场 | 30秒 | 痛点+价值 |
| 页面1 | 30秒 | 目标拆解树 |
| 页面2 | 90秒 | 策略推荐（核心） |
| 页面3 | 60秒 | 异常解释 |
| 页面4 | 30秒 | 自动复盘 |
| 页面5 | 45秒 | 经验召回 |
| 收尾 | 45秒 | 价值总结 |

### 7.2 演示前检查清单

**环境检查**：
- [ ] Python >=3.9
- [ ] pip install -r requirements.txt 成功
- [ ] .env 配置API Key
- [ ] streamlit run app.py 可启动
- [ ] 网络可访问OpenAI API

**功能测试**：
- [ ] 页面1-5都能切换
- [ ] 至少1个异常点可见
- [ ] AI策略推荐<10秒返回
- [ ] AI异常解释<10秒返回
- [ ] AI复盘报告<15秒返回
- [ ] RAG检索返回≥2个案例

**备份准备**：
- [ ] 离线录屏（5分钟）
- [ ] 截图集（5个页面各1张）
- [ ] 数据备份（data/目录）
- [ ] 应急话术（API失败圆场）

---

## 八、验收标准

### 8.1 L0: 基础可用性

- [ ] pip install 成功
- [ ] streamlit run app.py 10秒内打开
- [ ] 5个页面都能切换
- [ ] 无Python报错
- [ ] 页面布局正常

### 8.2 L1: AI调用验收

**策略推荐**：
- [ ] 点击"AI推荐"按钮
- [ ] 10秒内返回结果
- [ ] 6个卡片全展示
- [ ] 失败时显示默认模板

**异常解释**：
- [ ] 至少检测到1个异常点
- [ ] 10秒内返回Markdown分析
- [ ] 失败时显示数据摘要

**复盘报告**：
- [ ] 15秒内返回报告
- [ ] 包含4个section
- [ ] 可下载.md文件

### 8.3 L2: 数据验证

- [ ] 30天数据无缺失
- [ ] 2-3个异常点（固定日期）
- [ ] 节假日标识正确
- [ ] arpu = revenue / dau
- [ ] 移动平均线正常

### 8.4 L3: 交互体验

- [ ] 滑块拖动流畅
- [ ] 实时显示预估边现
- [ ] 资源位容量预警（>80%）
- [ ] RAG返回≥2个案例
- [ ] Plotly交互正常

---

## 九、风险与应对

### 9.1 主要风险

| 风险 | 概率 | 影响 | 应对方案 |
|-----|------|------|---------|
| GPT返回格式错误 | 高 | 严重 | 三层防护+降级 |
| API限流/超时 | 中 | 严重 | 重试机制+错误提示 |
| 网络环境差 | 中 | 中 | ①离线录屏 ②BM25替代FAISS |
| 异常点未检测到 | 低 | 中 | 固定随机种子 |
| 时间不足 | 中 | 严重 | 砍掉P2功能 |

### 9.2 应急预案

**API完全不可用**：
- 演示离线录屏
- 讲解技术原理+架构图
- 展示代码+Prompt设计

**部分功能失败**：
- 跳过失败页面
- 重点演示可用功能
- 说明技术方案可行性

---

## 十、后续升级路径

### 10.1 V1.5（1周内）

- 接入StarRocks实时数据
- 增加A/B测试模拟器
- 支持多目标优化（帕累托前沿）

### 10.2 V2.0（1个月内）

- AI Agent自主决策（无需人工输入）
- 实时预警推送（钉钉/企微）
- 多维度归因分析（Shapley值）

### 10.3 V3.0（3个月内）

- 强化学习策略优化
- 因果推断模型
- 跨平台联合运营

---

## 附录

### A. 核心代码实现示例

#### A.1 AI策略推荐引擎（modules/ai_engine.py - 核心部分）

```python
import openai
from typing import Dict, List
import pandas as pd
import json
from utils.validators import StrategyResponse

class AIStrategyEngine:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(
            api_key=api_key,
            timeout=30,
            max_retries=3
        )

    def recommend_strategy(self, target: str, history_df: pd.DataFrame,
                          segments_df: pd.DataFrame) -> Dict:
        """策略推荐核心逻辑"""

        # 1. 召回相似历史案例
        similar_cases = history_df.nlargest(3, 'roi')[
            ['campaign_id', 'strategy_tag', 'roi', 'arpu_lift', 'success_factors']
        ]

        # 2. 构建prompt
        prompt = f"""
你是会员运营AI助手,分析目标并推荐策略。

【运营目标】
{target}

【历史成功案例TOP3】
{similar_cases.to_string()}

【可用用户分层】
{segments_df[['segment', 'size', 'content_preference', 'price_sensitivity']].to_string()}

请输出JSON格式推荐方案:
{{
  "target_segment": "推荐人群(选择最匹配的segment)",
  "estimated_size": "预估触达人数",
  "content_strategy": {{
    "primary_content": "主推内容类型",
    "content_ratio": "内容配比(如家庭剧70%+动漫30%)",
    "reason": "为什么选择这个组合"
  }},
  "resource_allocation": {{
    "positions": ["资源位列表"],
    "peak_hours": "最佳投放时段",
    "budget_focus": "预算重点分配"
  }},
  "discount_recommendation": "优惠策略(10元券/5折月卡/免费试看)",
  "kpi_forecast": {{
    "arpu_lift": "预估边现提升(元)",
    "confidence": "置信度(0-100)",
    "roi_estimate": "预估ROI"
  }},
  "risk_alert": "风险提示(1-2条)",
  "historical_reference": "参考的历史活动ID"
}}
"""

        try:
            # 3. 调用GPT
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            # 4. 解析并校验
            return self._parse_strategy_safe(response.choices[0].message.content)

        except Exception as e:
            logger.warning(f"AI调用失败，使用降级方案: {e}")
            return self._get_default_strategy()

    def _parse_strategy_safe(self, response_text: str) -> Dict:
        """三层防护解析"""
        try:
            # 提取JSON代码块
            json_str = self._extract_json_block(response_text)
            data = json.loads(json_str)

            # Pydantic校验
            validated = StrategyResponse(**data)
            return validated.dict()

        except Exception as e:
            logger.warning(f"解析失败: {e}")
            # 尝试直接解析
            try:
                return json.loads(response_text)
            except:
                raise ValueError("无法解析AI响应")

    def _get_default_strategy(self) -> Dict:
        """降级默认策略"""
        return {
            "target_segment": "家庭向高活跃",
            "estimated_size": "86万",
            "content_strategy": {
                "primary_content": "家庭剧",
                "content_ratio": "家庭剧70%+动漫20%+综艺10%",
                "reason": "基于历史最佳ROI活动"
            },
            "resource_allocation": {
                "positions": ["首页位3", "详情页推荐"],
                "peak_hours": "周五19-22点+周末全天",
                "budget_focus": "70%投入首页位"
            },
            "discount_recommendation": "10元券",
            "kpi_forecast": {
                "arpu_lift": "+0.019",
                "confidence": "75",
                "roi_estimate": "1.30"
            },
            "risk_alert": "建议延长活动周期至7天以上",
            "historical_reference": "2024Q4_VIP"
        }
```

#### A.2 数据生成脚本（scripts/generate_data.py）

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 固定随机种子（确保异常点可复现）
np.random.seed(42)

def generate_daily_metrics(days=30):
    """生成日报数据"""
    dates = pd.date_range(end=datetime.now(), periods=days)

    daily_data = []
    for i, date in enumerate(dates):
        # 周期性波动
        base_dau = 4700000
        weekend_boost = 200000 if date.dayofweek >= 5 else 0
        random_factor = np.random.randint(-100000, 150000)
        dau = base_dau + weekend_boost + random_factor

        # 边现模拟
        base_arpu = 0.092
        content_boost = np.random.choice([0.005, 0.008, -0.003], p=[0.4, 0.3, 0.3])
        arpu = base_arpu + content_boost + np.random.normal(0, 0.002)

        # 人工注入异常点
        if i in [5, 12, 21]:  # 固定异常日期
            arpu *= 0.85  # 下降15%

        revenue = int(dau * arpu)

        daily_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'dau': dau,
            'revenue': revenue,
            'new_members': np.random.randint(18000, 25000),
            'renew_members': np.random.randint(58000, 68000),
            'content_type': np.random.choice(['家庭剧', '动漫', '综艺'], p=[0.5, 0.3, 0.2]),
            'platform': 'TV',
            'resource_position': np.random.choice(['首页位1', '首页位3', '详情页推荐']),
            'discount_type': np.random.choice(['10元券', '5折月卡', '免费试看']),
            'is_holiday': 1 if date.dayofweek >= 5 else 0,
            'day_of_week': date.dayofweek
        })

    return pd.DataFrame(daily_data)

# 生成并保存
df = generate_daily_metrics(30)
df.to_csv('data/daily_metrics.csv', index=False)
print(f"✅ 生成 {len(df)} 行数据")
```

#### A.3 异常检测算法（modules/anomaly_detector.py）

```python
import pandas as pd
import numpy as np

class AnomalyDetector:
    @staticmethod
    def detect_arpu_anomalies(df: pd.DataFrame, threshold=1.5):
        """
        智能异常检测（剔除日历效应）

        Args:
            df: 包含arpu, is_holiday的DataFrame
            threshold: Z-Score阈值（默认1.5）

        Returns:
            异常点DataFrame
        """
        # 1. 计算工作日/周末基线
        workday_mean = df[df['is_holiday'] == 0]['arpu'].mean()
        weekend_mean = df[df['is_holiday'] == 1]['arpu'].mean()

        # 2. 归一化处理（剔除日历效应）
        df['arpu_adjusted'] = df.apply(
            lambda row: row['arpu'] - (weekend_mean - workday_mean) if row['is_holiday'] else row['arpu'],
            axis=1
        )

        # 3. 滚动窗口Z-Score
        df['arpu_ma7'] = df['arpu_adjusted'].rolling(window=7, min_periods=1).mean()
        df['arpu_std7'] = df['arpu_adjusted'].rolling(window=7, min_periods=1).std()
        df['arpu_zscore'] = (df['arpu_adjusted'] - df['arpu_ma7']) / df['arpu_std7']

        # 4. 多维度交叉验证（避免DAU突增导致的误判）
        df['dau_change'] = df['dau'].pct_change() * 100

        is_anomaly = (
            (abs(df['arpu_zscore']) > threshold) &  # 边现异常
            (abs(df['dau_change']) < 30)            # DAU无剧烈波动
        )

        # 5. 分级
        df['anomaly_level'] = 'normal'
        df.loc[abs(df['arpu_zscore']) > 1.5, 'anomaly_level'] = '🟡 轻微'
        df.loc[abs(df['arpu_zscore']) > 2.0, 'anomaly_level'] = '🟠 中度'
        df.loc[abs(df['arpu_zscore']) > 2.5, 'anomaly_level'] = '🔴 严重'

        return df[is_anomaly][['date', 'arpu', 'arpu_zscore', 'anomaly_level']]
```

### B. 数据生成脚本

见上方 A.2

### C. Prompt模板

#### B.1 策略推荐Prompt

```
你是会员运营AI助手，基于历史数据推荐策略。

【运营目标】
{target}

【历史成功案例TOP3】
{similar_cases}

【可用用户分层】
{segments_df}

请输出JSON格式（严格遵守schema）:
{
  "target_segment": "...",
  ...
}
```

#### B.2 异常解释Prompt

```
你是数据分析专家，解释会员指标异常。

【异常日期】{date}
【指标数据】...

请按以下格式输出（Markdown）:
### 核心原因
...
```

### C. 配置文件

见 `.env.example`

### D. API文档

#### OpenAI调用示例

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3,
    timeout=30
)
```

---

## 文档变更记录

| 版本 | 日期 | 变更内容 | 作者 |
|-----|------|---------|------|
| v1.0 | 2025-10-27 | 初始版本 | - |

---

**文档结束**
