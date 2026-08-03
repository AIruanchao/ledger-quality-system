"""
数据质量门禁 D2-D10 — 从 test_taizhang_suite.py 提取的纯逻辑函数。
可被 unit test 和 E2E test 共同调用。
"""
from __future__ import annotations

import re
from typing import Any

from ..validators.schema import BAD_CONFIG_VALUES, ContractStatus


def check_config_contamination(records: list[dict[str, str]]) -> list[str]:
    """
    D2/D5 门禁 (PIT-TZ-002): 产品型号/产品名称/对方公司字段不能串入配置信息。
    Returns: 违规项列表（空=PASS）。
    """
    violations = []
    for item in records:
        for field, val in item.items():
            if field.startswith("_"):
                continue
            val_str = str(val).strip()
            # 直接匹配已知配置值
            if val_str.lower() in BAD_CONFIG_VALUES and field not in ("单位", "台数"):
                violations.append(f"{field}={val_str}")
            # 产品相关字段的纯数字+符号模式
            if field in ("产品型号", "产品名称", "对方公司"):
                if re.match(r"^[\d+\-/\s×]+$", val_str) and len(val_str) <= 10:
                    violations.append(f"{field}={val_str}")
    return violations


def check_null_rate(
    records: list[dict[str, str]],
    field: str,
    threshold: float = 0.1,
) -> tuple[bool, float]:
    """
    D4 门禁 (PIT-TZ-003/010): 活跃合同空值率 < threshold。
    排除草稿和已终止状态的合同。
    """
    active = [
        r for r in records
        if r.get("合同状态", "") not in (ContractStatus.DRAFT.value, "草稿", ContractStatus.TERMINATED.value)
    ]
    if not active:
        return True, 0.0
    total = len(active)
    null_count = sum(
        1 for r in active
        if not str(r.get(field, "")).strip() or str(r.get(field, "")) in ("None", "0")
    )
    rate = null_count / total
    return rate < threshold, rate


def check_amount_logic(records: list[dict[str, str]]) -> list[str]:
    """
    D6 门禁 (PIT-TZ-004): 金额 = 单价 × 台数（偏差<1%）。
    Returns: 错误项列表（空=PASS）。
    """
    errors = []
    for item in records:
        try:
            amount = float(item.get("合同金额", 0))
            price = float(item.get("单价", 0))
            qty = float(item.get("台数", 0))
            cno = item.get("合同编号", "?")
            if price > 0 and qty > 0 and amount > 0:
                expected = price * qty
                if abs(amount - expected) / max(expected, 1) > 0.01:
                    errors.append(f"{cno}: {amount}≠{price}×{qty}={expected:.0f}")
        except (ValueError, TypeError):
            continue
    return errors


def check_date_format(date_str: str) -> bool:
    """
    D8 门禁 (PIT-TZ-001): 日期应该是 YYYY-MM-DD 格式（10字符含-），
    不是毫秒时间戳（13位纯数字）。
    """
    if not date_str:
        return False
    # 毫秒时间戳检测
    if date_str.isdigit() and len(date_str) >= 13:
        return False
    return len(date_str) == 10 and "-" in date_str


def check_null_safety(items: list[Any] | None) -> list[Any]:
    """
    PIT-TZ-008: 空表返回 items=None → 必须返回空列表而非崩溃。
    """
    return items if items is not None else []


def check_garbage_threshold(feishu_count: int, source_count: int) -> bool:
    """
    D-Garbage 门禁 (PIT-TZ-006): 飞书条数 ≤ 源系统条数 × 2。
    Returns: True = 无垃圾膨胀。
    """
    threshold = max(source_count * 2, 10)
    return feishu_count <= threshold
