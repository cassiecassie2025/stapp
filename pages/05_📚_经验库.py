"""
页面5：经验库与RAG检索（重新设计 - 新手友好版）
"""
import streamlit as st
import pandas as pd

st.title("📚 活动经验知识库")

if not st.session_state.get('data_loaded'):
    st.error("❌ 数据未加载，请先在主页配置API Key并等待数据加载完成")
    st.stop()

rag = st.session_state.rag
campaigns = st.session_state.campaigns_df

# 顶部操作指引
st.info("💡 **新手指引**：本页面帮助您从历史活动中查找相似案例。输入目标 → 检索案例 → 查看详情 → 下载模板")

# ==================== 第1部分：经验库概览 ====================
st.markdown("---")
st.markdown("## 📊 第1部分：经验库概览")
st.markdown("*查看知识库统计和历史活动分布*")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "总活动数",
        len(campaigns),
        help="历史活动总数"
    )

with col2:
    st.metric(
        "平均ROI",
        f"{campaigns['roi'].mean():.2f}",
        help="所有活动的平均投入产出比"
    )

with col3:
    st.metric(
        "最高ROI",
        f"{campaigns['roi'].max():.2f}",
        help="历史最佳ROI记录"
    )

with col4:
    avg_arpu_lift = campaigns['arpu_lift'].apply(lambda x: float(x.replace('+', '')) if isinstance(x, str) else 0).mean()
    st.metric(
        "平均边现提升",
        f"+{avg_arpu_lift:.3f}",
        help="平均单DAU边现提升"
    )

# 策略标签分布
st.markdown("---")
st.markdown("### 📈 策略标签分布")
st.caption("查看不同策略标签的活动数量分布")

strategy_counts = campaigns['strategy_tag'].value_counts()
st.bar_chart(strategy_counts)

with st.expander("📊 查看完整活动列表"):
    st.dataframe(
        campaigns[['campaign_id', 'strategy_tag', 'target_segment', 'roi', 'arpu_lift', 'start_date', 'end_date']],
        use_container_width=True,
        column_config={
            'campaign_id': '活动ID',
            'strategy_tag': '策略标签',
            'target_segment': '目标人群',
            'roi': st.column_config.NumberColumn('ROI', format="%.2f"),
            'arpu_lift': '边现提升',
            'start_date': st.column_config.DateColumn('开始日期', format="YYYY-MM-DD"),
            'end_date': st.column_config.DateColumn('结束日期', format="YYYY-MM-DD")
        }
    )

# ==================== 第2部分：智能检索 ====================
st.markdown("---")
st.markdown("## 🔍 第2部分：智能检索相似活动")
st.markdown("*输入您的运营场景，AI将检索最相关的历史案例*")

with st.form("rag_search_form"):
    st.markdown("### 📋 检索表单")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("**1️⃣ 描述运营场景** *（越详细越好）*")
        query = st.text_area(
            "运营场景",
            value="提升单DAU边现，重点在家庭向高活跃用户，周末档期",
            height=100,
            help="详细描述您的运营目标、人群、内容偏好等，系统将检索相似案例",
            label_visibility="collapsed"
        )

    with col2:
        st.markdown("**2️⃣ 返回案例数**")
        top_k = st.slider(
            "案例数量",
            min_value=1,
            max_value=6,
            value=3,
            help="返回最相似的N个案例",
            label_visibility="collapsed"
        )
        st.caption(f"📋 返回 **{top_k}** 个案例")

    st.markdown("---")

    # 提交按钮
    search_submitted = st.form_submit_button(
        "🔍 检索相似活动",
        type="primary",
        use_container_width=True
    )

# 执行检索
if search_submitted or st.session_state.get('rag_searched'):

    if search_submitted:
        with st.spinner("🔍 RAG检索中，请稍候（约3-5秒）..."):
            try:
                # RAG召回
                results = rag.search(query, top_k=top_k)

                # 保存结果
                st.session_state.rag_results = results
                st.session_state.rag_searched = True
                st.session_state.rag_query = query

                st.success(f"✅ 检索完成，找到 {len(results)} 个相关案例")

            except Exception as e:
                st.error(f"❌ 检索失败: {str(e)}")
                st.info("💡 使用降级方案：返回TOP ROI案例...")

                # 降级方案：返回top ROI案例
                results = campaigns.nlargest(top_k, 'roi').copy()
                results['similarity_score'] = 0.8
                st.session_state.rag_results = results
                st.session_state.rag_searched = True
                st.session_state.rag_query = query

