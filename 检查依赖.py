"""
检查并安装所有依赖包
"""
import subprocess
import sys

def install_package(package):
    """安装Python包"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# 必需的包
required_packages = {
    'streamlit': 'streamlit==1.31.0',
    'pandas': 'pandas==2.1.4',
    'numpy': 'numpy==1.26.3',
    'plotly': 'plotly==5.18.0',
    'openai': 'openai==1.10.0',
    'python-dotenv': 'python-dotenv==1.0.0',
    'pydantic': 'pydantic==2.5.0',
    'loguru': 'loguru==0.7.2',
    'rank_bm25': 'rank-bm25==0.2.2',
    'jieba': 'jieba==0.42.1'
}

print("🔍 检查依赖包...")
print("=" * 60)

missing_packages = []

for module_name, package_spec in required_packages.items():
    try:
        __import__(module_name)
        print(f"✅ {module_name:20s} 已安装")
    except ImportError:
        print(f"❌ {module_name:20s} 未安装")
        missing_packages.append(package_spec)

print("=" * 60)

if missing_packages:
    print(f"\n发现 {len(missing_packages)} 个缺失的包")
    print("\n正在安装...")

    for package in missing_packages:
        print(f"\n安装 {package}...")
        try:
            install_package(package)
            print(f"✅ {package} 安装成功")
        except Exception as e:
            print(f"❌ {package} 安装失败: {e}")

    print("\n" + "=" * 60)
    print("🎉 依赖安装完成！")
else:
    print("\n✅ 所有依赖包已安装")

print("\n📝 现在可以运行:")
print("   streamlit run app.py")
