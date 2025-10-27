"""
配置管理模块
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """全局配置类"""

    # OpenAI配置（也支持DeepSeek等兼容API）
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', None)  # DeepSeek: https://api.deepseek.com/v1
    OPENAI_TIMEOUT = int(os.getenv('OPENAI_TIMEOUT', '30'))
    OPENAI_MAX_RETRIES = int(os.getenv('OPENAI_MAX_RETRIES', '3'))

    # 数据路径
    DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

    # 异常检测配置
    ANOMALY_THRESHOLD = 1.5  # Z-Score阈值
    ANOMALY_WINDOW = 7  # 滚动窗口天数

    # UI配置
    PAGE_TITLE = "会员智能运营闭环"
    PAGE_ICON = "🎯"

    @classmethod
    def validate(cls):
        """验证配置有效性"""
        if not cls.OPENAI_API_KEY:
            return False, "请配置OPENAI_API_KEY环境变量"

        if not os.path.exists(cls.DATA_PATH):
            return False, f"数据目录不存在: {cls.DATA_PATH}"

        return True, "配置验证通过"
