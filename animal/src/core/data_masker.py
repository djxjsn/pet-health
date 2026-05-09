"""
敏感数据脱敏服务

提供多种脱敏策略，用于：
- API 响应中隐藏敏感信息
- 日志中安全输出
- 数据导出时保护隐私
"""
import re
import logging
from typing import Dict, Any, List, Optional, Callable
from enum import Enum

logger = logging.getLogger(__name__)


class MaskStrategy(Enum):
    """脱敏策略"""
    PHONE = "phone"
    EMAIL = "email"
    ID_CARD = "id_card"
    NAME = "name"
    ADDRESS = "address"
    BANK_CARD = "bank_card"
    PASSWORD = "password"
    IP_ADDRESS = "ip_address"
    CUSTOM = "custom"


class DataMasker:
    """
    数据脱敏服务
    
    支持多种内置脱敏策略和自定义规则
    """

    DEFAULT_MASK_CHAR = "*"

    def mask_phone(self, phone: str) -> str:
        """
        手机号脱敏：138****1234
        """
        if not phone or len(phone) < 7:
            return phone
        
        phone = phone.strip()
        if re.match(r'^\d{11}$', phone):
            return f"{phone[:3]}****{phone[7:]}"
        return phone[:3] + "****" + phone[-4:] if len(phone) >= 7 else phone

    def mask_email(self, email: str) -> str:
        """
        邮箱脱敏：u***@example.com
        """
        if not email or "@" not in email:
            return email
        
        local, domain = email.split("@", 1)
        if len(local) <= 1:
            masked_local = self.DEFAULT_MASK_CHAR
        elif len(local) <= 3:
            masked_local = local[0] + self.DEFAULT_MASK_CHAR * (len(local) - 1)
        else:
            masked_local = local[0] + self.DEFAULT_MASK_CHAR * (len(local) - 2) + local[-1]
        
        return f"{masked_local}@{domain}"

    def mask_id_card(self, id_card: str) -> str:
        """
        身份证脱敏：110***********1234
        """
        if not id_card or len(id_card) < 8:
            return id_card
        
        return id_card[:3] + self.DEFAULT_MASK_CHAR * (len(id_card) - 7) + id_card[-4:]

    def mask_name(self, name: str) -> str:
        """
        姓名脱敏：张*、张*明
        """
        if not name:
            return name
        
        if len(name) == 1:
            return name
        elif len(name) == 2:
            return name[0] + self.DEFAULT_MASK_CHAR
        else:
            return name[0] + self.DEFAULT_MASK_CHAR * (len(name) - 2) + name[-1]

    def mask_address(self, address: str) -> str:
        """
        地址脱敏：北京市朝阳区****
        """
        if not address or len(address) <= 6:
            return address
        
        return address[:6] + self.DEFAULT_MASK_CHAR * (len(address) - 6)

    def mask_bank_card(self, card_no: str) -> str:
        """
        银行卡脱敏：**** **** **** 1234
        """
        if not card_no:
            return card_no
        
        digits = re.sub(r'\D', '', card_no)
        if len(digits) < 4:
            return self.DEFAULT_MASK_CHAR * len(digits)
        
        last_four = digits[-4:]
        masked = self.DEFAULT_MASK_CHAR * (len(digits) - 4)
        full = masked + last_four
        
        groups = [full[i:i+4] for i in range(0, len(full), 4)]
        return " ".join(groups)

    def mask_password(self, password: str) -> str:
        """
        密码脱敏：始终返回 ******
        """
        return self.DEFAULT_MASK_CHAR * 6

    def mask_ip_address(self, ip: str) -> str:
        """
        IP地址脱敏：192.168.*.*
        """
        if not ip:
            return ip
        
        parts = ip.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.*.*"
        return ip

    def mask_custom(self, value: str, visible_prefix: int = 2, visible_suffix: int = 2) -> str:
        """
        自定义脱敏：保留前后N位
        """
        if not value:
            return value
        
        if len(value) <= visible_prefix + visible_suffix:
            return self.DEFAULT_MASK_CHAR * len(value)
        
        prefix = value[:visible_prefix]
        suffix = value[-visible_suffix:] if visible_suffix > 0 else ""
        mask_length = len(value) - visible_prefix - visible_suffix
        
        return prefix + self.DEFAULT_MASK_CHAR * mask_length + suffix

    def mask(self, value: str, strategy: MaskStrategy, **kwargs) -> str:
        """
        通用脱敏入口
        
        Args:
            value: 待脱敏值
            strategy: 脱敏策略
            **kwargs: 策略参数
            
        Returns:
            脱敏后的值
        """
        strategy_map = {
            MaskStrategy.PHONE: self.mask_phone,
            MaskStrategy.EMAIL: self.mask_email,
            MaskStrategy.ID_CARD: self.mask_id_card,
            MaskStrategy.NAME: self.mask_name,
            MaskStrategy.ADDRESS: self.mask_address,
            MaskStrategy.BANK_CARD: self.mask_bank_card,
            MaskStrategy.PASSWORD: self.mask_password,
            MaskStrategy.IP_ADDRESS: self.mask_ip_address,
            MaskStrategy.CUSTOM: self.mask_custom,
        }
        
        handler = strategy_map.get(strategy)
        if not handler:
            logger.warning(f"未知脱敏策略: {strategy}")
            return value
        
        try:
            if strategy == MaskStrategy.CUSTOM:
                return handler(value, **kwargs)
            return handler(value)
        except Exception as e:
            logger.error(f"脱敏处理异常: {e}")
            return self.DEFAULT_MASK_CHAR * len(value) if value else value

    def mask_dict(
        self,
        data: Dict[str, Any],
        field_rules: Dict[str, MaskStrategy],
        exclude_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        对字典数据进行批量脱敏
        
        Args:
            data: 原始数据字典
            field_rules: 字段名 -> 脱敏策略映射
            exclude_fields: 需要排除的字段列表
            
        Returns:
            脱敏后的数据字典
        """
        exclude_fields = exclude_fields or []
        result = {}
        
        for key, value in data.items():
            if key in exclude_fields:
                continue
            
            if key in field_rules and isinstance(value, str):
                result[key] = self.mask(value, field_rules[key])
            else:
                result[key] = value
        
        return result

    def mask_nested_dict(
        self,
        data: Dict[str, Any],
        field_rules: Dict[str, MaskStrategy],
        exclude_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        对嵌套字典进行深度脱敏
        """
        import copy
        result = copy.deepcopy(data)
        exclude_fields = exclude_fields or []
        
        def _mask_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in exclude_fields:
                        continue
                    if key in field_rules and isinstance(value, str):
                        obj[key] = self.mask(value, field_rules[key])
                    elif isinstance(value, (dict, list)):
                        _mask_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, (dict, list)):
                        _mask_recursive(item)
        
        _mask_recursive(result)
        return result


# 预定义的常用脱敏规则
DEFAULT_USER_MASK_RULES = {
    "phone": MaskStrategy.PHONE,
    "email": MaskStrategy.EMAIL,
    "password": MaskStrategy.PASSWORD,
    "password_hash": MaskStrategy.PASSWORD,
    "id_card": MaskStrategy.ID_CARD,
    "real_name": MaskStrategy.NAME,
    "address": MaskStrategy.ADDRESS,
}

DEFAULT_PET_MASK_RULES = {
    "owner_phone": MaskStrategy.PHONE,
    "owner_email": MaskStrategy.EMAIL,
    "owner_address": MaskStrategy.ADDRESS,
}


def get_data_masker() -> DataMasker:
    """获取脱敏服务实例"""
    return DataMasker()
