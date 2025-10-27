"""
会员智能运营闭环 Demo - 主程序
"""
import streamlit as st
from modules.data_loader import DataLoader
from modules.ai_engine import AIStrategyEngine
from modules.rag_search import CampaignRAG
from utils.config import Config
import os

# 页面配置
st.set_page_config(
    page_title=Config.PAGE_TITLE,
    page_icon=Config.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化session_state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.ai_engine = None
    st.session_state.rag = None
    st.session_state.daily_df = None
    st.session_state.segments_df = None
    st.session_state.campaigns_df = None
    st.session_state.capacity_df = None

# 侧边栏
with st.sidebar:
    st.title(f"{Config.PAGE_ICON} {Config.PAGE_TITLE}")
    st.markdown("---")

    # API 提供商选择
    st.markdown("### ⚙️ AI配置")
    api_provider = st.radio(
        "选择API提供商",
        ["OpenAI", "DeepSeek"],
        help="选择你要使用的AI服务提供商"
    )

    # 根据提供商显示不同的配置
    if api_provider == "OpenAI":
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=os.getenv('OPENAI_API_KEY', ''),
            help="请输入你的OpenAI API Key"
        )
        model = st.selectbox(
            "选择模型",
            ["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-3.5-turbo"],
            help="推荐使用 gpt-4o-mini（性价比高）"
        )
        base_url = None

    else:  # DeepSeek
        api_key = st.text_input(
            "DeepSeek API Key",
            type="password",
            value=os.getenv('DEEPSEEK_API_KEY', ''),
            help="请输入你的DeepSeek API Key"
        )
        model = "deepseek-chat"
        base_url = "https://api.deepseek.com/v1"

    if api_key and not st.session_state.data_loaded:
        with st.spinner("正在加载数据..."):
            try:
                # 初始化数据加载器
                loader = DataLoader()

                # 加载数据
                st.session_state.daily_df = loader.load_daily_metrics()
                st.session_state.segments_df = loader.load_user_segments()
                st.session_state.campaigns_df = loader.load_campaign_history()
                st.session_state.capacity_df = loader.load_resource_capacity()

                # 初始化AI引擎（传入配置）
                st.session_state.ai_engine = AIStrategyEngine(
                    api_key=api_key,
                    model=model,
                    base_url=base_url
                )

                # 初始化RAG
                st.session_state.rag = CampaignRAG()
                st.session_state.rag.build_index(st.session_state.campaigns_df)

                st.session_state.data_loaded = True
                st.success("✅ 系统初始化完成!")

            except Exception as e:
                st.error(f"❌ 初始化失败: {str(e)}")
                st.info("请确保已运行 `python scripts/generate_data.py` 生成数据文件")

    st.markdown("---")
    st.markdown("### 数据概览")

    if st.session_state.data_loaded:
        st.metric("数据天数", len(st.session_state.daily_df))
        st.metric("用户分层", len(st.session_state.segments_df))
        st.metric("历史活动", len(st.session_state.campaigns_df))
    else:
        st.info("请输入API Key以加载数据")

    st.markdown("---")
    st.markdown("### 功能导航")
    st.markdown("""
- 🎯 **目标规划**: AI解读目标并预测趋势
- 👥 **人群策略**: 智能圈人+策略推荐
- 📈 **实时监控**: 异常检测+AI解释
- 🧠 **AI复盘**: 自动生成分析报告
- 📚 **经验库**: RAG召回相似活动
    """)

# 主页面
st.title(f"{Config.PAGE_ICON} 会员智能运营闭环 Demo")

st.markdown("""
## 系统价值

**AI如何让会员运营从「拍脑袋决策」变成「数据+智能驱动」**

### 三大核心场景

1. **异常响应** 🔍
   - 老板问："为什么这周边现下降了？"
   - AI答：自动分析原因 + 给出3条行动建议（10秒内）

2. **策略制定** 💡
   - 运营问："如何提升家庭向会员收入？"
   - AI答：推荐完整策略组合（人群+内容+资源位+优惠+KPI预测）

3. **复盘总结** 📊
   - 复盘会："上次活动效果怎么样？"
   - AI答：自动生成Markdown复盘报告（15秒内）

---

👈 **请在左侧输入API Key开始使用，然后从侧边栏选择功能页面**
""")

if st.session_state.data_loaded:
    st.markdown("### 快速数据预览")

    # 显示最新指标
    loader = DataLoader()
    latest_metrics = loader.get_latest_metrics(st.session_state.daily_df)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "最新DAU",
        f"{latest_metrics.get('dau', 0):,.0f}",
        f"{latest_metrics.get('dau_change', 0):.1f}%"
    )
    col2.metric(
        "会员收入",
        f"{latest_metrics.get('revenue', 0):,.0f}元",
        f"{latest_metrics.get('revenue_change', 0):.1f}%"
    )
    col3.metric(
        "单DAU边现",
        f"{latest_metrics.get('arpu', 0):.4f}元",
        f"{latest_metrics.get('arpu_change', 0):.1f}%"
    )
    col4.metric(
        "转化率",
        f"{latest_metrics.get('conversion_rate', 0):.2f}%"
    )

    st.markdown("---")
    st.info("💡 **提示**: 请从左侧边栏选择功能页面开始体验完整闭环流程")

else:
    st.warning("⚠️ 请先在左侧边栏输入OpenAI API Key")

    with st.expander("📖 如何获取OpenAI API Key"):
        st.markdown("""
        1. 访问 [OpenAI Platform](https://platform.openai.com/)
        2. 注册/登录账号
        3. 进入 API Keys 页面
        4. 创建新的API Key
        5. 复制并粘贴到左侧输入框

        或者在项目根目录创建 `.env` 文件：
        ```
        OPENAI_API_KEY=sk-your-api-key-here
        ```
        """)
