"""
Skill Creator Agent 服务

管理 Skill Creator Agent 的会话和交互
"""
import asyncio
import sys
import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

# 添加 framework 到路径
backend_dir = Path(__file__).parent.parent
framework_dir = backend_dir.parent / 'framework'
if str(framework_dir) not in sys.path:
    sys.path.insert(0, str(framework_dir))

try:
    from agentscope.message import Msg
    FRAMEWORK_AVAILABLE = True
except ImportError:
    FRAMEWORK_AVAILABLE = False
    logger.error("Failed to import agentscope.message")


# 四个维度定义
DIMENSIONS = ["core_value", "usage_scenario", "alias_preference", "boundaries"]

# 维度引导语
DIMENSION_GUIDANCE = {
    "core_value": "让我们从最基本的问题开始。",
    "usage_scenario": "很好！现在让我更深入了解一下使用场景。",
    "alias_preference": "为了让技能更容易使用，我们需要设计简洁的调用方式。",
    "boundaries": "最后，让我们明确技能的边界，避免过度承诺。",
}


class AgentSession:
    """Agent 会话管理"""

    def __init__(self, session_id: str, user_id: int):
        self.session_id = session_id
        self.user_id = user_id
        self.created_at = datetime.now()
        self.last_activity = datetime.now()

        # 对话状态
        self.current_dimension_idx = 0  # 当前维度索引 (0-3)
        self.conversation_history: List[Dict[str, str]] = []  # 对话历史
        self.answers: Dict[str, List[str]] = {d: [] for d in DIMENSIONS}  # 每个维度的所有回答
        self.metadata: Dict[str, Any] = {}  # 生成的元数据

        # Agent 实例（延迟创建）
        self.agent = None

    @property
    def current_dimension(self) -> str:
        """获取当前维度名称"""
        if self.current_dimension_idx < len(DIMENSIONS):
            return DIMENSIONS[self.current_dimension_idx]
        return "complete"

    async def initialize_agent(self, api_key: Optional[str] = None):
        """初始化 Agent"""
        if not FRAMEWORK_AVAILABLE:
            raise RuntimeError("Framework not available")

        try:
            logger.info(f"===== INITIALIZING AGENT FOR SESSION {self.session_id} =====")

            # 检查当前 Python 路径
            logger.info(f"Python path: {sys.path[:3]}")

            # 检查框架导入
            logger.info(f"Framework available: {FRAMEWORK_AVAILABLE}")
            try:
                from agentscope.message import Msg
                logger.info("AgentScope message import: OK")
            except Exception as e:
                logger.error(f"AgentScope message import failed: {e}")

            # 直接调用 create_skill_creator_agent，它会处理 AgentScope 初始化和 Studio 连接
            from lingnexus.react_agent import create_skill_creator_agent
            logger.info("create_skill_creator_agent imported successfully")

            # 检查参数
            logger.info(f"Creating agent with parameters:")
            logger.info(f"  model_name: qwen-max")
            logger.info(f"  api_key: {api_key[:20] if api_key else None}...")
            logger.info(f"  temperature: 0.4")
            logger.info(f"  project_name: LingNexus-SkillCreator")

            # 使用唯一的 project_name 以确保每个 session 有独立的 memory
            # AgentScope 的 memory 是按照 project 绑定的
            unique_project_name = f"LingNexus-SkillCreator-{self.session_id}"
            logger.info(f"Using unique project name for session-scoped memory: {unique_project_name}")

            self.agent = create_skill_creator_agent(
                model_name="qwen-max",
                api_key=api_key,
                temperature=0.4,
                project_name=unique_project_name,
            )

            logger.info(f"Agent '{self.agent.name}' created successfully")
            logger.info(f"Agent type: {type(self.agent).__name__}")
            logger.info(f"Agent has toolkit: {self.agent.toolkit is not None}")
            logger.info(f"AgentScope Studio should be available at: http://localhost:3000")
            logger.info(f"===== AGENT INITIALIZATION COMPLETE =====")
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def update_activity(self):
        """更新活动时间"""
        self.last_activity = datetime.now()

    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """检查会话是否过期"""
        delta = datetime.now() - self.last_activity
        return delta.total_seconds() > timeout_minutes * 60


