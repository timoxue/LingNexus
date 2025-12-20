from typing import List

from core_agents.intelligence_service.schema import DailyDigestItem, NewsItem, TopicConfig, UserConfig
from shared.skills import get_skill
from shared.skills.intelligence.daily_digest import DailyDigestInput
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


class AnalysisAgent:
    """负责对检索到的资讯做去重、排序，并调用大模型生成订阅日报摘要。"""

    async def build_digest(
        self,
        topic: TopicConfig,
        news_list: List[NewsItem],
        users: List[UserConfig] | None = None,
        role: str | None = None,
    ) -> DailyDigestItem:
        """针对单个主题生成订阅日报内容。"""
        # 1. 简单去重（按 URL 或标题）
        unique_news: List[NewsItem] = []
        seen_keys = set()
        for item in news_list:
            key = item.url or item.title
            if not key:
                continue
            if key in seen_keys:
                continue
            seen_keys.add(key)
            unique_news.append(item)

        # 2. 简单排序：按发布时间逆序（字符串比较足够满足 mock 数据场景）
        unique_news.sort(key=lambda x: (x.published_at or ""), reverse=True)

        if not unique_news:
            digest_text = f"当前主题：{topic.name} 暂无可用于订阅日报的资讯。"
            return DailyDigestItem(topic=topic, news=[], digest_summary=digest_text, role=role)

        # 限制数量在配置的 max_items 之内
        limited_news = unique_news[: topic.max_items]

        # 3. 组织传入 Prompt 的候选资讯文本
        news_items_str_parts: List[str] = []
        for idx, item in enumerate(limited_news, start=1):
            line = [
                f"[{idx}] 标题: {item.title}",
                f"来源/日期: {item.source or '未知来源'} / {item.published_at or '未知日期'}",
                f"摘要: {item.summary or '（无摘要）'}",
                f"链接: {item.url or '（无链接）'}",
            ]
            news_items_str_parts.append("\n".join(line))

        news_items_str = "\n\n".join(news_items_str_parts)

        # 4. 优先通过技能中心调用订阅日报生成技能
        skill = get_skill("intel.generate_daily_digest")
        if skill is not None:
            skill_input = DailyDigestInput(
                topic_name=topic.name,
                topic_description=topic.description or "",
                news_items_text=news_items_str,
                role=role,
            )
            skill_output = await skill.execute(skill_input)
            digest_summary = skill_output.data if skill_output.success else ""
        else:
            # 回退到函数封装，保证在技能未注册时仍可工作
            from shared.skills.intelligence.daily_digest import generate_daily_digest_text

            digest_summary = await generate_daily_digest_text(
                topic_name=topic.name,
                topic_description=topic.description or "",
                news_items_text=news_items_str,
                role=role,
            )

        logger.info(
            "AnalysisAgent generating digest",
            extra={
                "topic": topic.name,
                "news_count": len(limited_news),
                "role": role or "综合读者",
            },
        )

        return DailyDigestItem(topic=topic, news=limited_news, digest_summary=digest_summary, role=role)


analysis_agent = AnalysisAgent()
