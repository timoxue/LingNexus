from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def calculate_molecular_weight(smiles: str) -> float:
    """计算分子量（骨架）。

    后续可接入 RDKit 等化学库。
    """
    logger.info("Calculating molecular weight", extra={"smiles": smiles})
    # TODO: 接入真实化学信息学库
    return 0.0