class SkillCreatorAgentService:
    """Skill Creator Agent 服务

    管理多个 Agent 会话，处理前后端交互
    """

    def __init__(self):
        self.sessions: Dict[str, AgentSession] = {}
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start_cleanup_task(self):
        """启动定期清理过期会话的任务"""
        async def cleanup():
            while True:
                await asyncio.sleep(300)  # 每5分钟清理一次
                await self._cleanup_expired_sessions()

        self._cleanup_task = asyncio.create_task(cleanup())

    async def _cleanup_expired_sessions(self):
        """清理过期会话"""
        expired = [
            sid for sid, session in self.sessions.items()
            if session.is_expired()
        ]
        for sid in expired:
            del self.sessions[sid]
            logger.info(f"Cleaned up expired session: {sid}")

    async def create_session(
        self,
        user_id: int,
        api_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        创建新的 Agent 会话

        Args:
            user_id: 用户 ID
            api_key: DashScope API Key

        Returns:
            会话信息
        """
        logger.info(f"===== CREATE SESSION CALLED =====")
        logger.info(f"User ID: {user_id}")
        logger.info(f"API Key: {api_key[:20] if api_key else None}...")

        session_id = str(uuid.uuid4())
        logger.info(f"Generated session_id: {session_id}")

        session = AgentSession(session_id, user_id)
        logger.info(f"Created AgentSession: {session}")

        # 初始化 Agent
        logger.info(f"About to initialize agent for session {session_id}...")
        try:
            await session.initialize_agent(api_key)
            logger.info(f"Agent initialized successfully for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to initialize agent for session {session_id}: {e}")
            raise

        self.sessions[session_id] = session
        logger.info(f"Created new session {session_id} for user {user_id}")

        # 返回第一个问题的引导
        return {
            "session_id": session_id,
            "type": "next_dimension",
            "current_dimension": "core_value",
            "dimension_name": "核心价值",
            "question": "这个技能主要帮助用户解决什么问题？或者完成什么任务？",
            "guidance": "让我们从最基本的问题开始。请用简洁的语言描述：",
            "placeholder": "例如：帮助QA团队快速审查SOP文档的合规性",
            "examples": [
                "自动优化电商产品图片，去除背景并适配各平台尺寸",
                "分析临床试验数据，自动生成FDA提交格式的报告",
                "为销售团队生成个性化客户提案"
            ],
            "progress": {
                "current": 1,
                "total": 4,
                "percentage": 0
            }
        }

    async def chat(
        self,
        session_id: str,
        message: str,
        user_id: int,
    ) -> Dict[str, Any]:
        """
        与 Agent 对话

        Args:
            session_id: 会话 ID
            message: 用户消息
            user_id: 用户 ID

        Returns:
            Agent 响应
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if session.user_id != user_id:
            raise PermissionError(f"User {user_id} not authorized for session {session_id}")

        session.update_activity()

        # 保存用户回答到当前维度
        current_dim = session.current_dimension
        session.answers[current_dim].append(message)

        # 添加到对话历史
        session.conversation_history.append({
            "role": "user",
            "content": message,
            "dimension": current_dim
        })

        # 调用 Agent 判断是否充足并生成响应
        return await self._get_agent_response(session)

    async def _get_agent_response(self, session: AgentSession) -> Dict[str, Any]:
        """调用 Agent 获取响应"""
        try:
            # 构建给 Agent 的上下文
            context = self._build_agent_context(session)
            logger.info(f"===== SENDING TO AGENT =====")
            logger.info(f"Dimension: {session.current_dimension}")
            logger.info(f"Agent: {session.agent.name if session.agent else 'None'}")
            logger.info(f"Agent type: {type(session.agent).__name__}")
            logger.info(f"Context length: {len(context)} chars")
            logger.info(f"Context preview: {context[:500]}...")

            # 调用 Agent（使用 __call__ 方法，AgentScope Studio 会监控）
            # 注意：ReActAgent 的 __call__ 是异步的
            logger.info(f"Calling agent.{session.agent.name}.__call__()...")

            # 确保 agent 有正确的方法
            if not hasattr(session.agent, '__call__'):
                logger.error(f"Agent {session.agent.name} does not have __call__ method!")
                raise RuntimeError(f"Agent {session.agent.name} is not callable")

            response = await session.agent(Msg(
                name="user",
                content=context,
                role="user"
            ))

            # 提取响应文本（处理 ContentBlock 格式）
            response_str = self._extract_response_text(response)
            logger.info(f"===== AGENT RESPONDED =====")
            logger.info(f"Response type: {type(response)}")
            logger.info(f"Response length: {len(response_str)} chars")
            logger.info(f"Extracted response text: {response_str[:500]}...")

            # 解析 Agent 返回的 JSON
            agent_response = self._parse_agent_response(response_str)

            # 记录评分
            if "score" in agent_response:
                logger.info(f"===== LLM SCORING RESULT =====")
                logger.info(f"Score: {agent_response['score']}/100")
                logger.info(f"Reasoning: {agent_response.get('reasoning', 'N/A')}")
                logger.info(f"Decision: {agent_response.get('type', 'N/A')}")

            # 根据响应类型处理
            if agent_response.get("type") == "follow_up":
                # 继续追问当前维度
                logger.info(f"Action: FOLLOW_UP - asking for more information")
                return self._format_follow_up(session, agent_response)
            elif agent_response.get("type") == "next_dimension":
                # 进入下一个维度
                logger.info(f"Action: NEXT_DIMENSION - proceeding to next dimension")
                return await self._advance_dimension(session, agent_response)
            elif agent_response.get("type") == "summary":
                # 完成总结
                logger.info(f"Action: SUMMARY - completing the session")
                return self._format_summary(session, agent_response)
            else:
                # 无法识别的响应，使用默认逻辑
                logger.warning(f"Unknown response type: {agent_response.get('type')}, using default")
                return await self._advance_dimension(session, agent_response)

        except Exception as e:
            logger.error(f"===== ERROR IN AGENT CALL =====")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {e}")
            logger.error(f"Traceback:", exc_info=True)

            # 获取当前维度的中文名称
            dimension_names = {
                "core_value": "核心价值",
                "usage_scenario": "使用场景",
                "alias_preference": "别名偏好",
                "boundaries": "边界限制"
            }

            # 发生错误时，返回一个特殊的错误响应而不是默认通过
            return {
                "type": "error",
                "error": str(e),
                "current_dimension": session.current_dimension,
                "dimension_name": dimension_names.get(session.current_dimension, session.current_dimension),
                "follow_up_question": f"抱歉，处理您的回答时出现了错误。请重新描述或简化您的回答。\n\n错误信息: {str(e)[:100]}",
                "score": 0,  # 使用 0 分表示错误
                "reasoning": "Agent 调用失败",
                "progress": {
                    "current": session.current_dimension_idx + 1,
                    "total": 4,
                    "percentage": int((session.current_dimension_idx / 4) * 100)
                },
                "recommended_options": [
                    {"id": "opt1", "text": "简短描述你的技能用途"},
                    {"id": "opt2", "text": "继续下一个问题"}
                ]
            }

    def _build_agent_context(self, session: AgentSession) -> str:
        """构建给 Agent 的上下文"""
        context_parts = []

        # 首先强调 JSON 格式要求
        context_parts.append("⚠️ 重要：你必须以纯 JSON 格式响应，不要添加任何其他文字！")

        # 当前维度
        current_dim = session.current_dimension
        dimension_names = {
            "core_value": "核心价值",
            "usage_scenario": "使用场景",
            "alias_preference": "别名偏好",
            "boundaries": "边界限制"
        }

        # 获取最新的用户回答
        latest_answer = session.answers[current_dim][-1] if session.answers[current_dim] else ""

        context_parts.append(f"【当前维度】: {dimension_names.get(current_dim, current_dim)}")
        context_parts.append(f"【用户最新回答】: {latest_answer}")

        # 该维度的所有历史回答
        if len(session.answers[current_dim]) > 1:
            context_parts.append(f"\n【该维度的历史回答】:")
            for i, ans in enumerate(session.answers[current_dim][:-1], 1):
                context_parts.append(f"  历史回答{i}: {ans}")

        # 之前已完成的维度
        if session.current_dimension_idx > 0:
            context_parts.append("\n【已完成的维度】:")
            for dim in DIMENSIONS[:session.current_dimension_idx]:
                if session.answers[dim]:
                    context_parts.append(f"  {dimension_names.get(dim, dim)}: {'; '.join(session.answers[dim])}")

        # 添加当前维度的评分标准
        scoring_criteria = self._get_scoring_criteria(current_dim)
        context_parts.append(f"\n【评分标准】:\n{scoring_criteria}")

        context_parts.append("\n【你的任务】:")
        context_parts.append("1. 对用户最新回答进行评分（0-100分）")
        context_parts.append("2. 综合该维度的所有回答，判断信息是否充足")
        context_parts.append("3. 如果评分 >= 91，返回 next_dimension 进入下一维度")
        context_parts.append("4. 如果评分 < 91，返回 follow_up，并提供具体帮助")
        context_parts.append("")
        context_parts.append("【关于 recommended_options 的重要说明】：")
        context_parts.append("⚠️ recommended_options 必须是【具体的模拟回答】，而不是指导性提示！")
        context_parts.append("")
        context_parts.append("❌ 错误示例（指导性提示）：")
        context_parts.append('  {"id": "opt1", "text": "详细描述技能要解决的问题"}')
        context_parts.append('  {"id": "opt2", "text": "指出技能的目标用户群体"}')
        context_parts.append("")
        context_parts.append("✅ 正确示例（具体模拟回答）：")
        context_parts.append('  {"id": "opt1", "text": "帮助QA团队自动审查SOP文档的合规性和格式要求"}')
        context_parts.append('  {"id": "opt2", "text": "主要用于制药企业质量管理部门，每天检查大量Word文档"}')
        context_parts.append('  {"id": "opt3", "text": "用户上传文档后，自动提取关键信息并生成检查报告"}')
        context_parts.append("")
        context_parts.append("每个选项都应该：")
        context_parts.append("- 基于用户已提供的信息进行合理推断和补充")
        context_parts.append("- 使用完整的句子，描述具体的场景或功能")
        context_parts.append("- 长度在20-50字之间，提供足够具体的细节")
        context_parts.append("- 作为【答案】而不是【问题】呈现")
        context_parts.append("\n【返回格式】:")
        context_parts.append("必须严格按照以下 JSON 格式返回，不要添加任何其他文字：")
        context_parts.append("""
如果评分 >= 91：
```json
{
  "type": "next_dimension",
  "score": 92,
  "reasoning": "评分理由"
}
```

如果评分 < 91：
```json
{
  "type": "follow_up",
  "score": 65,
  "reasoning": "评分理由",
  "follow_up_question": "简要说明需要补充的信息方向",
  "recommended_options": [
    {"id": "opt1", "text": "基于用户信息的具体模拟回答1"},
    {"id": "opt2", "text": "基于用户信息的具体模拟回答2"}
  ]
}
```
""")

        return "\n".join(context_parts)

    def _get_scoring_criteria(self, dimension: str) -> str:
        """获取各维度的评分标准"""
        criteria = {
            "core_value": """
- 是否清晰描述解决的问题？（20分）
- 能否识别目标用户？（20分）
- 能否推断技能类别？（20分）
- 表达是否具体？（20分）
- 是否有明确的期望效果？（20分）
            """,
            "usage_scenario": """
- 是否有具体的使用场景描述？（25分）
- 是否知道输入是什么？（25分）
- 是否知道期望输出？（25分）
- 是否理解使用频率？（25分）
            """,
            "alias_preference": """
- 是否简洁（2-5个字）？（40分）
- 是否符合自然语言习惯？（30分）
- 是否容易记忆？（30分）
            """,
            "boundaries": """
- 是否有明确的限制说明？（40分）
- 是否识别合规要求？（30分）
- 是否知道不做什么？（30分）
            """
        }
        return criteria.get(dimension, "根据回答的完整性和具体性评分")

    def _extract_response_text(self, response) -> str:
        """从 Agent 响应中提取文本内容

        Args:
            response: Agent 返回的 Msg 对象

        Returns:
            提取的文本内容
        """
        try:
            # 检查 response.content 是否是 ContentBlock 列表
            if hasattr(response, 'content'):
                content = response.content

                # 如果是列表，提取所有 text block
                if isinstance(content, list):
                    text_parts = []
                    for block in content:
                        if isinstance(block, dict) and 'text' in block:
                            text_parts.append(block['text'])
                        elif hasattr(block, 'text'):
                            text_parts.append(block.text)
                    return '\n'.join(text_parts)

                # 如果是字符串，直接返回
                elif isinstance(content, str):
                    return content

            # 降级处理：转换为字符串
            return str(response.content)
        except Exception as e:
            logger.warning(f"Failed to extract response text: {e}")
            return str(response.content) if hasattr(response, 'content') else str(response)

    def _parse_agent_response(self, response: str) -> Dict[str, Any]:
        """解析 Agent 返回的 JSON"""
        logger.info(f"Parsing agent response, length: {len(response)}")

        # 方法1：尝试提取 ```json 代码块
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
            logger.info(f"Found JSON in code block")
        else:
            # 方法2：尝试查找第一个完整的 JSON 对象
            # 从第一个 { 开始匹配，直到找到对应的 }
            brace_start = response.find('{')
            if brace_start != -1:
                # 尝试匹配完整的 JSON 对象
                brace_count = 0
                json_end = brace_start
                for i in range(brace_start, len(response)):
                    if response[i] == '{':
                        brace_count += 1
                    elif response[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break

                if json_end > brace_start:
                    json_str = response[brace_start:json_end].strip()
                    logger.info(f"Extracted JSON object from response")
                else:
                    json_str = response.strip()
                    logger.info(f"No complete JSON object found, parsing directly")
            else:
                # 方法3：尝试直接解析整个响应
                json_str = response.strip()
                logger.info(f"No JSON found, parsing directly")

        try:
            parsed = json.loads(json_str)
            logger.info(f"Successfully parsed JSON, type: {parsed.get('type')}, score: {parsed.get('score')}")
            return parsed
        except json.JSONDecodeError as e:
            logger.warning(f"===== JSON PARSE FAILED =====")
            logger.warning(f"Error: {e}")
            logger.warning(f"JSON string was: {json_str[:500]}")
            logger.warning(f"Full agent response: {response[:1000]}")
            # 返回解析失败的响应，使用 -1 分表示解析失败
            return {
                "type": "parse_error",
                "score": -1,
                "reasoning": f"JSON 解析失败: {str(e)[:100]}",
                "raw_response": response[:500]
            }

    def _format_follow_up(self, session: AgentSession, agent_response: Dict[str, Any]) -> Dict[str, Any]:
        """格式化追问响应"""
        current_dim = session.current_dimension
        dimension_names = {
            "core_value": "核心价值",
            "usage_scenario": "使用场景",
            "alias_preference": "别名偏好",
            "boundaries": "边界限制"
        }

        # 获取评分
        score = agent_response.get("score", 0)
        reasoning = agent_response.get("reasoning", "")

        # 计算进度（同一维度不增加进度）
        progress_percentage = int((session.current_dimension_idx / 4) * 100)

        return {
            "type": "follow_up",
            "current_dimension": current_dim,
            "dimension_name": dimension_names.get(current_dim, current_dim),
            "follow_up_question": agent_response.get("follow_up_question", "能再详细说明一下吗？"),
            "guidance": agent_response.get("guidance", ""),
            "examples": agent_response.get("examples", []),
            "recommended_options": agent_response.get("recommended_options", []),
            "score": score,
            "reasoning": reasoning,
            "progress": {
                "current": session.current_dimension_idx + 1,
                "total": 4,
                "percentage": progress_percentage
            }
        }

    async def _advance_dimension(self, session: AgentSession, agent_response: Dict[str, Any]) -> Dict[str, Any]:
        """进入下一个维度"""
        # 移动到下一个维度
        session.current_dimension_idx += 1

        # 获取评分
        score = agent_response.get("score", 95)
        reasoning = agent_response.get("reasoning", "")

        # 检查是否完成所有维度
        if session.current_dimension_idx >= len(DIMENSIONS):
            # 生成最终总结
            return await self._generate_final_summary(session)

        # 获取新维度
        new_dim = session.current_dimension
        dimension_names = {
            "core_value": "核心价值",
            "usage_scenario": "使用场景",
            "alias_preference": "别名偏好",
            "boundaries": "边界限制"
        }

        # 维度默认问题
        default_questions = {
            "core_value": "这个技能主要帮助用户解决什么问题？",
            "usage_scenario": "用户会在什么具体场景下使用这个技能？请描述一个典型的工作流程。",
            "alias_preference": "如果让你用3-5个字简短称呼这个技能的核心功能，你会怎么叫它？",
            "boundaries": "这个技能不应该做哪些事情？或者有哪些明确的限制？"
        }

        # 计算进度
        progress_percentage = int((session.current_dimension_idx / 4) * 100)

        return {
            "type": "next_dimension",
            "current_dimension": new_dim,
            "dimension_name": dimension_names.get(new_dim, new_dim),
            "question": agent_response.get("question") or default_questions.get(new_dim, ""),
            "guidance": agent_response.get("guidance") or DIMENSION_GUIDANCE.get(new_dim, ""),
            "examples": agent_response.get("examples", []),
            "score": score,
            "reasoning": reasoning,
            "progress": {
                "current": session.current_dimension_idx + 1,
                "total": 4,
                "percentage": progress_percentage
            }
        }

    def _format_summary(self, session: AgentSession, agent_response: Dict[str, Any]) -> Dict[str, Any]:
        """格式化总结响应"""
        # 从 Agent 响应中获取元数据
        metadata = agent_response.get("skill_metadata", {})

        # 如果没有元数据，生成默认的
        if not metadata:
            merged_answers = {}
            for dim, answers_list in session.answers.items():
                merged_answers[dim] = " ".join(answers_list)
            metadata = self._generate_metadata(merged_answers)

        session.metadata = metadata

        return {
            "type": "summary",
            "message": agent_response.get("message", "太好了！我已经收集了所有必要的信息。"),
            "skill_metadata": metadata,
            "progress": {
                "current": 4,
                "total": 4,
                "percentage": 100
            },
            "next_step": "请确认以上信息是否正确，或告诉我需要调整的地方。"
        }

    async def _generate_final_summary(self, session: AgentSession) -> Dict[str, Any]:
        """生成最终总结"""
        # 合并所有回答
        merged_answers = {}
        for dim, answers_list in session.answers.items():
            merged_answers[dim] = " ".join(answers_list)

        # 生成元数据
        metadata = self._generate_metadata(merged_answers)
        session.metadata = metadata

        return {
            "type": "summary",
            "message": "太好了！我已经收集了所有必要的信息。让我为您总结一下：",
            "skill_metadata": metadata,
            "progress": {
                "current": 4,
                "total": 4,
                "percentage": 100
            },
            "next_step": "请确认以上信息是否正确，或告诉我需要调整的地方。"
        }

    def _generate_metadata(self, answers: Dict[str, str]) -> Dict[str, Any]:
        """基于用户回答生成技能元数据"""
        core_value = answers.get("core_value", "")
        scenario = answers.get("usage_scenario", "")
        alias_pref = answers.get("alias_preference", "")
        boundaries = answers.get("boundaries", "")

        # 提取主别名
        main_alias = alias_pref.strip().split()[0] if alias_pref else "执行技能"

        # 生成技能名称
        skill_name = self._generate_skill_name(core_value, main_alias)

        # 生成上下文别名
        context_aliases = self._generate_context_aliases(main_alias, core_value)

        # 生成命令别名
        command_alias = self._generate_command_alias(main_alias, skill_name)

        # 生成 API 别名
        api_alias = skill_name.replace("-", "_")

        # 识别类别
        category = self._identify_category(core_value, scenario)

        # 识别目标用户
        target_users = self._identify_target_users(scenario)

        # 识别合规要求
        compliance_reqs = self._identify_compliance_requirements(boundaries)

        return {
            "skill_name": skill_name,
            "core_value": core_value,
            "usage_scenario": scenario,
            "main_alias": main_alias,
            "context_aliases": context_aliases,
            "command_alias": command_alias,
            "api_alias": api_alias,
            "boundaries": boundaries,
            "category": category,
            "target_users": target_users,
            "compliance_requirements": compliance_reqs,
            "suggested_capabilities": self._suggest_capabilities(core_value, scenario)
        }

    def _generate_skill_name(self, core_value: str, main_alias: str) -> str:
        """生成技能名称（kebab-case）"""
        # 关键词映射
        mappings = {
            "sop": "sop",
            "合规": "compliance",
            "审查": "review",
            "qa": "qa",
            "图片": "image",
            "优化": "optimizer",
            "电商": "ecommerce",
            "数据": "data",
            "分析": "analyzer",
            "临床试验": "clinical-trials",
            "报告": "report",
            "生成": "generator",
        }

        words = []
        for key, value in mappings.items():
            if key in core_value.lower():
                words.append(value)

        if len(words) >= 2:
            return "-".join(words[:2])
        elif main_alias:
            # 从主别名生成
            return re.sub(r'[^\w\u4e00-\u9fa5]+', '-', main_alias.lower()).strip('-')

        return "custom-skill"

    def _generate_context_aliases(self, main_alias: str, core_value: str) -> List[str]:
        """生成上下文别名"""
        aliases = [main_alias]

        # 基于主别名生成变体
        if len(main_alias) > 2:
            aliases.append(main_alias[:2])  # 短版本

        # 基于核心价值添加相关词
        if "检查" in core_value or "审查" in core_value:
            aliases.append("检查")
            aliases.append("验证")
        elif "优化" in core_value:
            aliases.append("处理")
            aliases.append("调整")

        return list(set(aliases))  # 去重

    def _generate_command_alias(self, main_alias: str, skill_name: str) -> str:
        """生成命令别名"""
        # 预定义映射
        command_map = {
            "审查SOP": "sop",
            "检查合规": "check",
            "优化图片": "img",
            "分析数据": "data",
        }

        if main_alias in command_map:
            return command_map[main_alias]

        # 从技能名称生成
        return skill_name.split("-")[0][:4] if "-" in skill_name else main_alias[:3]

    def _identify_category(self, core_value: str, scenario: str) -> str:
        """识别技能类别"""
        text = (core_value + " " + scenario).lower()

        if any(kw in text for kw in ["sop", "合规", "审查", "qa", "gxp"]):
            return "compliance"
        elif any(kw in text for kw in ["图片", "电商", "产品"]):
            return "ecommerce"
        elif any(kw in text for kw in ["临床", "试验", "nct", "数据"]):
            return "clinical"
        elif any(kw in text for kw in ["文档", "pdf", "word"]):
            return "document"
        else:
            return "general"

    def _identify_target_users(self, scenario: str) -> List[str]:
        """识别目标用户"""
        users = []
        text = scenario.lower()

        if any(kw in text for kw in ["qa", "质量", "合规"]):
            users.append("QA专员")
        if any(kw in text for kw in ["运营", "电商", "卖家"]):
            users.append("电商运营")
        if any(kw in text for kw in ["临床", "研究员", "cra"]):
            users.append("临床研究员")
        if any(kw in text for kw in ["销售", "客户"]):
            users.append("销售人员")

        return users if users else ["通用用户"]

    def _identify_compliance_requirements(self, boundaries: str) -> List[str]:
        """识别合规要求"""
        reqs = []
        text = boundaries.lower()

        if "21 cfr" in text or "part 11" in text:
            reqs.append("21 CFR Part 11")
        if "gxp" in text:
            reqs.append("GxP")
        if "个人身份" in text or "pii" in text:
            reqs.append("数据隐私保护")
        if "存储" in text or "保留" in text:
            reqs.append("数据保留策略")

        return reqs

    def _suggest_capabilities(self, core_value: str, scenario: str) -> List[Dict[str, Any]]:
        """建议能力列表"""
        capabilities = []
        text = (core_value + " " + scenario).lower()

        if any(kw in text for kw in ["sop", "合规", "审查"]):
            capabilities.extend([
                {"id": "parse", "name": "文档解析", "complexity": "medium"},
                {"id": "check", "name": "合规检查", "complexity": "low"},
                {"id": "report", "name": "生成报告", "complexity": "medium"},
            ])
        elif any(kw in text for kw in ["图片", "优化"]):
            capabilities.extend([
                {"id": "remove-bg", "name": "去背景", "complexity": "medium"},
                {"id": "resize", "name": "尺寸调整", "complexity": "low"},
                {"id": "format", "name": "格式转换", "complexity": "low"},
            ])
        elif any(kw in text for kw in ["数据", "分析"]):
            capabilities.extend([
                {"id": "collect", "name": "数据采集", "complexity": "medium"},
                {"id": "analyze", "name": "数据分析", "complexity": "high"},
                {"id": "visualize", "name": "可视化", "complexity": "medium"},
            ])

        if not capabilities:
            capabilities = [
                {"id": "main", "name": "主功能", "complexity": "medium"},
            ]

        return capabilities

    async def end_session(self, session_id: str, user_id: int) -> Dict[str, Any]:
        """结束会话"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if session.user_id != user_id:
            raise PermissionError(f"User {user_id} not authorized for session {session_id}")

        # 获取最终元数据
        metadata = session.metadata if session.metadata else self._generate_metadata(
            {dim: " ".join(ans) for dim, ans in session.answers.items()}
        )

        # 删除会话
        del self.sessions[session_id]

        return {
            "message": "Session ended",
            "skill_metadata": metadata,
            "answers": {dim: " ".join(ans) for dim, ans in session.answers.items()}
        }


# 全局服务实例
_skill_creator_agent_service: Optional[SkillCreatorAgentService] = None


def get_skill_creator_agent_service() -> SkillCreatorAgentService:
    """获取 Skill Creator Agent 服务实例"""
    global _skill_creator_agent_service
    if _skill_creator_agent_service is None:
        _skill_creator_agent_service = SkillCreatorAgentService()
    return _skill_creator_agent_service
