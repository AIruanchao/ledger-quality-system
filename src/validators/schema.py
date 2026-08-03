"""
Pydantic 数据契约 — 台账核心实体的类型约束和业务规则。
每个 PIT-TZ 坑点对应一条验证规则。
"""
from __future__ import annotations

import re
from enum import Enum

from pydantic import BaseModel, Field, model_validator


class ContractStatus(str, Enum):
    """合同状态枚举。"""
    DRAFT = "📝 草稿"
    APPROVED = "✅ 已批准"
    TERMINATED = "⚪ 已终止"
    COMPLETED = "🏁 已完成"


# PIT-TZ-002: 产品型号不能串入的配置信息
BAD_CONFIG_VALUES = frozenset({
    "12+256", "8+128", "6+64", "4+64", "16+512",
    "1tb", "512g", "256g", "128g",
})


class ContractRecord(BaseModel):
    """
    合同台账记录的数据契约。
    包含 PIT-TZ-001~004, 010 的验证规则。
    """
    合同编号: str = Field(..., min_length=1, description="合同编号，非空")
    对方公司: str = Field(..., min_length=1, description="对方公司，非空")
    合同金额: float = Field(..., ge=0, description="合同金额≥0")
    合同状态: str = Field(default="", description="合同状态")
    台数: int | None = Field(None, ge=0, description="台数≥0")
    单价: float | None = Field(None, ge=0, description="单价≥0")
    到期日期: str | None = Field(None, description="到期日期")
    产品型号: str | None = Field(None, description="产品型号")

    @model_validator(mode="after")
    def validate_amount_logic(self) -> ContractRecord:
        """
        PIT-TZ-004: 金额 = 单价 × 台数（偏差<1%）。
        仅在单价和台数都有值且>0时检查。
        """
        if self.台数 is not None and self.单价 is not None and self.台数 > 0 and self.单价 > 0:
            expected = self.台数 * self.单价
            if abs(self.合同金额 - expected) / max(expected, 1) > 0.01:
                raise ValueError(
                    f"PIT-TZ-004: 金额{self.合同金额} ≠ 单价{self.单价}×台数{self.台数}={expected}"
                )
        return self

    @model_validator(mode="after")
    def validate_no_config_contamination(self) -> ContractRecord:
        """
        PIT-TZ-002: 产品型号字段不能串入存储配置信息（如"12+256"）。
        """
        if self.产品型号:
            val = self.产品型号.strip().lower()
            if val in BAD_CONFIG_VALUES:
                raise ValueError(f"PIT-TZ-002: 产品型号'{self.产品型号}'是配置信息非产品名")
            # 纯数字+符号组合也可能是配置串入
            if re.match(r"^[\d+\-/\s×]+$", self.产品型号.strip()) and len(self.产品型号) <= 10:
                raise ValueError(f"PIT-TZ-002: 产品型号'{self.产品型号}'疑似配置串入")
        return self

    @property
    def is_active(self) -> bool:
        """
        PIT-TZ-003/010: 判断合同是否为活跃状态（排除草稿和已终止）。
        空值检查只对活跃合同生效。
        """
        return self.合同状态 not in (ContractStatus.DRAFT.value, "草稿", ContractStatus.TERMINATED.value)


class PaymentRecord(BaseModel):
    """回款单记录的数据契约。"""
    银行凭证号: str = Field(..., min_length=1, description="幂等key，非空")
    合同编号: str = Field(default="", description="关联合同编号")
    回款金额: float = Field(..., ge=0, description="回款金额≥0")


def validate_null_rate(records: list[dict[str, str]], field: str, threshold: float = 0.1) -> tuple[bool, float]:
    """
    PIT-TZ-003: 空值率检查。只对活跃合同检查，排除草稿/已终止。

    Returns:
        (pass_bool, null_rate)
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


def check_idempotency_field(field_def: dict) -> bool:
    """
    PIT-TZ-009: 幂等key字段（银行凭证号）必须是可写类型（type=1 Text），
    不能是 type=1005（AutoNumber 自动编号，API写入被忽略）。
    """
    return field_def.get("type") == 1