# ==================== 第3部分：检索结果展示 ====================
if st.session_state.get('rag_searched'):
    results = st.session_state.get('rag_results')
    query = st.session_state.get('rag_query', '')

    st.markdown("---")
    st.markdown("## 📋 第3部分：检索结果")
    st.markdown(f"*基于查询「{query[:50]}...」，找到以下相似案例*")

    # 使用tabs展示不同案例
    if len(results) > 0:
        # 创建tabs
        tab_labels = [f"案例{i+1}：{row['campaign_id']}" for i, (_, row) in enumerate(results.head(3).iterrows())]
        tabs = st.tabs(tab_labels)

        for tab_idx, (idx, row) in enumerate(results.head(3).iterrows()):
            with tabs[tab_idx]:
                # 案例卡片
                st.markdown(f"### 📌 {row['campaign_id']}")

                # 关键指标
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "ROI",
                        f"{row['roi']:.2f}",
                        help="投入产出比"
                    )
                with col2:
                    st.metric(
                        "边现提升",
                        row['arpu_lift'],
                        help="单DAU边现提升"
                    )
                with col3:
                    st.metric(
                        "相似度",
                        f"{row['similarity_score']:.0%}",
                        help="与您的查询的相似度"
                    )

                st.markdown("---")

                # 策略详情
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### 🎯 策略信息")
                    st.markdown(f"""
                    **策略标签**：{row['strategy_tag']}

                    **目标人群**：{row['target_segment']}

                    **成功因素**：
                    {row['success_factors']}
                    """)

                with col2:
                    # 获取详细信息
                    campaign_detail = campaigns[campaigns['campaign_id'] == row['campaign_id']]
                    if len(campaign_detail) > 0:
                        detail = campaign_detail.iloc[0]

                        st.markdown("#### 📊 执行详情")
                        st.markdown(f"""
                        **活动周期**：{detail['start_date'].strftime('%Y-%m-%d')} 至 {detail['end_date'].strftime('%Y-%m-%d')}

                        **内容组合**：{detail['content_mix']}

                        **资源位**：{detail['resource_positions']}

                        **优惠方案**：{detail['discount']}

                        **预算**：{detail['budget_used']}万元
                        """)

                st.markdown("---")

                # 数据表现
                if len(campaign_detail) > 0:
                    st.markdown("#### 📈 数据表现")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("收入提升", detail['revenue_lift'])
                    with col2:
                        st.metric("边现提升", detail['arpu_lift'])
                    with col3:
                        st.metric("ROI", f"{detail['roi']:.2f}")

    # ==================== 第4部分：AI复用建议 ====================
    st.markdown("---")
    st.markdown("## 💡 第4部分：AI复用建议")
    st.markdown("*基于最相似案例的AI建议*")

    if len(results) > 0:
        best_case = results.iloc[0]
        campaign_detail = campaigns[campaigns['campaign_id'] == best_case['campaign_id']]

        if len(campaign_detail) > 0:
            detail = campaign_detail.iloc[0]

            # 使用tabs组织复用内容
            tab1, tab2 = st.tabs(["🤖 AI建议", "📥 下载模板"])

            with tab1:
                recommendation = f"""
### 基于案例：{best_case['campaign_id']} (相似度: {best_case['similarity_score']:.0%})

#### ✅ 推荐沿用策略
- **策略标签**：{best_case['strategy_tag']}
- **目标人群**：{best_case['target_segment']}
- **内容组合**：{detail['content_mix']}
- **资源位**：{detail['resource_positions']}
- **优惠方案**：{detail['discount']}

#### 🔑 关键成功因素
{best_case['success_factors']}

#### 📊 预期效果
- **预期ROI**：{best_case['roi']:.2f}
- **预期边现提升**：{best_case['arpu_lift']}
- **建议预算**：{detail['budget_used']}万元

#### 💡 优化建议
1. **预算优化**：在原策略基础上增加10%预算投入首页焦点图位
2. **周期优化**：延长活动周期至7天以上，观察完整用户行为周期
3. **时段优化**：重点关注周末档期（周五19:00-周日23:00）
4. **监控优化**：实时监控转化率，如低于3%立即调整内容策略

#### ⚠️ 风险提示
- 该案例预算为{detail['budget_used']}万元，请确保预算充足
- 建议提前3天申请资源位，避免临时抢占
- 优惠券成本约占预算30%，需提前规划
"""

                st.markdown(recommendation)

            with tab2:
                st.markdown("### 📥 下载可复用模板")

                template = f"""# 活动执行模板（复用自: {best_case['campaign_id']}）

## 基本信息

**原案例ID**：{best_case['campaign_id']}
**相似度**：{best_case['similarity_score']:.0%}
**历史ROI**：{best_case['roi']:.2f}

---

## 策略标签
{detail['strategy_tag']}

## 目标人群
{detail['target_segment']}

## 内容策略
{detail['content_mix']}

**说明**：
- 优先推荐主推内容类型
- 建议准备200+部精选内容
- 每3天更新一次推荐池

## 资源位配置
{detail['resource_positions']}

**投放时段**：
- 工作日：19:00-23:00
- 周末：全天（重点投放）

**预算分配**：
- 首页焦点图位：40%
- 首页推荐流位：30%
- 详情页推荐位：20%
- Push通知：10%

## 优惠方案
{detail['discount']}

**配置建议**：
- 发放规则：首页曝光后领取
- 有效期：7天
- 使用门槛：≥15元订单
- 预期核销率：35%

## 预算规划
**总预算**：{detail['budget_used']}万元

**成本构成**：
- 优惠券成本：约{detail['budget_used'] * 0.3:.1f}万元（30%）
- 资源位成本：约{detail['budget_used'] * 0.5:.1f}万元（50%）
- 内容制作：约{detail['budget_used'] * 0.2:.1f}万元（20%）

## KPI目标
- **收入提升**：{detail['revenue_lift']}
- **边现提升**：{detail['arpu_lift']}
- **预期ROI**：{detail['roi']:.2f}

## 历史表现（参考）
- 收入提升: {detail['revenue_lift']}
- 边现提升: {detail['arpu_lift']}
- ROI: {detail['roi']:.2f}

## 成功因素（必须重视）
{detail['success_factors']}

---

## 执行清单

### 第1-2天：准备阶段
- [ ] 配置内容推荐池（按{detail['content_mix']}配比）
- [ ] 申请资源位：{detail['resource_positions']}（提前3天）
- [ ] 设置优惠券：{detail['discount']}
- [ ] 配置监控大盘（DAU、ARPU、转化率）
- [ ] 设置预警规则（ARPU ±15%）

### 第3-9天：执行阶段
- [ ] 每日查看监控大盘（早10点、晚20点）
- [ ] 每日分析关键指标
- [ ] 每3天微调内容策略
- [ ] 每日汇报进度

### 第10天：复盘阶段
- [ ] 生成AI复盘报告
- [ ] 提取策略执行模板
- [ ] 沉淀优化建议
- [ ] 更新经验库

---

## 注意事项

⚠️ **必读**：
1. **预算要求**：建议预算不低于{detail['budget_used']}万元
2. **周期要求**：建议活动周期至少7天
3. **资源要求**：需提前3天申请首页焦点图位
4. **监控要求**：必须配置实时监控和预警

⚡ **重点关注**：
- {detail['success_factors']}

---

**生成时间**：{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
**生成页面**：经验库 - AI复用建议
**原案例**：{best_case['campaign_id']}
"""

                st.download_button(
                    label="📥 下载完整复用模板",
                    data=template,
                    file_name=f"复用模板_{best_case['campaign_id']}.md",
                    mime="text/markdown",
                    use_container_width=True,
                    type="primary"
                )

                st.success("✅ 模板包含完整的策略信息、执行清单、注意事项，可直接用于团队执行")

# ==================== 底部引导 ====================
st.markdown("---")
st.markdown("## 🎉 恭喜！您已完成整个闭环体验")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.success("""
    ✅ **完整流程回顾**：

    1. **页面1：目标规划** - 设定运营目标并评估可行性
    2. **页面2：人群策略** - AI生成推荐策略和执行模板
    3. **页面3：实时监控** - 监控数据并分析异常
    4. **页面4：AI复盘** - 生成复盘报告和策略模板
    5. **页面5：经验库** - 检索历史案例并复用策略

    **下一步**：
    - 返回任意页面继续探索
    - 或使用真实数据开始实际运营
    """)

    st.info("💡 **提示**：建议将本系统集成到您的日常运营流程中，形成「规划→执行→监控→复盘→沉淀」的闭环")
