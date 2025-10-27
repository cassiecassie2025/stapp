"""
RAG经验库检索模块（BM25实现）
"""
import pandas as pd
from rank_bm25 import BM25Okapi
import jieba


class CampaignRAG:
    """活动经验RAG检索器"""

    def __init__(self):
        self.bm25 = None
        self.campaigns_df = None
        self.tokenized_docs = []

    def build_index(self, campaigns_df: pd.DataFrame):
        """构建BM25索引"""
        self.campaigns_df = campaigns_df.copy()

        # 构建检索文本
        self.campaigns_df['search_text'] = campaigns_df.apply(
            lambda row: f"{row['strategy_tag']} {row['target_segment']} {row['success_factors']} {row['content_mix']}",
            axis=1
        )

        # 分词
        self.tokenized_docs = [
            list(jieba.cut(text))
            for text in self.campaigns_df['search_text']
        ]

        # 创建BM25索引
        self.bm25 = BM25Okapi(self.tokenized_docs)

        print(f"✅ RAG索引构建完成: {len(campaigns_df)} 个历史活动")

    def search(self, query: str, top_k: int = 3) -> pd.DataFrame:
        """
        检索相似活动

        Args:
            query: 查询文本
            top_k: 返回top_k个结果

        Returns:
            检索结果DataFrame
        """
        if self.bm25 is None:
            raise ValueError("请先调用build_index()构建索引")

        # 查询分词
        tokenized_query = list(jieba.cut(query))

        # 检索
        scores = self.bm25.get_scores(tokenized_query)

        # 获取top_k索引
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        # 返回结果
        results = self.campaigns_df.iloc[top_indices].copy()
        results['similarity_score'] = [scores[i] for i in top_indices]

        # 归一化分数到0-1
        max_score = results['similarity_score'].max() if len(results) > 0 and results['similarity_score'].max() > 0 else 1
        results['similarity_score'] = results['similarity_score'] / max_score

        return results[[
            'campaign_id', 'strategy_tag', 'target_segment',
            'roi', 'arpu_lift', 'success_factors', 'similarity_score'
        ]]
