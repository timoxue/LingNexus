from dataclasses import dataclass
from typing import Dict


@dataclass
class ESIndexConfig:
    """ES 索引配置骨架。"""

    name: str
    mapping: Dict
    settings: Dict


# 示例：后续可以在这里集中定义医药相关索引
CLINICAL_TRIAL_INDEX = ESIndexConfig(
    name="clinical_trials",
    mapping={},  # TODO: 补充 mapping
    settings={},  # TODO: 补充 settings
)
