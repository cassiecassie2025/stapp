#!/bin/bash

# 会员智能运营闭环 - 依赖安装脚本

echo "🚀 开始安装依赖包..."
echo ""

# 切换到项目目录
cd "$(dirname "$0")"

# 升级pip
echo "📦 升级pip..."
pip install --upgrade pip -q

# 安装依赖
echo "📦 安装项目依赖..."
pip install -r requirements.txt

echo ""
echo "✅ 依赖安装完成！"
echo ""

# 验证关键包
echo "🔍 验证关键包..."
python -c "
import streamlit
import pandas
import plotly
import openai
import loguru
import matplotlib
from rank_bm25 import BM25Okapi
import jieba

print('✅ streamlit:', streamlit.__version__)
print('✅ pandas:', pandas.__version__)
print('✅ plotly:', plotly.__version__)
print('✅ openai:', openai.__version__)
print('✅ matplotlib: 已安装')
print('✅ rank-bm25: 已安装')
print('✅ jieba: 已安装')
print('')
print('🎉 所有依赖包验证通过！')
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
    echo "📝 现在可以运行:"
    echo "   streamlit run app.py"
else
    echo ""
    echo "⚠️  部分包验证失败，请手动检查"
fi
