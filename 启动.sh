#!/bin/bash

# 会员智能运营闭环 - 一键启动脚本

echo "🚀 会员智能运营闭环 Demo - 启动中..."
echo ""

# 切换到项目目录
cd "$(dirname "$0")"

# 检查数据文件
echo "📁 检查数据文件..."
if [ ! -f "data/daily_metrics.csv" ]; then
    echo "⚠️  数据文件不存在，正在生成..."
    python scripts/generate_data.py
else
    echo "✅ 数据文件已存在"
fi

echo ""
echo "📝 检查环境配置..."

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️  .env文件不存在"
    echo "💡 提示：启动后请在左侧边栏输入OpenAI API Key"
    echo "   或者创建.env文件并添加: OPENAI_API_KEY=sk-xxx"
else
    echo "✅ 环境配置已存在"
fi

echo ""
echo "🎯 启动Streamlit应用..."
echo "📍 浏览器将自动打开 http://localhost:8501"
echo ""
echo "💡 使用提示："
echo "   1. 在左侧边栏输入OpenAI API Key"
echo "   2. 等待系统加载数据"
echo "   3. 开始体验5页完整闭环"
echo ""
echo "---"
echo ""

# 启动Streamlit
streamlit run app.py
