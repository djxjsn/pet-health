"""
DEV-009 数据安全与隐私模块 单元测试

测试加密服务、脱敏服务、RBAC权限控制、审计日志
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


# ========== 加密服务测试 ==========

class TestEncryptionService:
    """加密服务测试"""

    @pytest.fixture
    def service(self):
        from src.core.encryption import EncryptionService
        return EncryptionService(master_key="test-master-key-for-unit-tests")

    def test_encrypt_decrypt_basic(self, service):
        """测试基本加密解密"""
        plaintext = "这是一条敏感信息"
        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)
        
        assert decrypted == plaintext
        assert encrypted != plaintext

    def test_encrypt_produces_different_ciphertext(self, service):
        """测试相同明文产生不同密文（随机nonce）"""
        plaintext = "相同的数据"
        encrypted1 = service.encrypt(plaintext)
        encrypted2 = service.encrypt(plaintext)
        
        assert encrypted1 != encrypted2

    def test_encrypt_empty_string(self, service):
        """测试空字符串加密"""
        assert service.encrypt("") == ""
        assert service.decrypt("") == ""

    def test_encrypt_field_with_name(self, service):
        """测试带字段名的加密"""
        value = "13800138000"
        encrypted = service.encrypt_field(value, "phone")
        decrypted = service.decrypt_field(encrypted, "phone")
        
        assert decrypted == value

    def test_decrypt_wrong_field_name_fails(self, service):
        """测试用错误字段名解密失败"""
        value = "敏感数据"
        encrypted = service.encrypt_field(value, "field_a")
        
        with pytest.raises(ValueError):
            service.decrypt_field(encrypted, "field_b")

    def test_decrypt_tampered_data_fails(self, service):
        """测试篡改数据解密失败"""
        import base64
        encrypted = service.encrypt("原始数据")
        
        tampered = encrypted[:-5] + "XXXXX"
        with pytest.raises(ValueError):
            service.decrypt(tampered)

    def test_generate_key(self, service):
        """测试密钥生成"""
        key = service.generate_key()
        
        assert isinstance(key, str)
        assert len(key) > 0

    def test_hash_data(self, service):
        """测试数据哈希"""
        data = "test_data"
        hash1 = service.hash_data(data)
        hash2 = service.hash_data(data)
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex长度

    def test_hash_data_different_inputs(self, service):
        """测试不同输入产生不同哈希"""
        hash1 = service.hash_data("input1")
        hash2 = service.hash_data("input2")
        
        assert hash1 != hash2

    def test_chinese_text_encryption(self, service):
        """测试中文文本加密"""
        plaintext = "宠物健康助手，包含中文和emoji🐾"
        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)
        
        assert decrypted == plaintext

    def test_long_text_encryption(self, service):
        """测试长文本加密"""
        plaintext = "A" * 10000
        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)
        
        assert decrypted == plaintext


# ========== 脱敏服务测试 ==========

class TestDataMasker:
    """脱敏服务测试"""

    @pytest.fixture
    def masker(self):
        from src.core.data_masker import DataMasker
        return DataMasker()

    def test_mask_phone(self, masker):
        """测试手机号脱敏"""
        assert masker.mask_phone("13800138000") == "138****8000"

    def test_mask_phone_short(self, masker):
        """测试短手机号"""
        result = masker.mask_phone("138")
        assert result is not None

    def test_mask_email(self, masker):
        """测试邮箱脱敏"""
        result = masker.mask_email("user@example.com")
        assert "@" in result
        assert "example.com" in result
        assert result != "user@example.com"

    def test_mask_email_short_local(self, masker):
        """测试短本地部分邮箱"""
        result = masker.mask_email("a@test.com")
        assert "@" in result

    def test_mask_id_card(self, masker):
        """测试身份证脱敏"""
        result = masker.mask_id_card("110101199001011234")
        assert result.startswith("110")
        assert result.endswith("1234")
        assert "****" in result or "*" in result

    def test_mask_name_two_chars(self, masker):
        """测试两字姓名脱敏"""
        assert masker.mask_name("张三") == "张*"

    def test_mask_name_three_chars(self, masker):
        """测试三字姓名脱敏"""
        result = masker.mask_name("张三丰")
        assert result[0] == "张"
        assert result[-1] == "丰"
        assert "*" in result

    def test_mask_address(self, masker):
        """测试地址脱敏"""
        result = masker.mask_address("北京市朝阳区某某路123号")
        assert result.startswith("北京市朝阳区")
        assert "*" in result

    def test_mask_bank_card(self, masker):
        """测试银行卡脱敏"""
        result = masker.mask_bank_card("6222021234567890123")
        assert "123" in result

    def test_mask_password(self, masker):
        """测试密码脱敏"""
        assert masker.mask_password("MySecret123!") == "******"

    def test_mask_ip_address(self, masker):
        """测试IP地址脱敏"""
        result = masker.mask_ip_address("192.168.1.100")
        assert result == "192.168.*.*"

    def test_mask_custom(self, masker):
        """测试自定义脱敏"""
        result = masker.mask_custom("ABCDEFGHIJ", visible_prefix=3, visible_suffix=2)
        assert result.startswith("ABC")
        assert result.endswith("IJ")
        assert "*" in result

    def test_mask_dict(self, masker):
        """测试字典批量脱敏"""
        from src.core.data_masker import MaskStrategy
        
        data = {
            "name": "张三",
            "phone": "13800138000",
            "email": "test@example.com",
            "age": 25
        }
        
        rules = {
            "name": MaskStrategy.NAME,
            "phone": MaskStrategy.PHONE,
            "email": MaskStrategy.EMAIL,
        }
        
        result = masker.mask_dict(data, rules)
        
        assert result["name"] != "张三"
        assert result["phone"] != "13800138000"
        assert result["email"] != "test@example.com"
        assert result["age"] == 25

    def test_mask_dict_with_exclude(self, masker):
        """测试带排除字段的字典脱敏"""
        from src.core.data_masker import MaskStrategy
        
        data = {"phone": "13800138000", "secret": "hidden", "name": "张三"}
        rules = {"phone": MaskStrategy.PHONE, "secret": MaskStrategy.PASSWORD, "name": MaskStrategy.NAME}
        
        result = masker.mask_dict(data, rules, exclude_fields=["secret"])
        
        assert "phone" in result
        assert "name" in result
        assert "secret" not in result

    def test_mask_general_entry(self, masker):
        """测试通用脱敏入口"""
        from src.core.data_masker import MaskStrategy
        
        result = masker.mask("13800138000", MaskStrategy.PHONE)
        assert result == "138****8000"


# ========== RBAC 测试 ==========

class TestRBAC:
    """RBAC权限控制测试"""

    @pytest.fixture
    def service(self):
        from src.core.rbac import RoleService
        return RoleService()

    def test_super_admin_has_all_permissions(self, service):
        """测试超级管理员拥有所有权限"""
        from src.core.rbac import Role, Permission
        
        perms = service.get_role_permissions(Role.SUPER_ADMIN)
        assert len(perms) == len(Permission)

    def test_user_has_basic_permissions(self, service):
        """测试普通用户拥有基本权限"""
        from src.core.rbac import Role, Permission
        
        perms = service.get_role_permissions(Role.USER)
        assert Permission.PET_READ in perms
        assert Permission.HEALTH_READ in perms
        assert Permission.ADMIN_PANEL not in perms

    def test_guest_has_minimal_permissions(self, service):
        """测试访客拥有最少权限"""
        from src.core.rbac import Role, Permission
        
        perms = service.get_role_permissions(Role.GUEST)
        assert Permission.HEALTH_READ in perms
        assert Permission.PET_WRITE not in perms

    def test_has_permission(self, service):
        """测试权限检查"""
        from src.core.rbac import Role, Permission
        
        assert service.has_permission(Role.ADMIN, Permission.USER_READ) == True
        assert service.has_permission(Role.USER, Permission.ADMIN_PANEL) == False

    def test_has_any_permission(self, service):
        """测试任一权限检查"""
        from src.core.rbac import Role, Permission
        
        assert service.has_any_permission(Role.USER, [Permission.ADMIN_PANEL, Permission.PET_READ]) == True
        assert service.has_any_permission(Role.GUEST, [Permission.ADMIN_PANEL, Permission.PET_WRITE]) == False

    def test_has_all_permissions(self, service):
        """测试全部权限检查"""
        from src.core.rbac import Role, Permission
        
        assert service.has_all_permissions(Role.ADMIN, [Permission.USER_READ, Permission.PET_READ]) == True
        assert service.has_all_permissions(Role.USER, [Permission.USER_READ, Permission.ADMIN_PANEL]) == False

    def test_get_role_from_superuser(self, service):
        """测试从超级用户获取角色"""
        from src.core.rbac import Role
        
        user = {"is_superuser": True}
        role = service.get_role_from_user(user)
        assert role == Role.SUPER_ADMIN

    def test_get_role_from_normal_user(self, service):
        """测试从普通用户获取角色"""
        from src.core.rbac import Role
        
        user = {"is_superuser": False, "role": "user"}
        role = service.get_role_from_user(user)
        assert role == Role.USER

    def test_list_roles(self, service):
        """测试列出角色"""
        roles = service.list_roles()
        
        assert len(roles) == 5
        role_names = [r["role"] for r in roles]
        assert "super_admin" in role_names
        assert "admin" in role_names
        assert "user" in role_names
        assert "guest" in role_names

    def test_role_hierarchy(self, service):
        """测试角色层级（权限递减）"""
        from src.core.rbac import Role
        
        sa_perms = len(service.get_role_permissions(Role.SUPER_ADMIN))
        admin_perms = len(service.get_role_permissions(Role.ADMIN))
        vet_perms = len(service.get_role_permissions(Role.VETERINARIAN))
        user_perms = len(service.get_role_permissions(Role.USER))
        guest_perms = len(service.get_role_permissions(Role.GUEST))
        
        assert sa_perms > admin_perms > vet_perms > user_perms > guest_perms


class TestSecurityContext:
    """安全上下文测试"""

    def test_context_creation(self):
        """测试上下文创建"""
        from src.core.rbac import SecurityContext, Role, Permission
        
        ctx = SecurityContext(
            user_id="user_001",
            role=Role.USER,
            permissions={Permission.PET_READ, Permission.HEALTH_READ}
        )
        
        assert ctx.user_id == "user_001"
        assert ctx.role == Role.USER

    def test_has_permission(self):
        """测试权限检查"""
        from src.core.rbac import SecurityContext, Role, Permission
        
        ctx = SecurityContext(
            user_id="user_001",
            role=Role.USER,
            permissions={Permission.PET_READ}
        )
        
        assert ctx.has_permission(Permission.PET_READ) == True
        assert ctx.has_permission(Permission.ADMIN_PANEL) == False

    def test_is_admin(self):
        """测试管理员判断"""
        from src.core.rbac import SecurityContext, Role, Permission
        
        admin_ctx = SecurityContext(user_id="a", role=Role.ADMIN, permissions=set())
        user_ctx = SecurityContext(user_id="b", role=Role.USER, permissions=set())
        
        assert admin_ctx.is_admin() == True
        assert user_ctx.is_admin() == False

    def test_to_dict(self):
        """测试序列化"""
        from src.core.rbac import SecurityContext, Role, Permission
        
        ctx = SecurityContext(
            user_id="user_001",
            role=Role.USER,
            permissions={Permission.PET_READ}
        )
        
        d = ctx.to_dict()
        assert d["user_id"] == "user_001"
        assert d["role"] == "user"
        assert d["is_admin"] == False


# ========== 审计日志测试 ==========

class TestAuditLogService:
    """审计日志服务测试"""

    @pytest.fixture
    def service(self):
        with patch("src.core.audit.MongoClient") as mock_client:
            mock_collection = MagicMock()
            mock_db = MagicMock()
            mock_db.__getitem__.return_value = mock_collection
            mock_client.__getitem__.return_value = mock_db
            
            from src.core.audit import AuditLogService
            svc = AuditLogService()
            svc._collection = mock_collection
            return svc

    def test_log_basic(self, service):
        """测试基本日志记录"""
        from src.core.audit import AuditAction
        
        result = service.log(
            action=AuditAction.LOGIN,
            user_id="user_001",
        )
        
        assert result["action"] == "auth:login"
        assert result["user_id"] == "user_001"
        assert "log_id" in result
        service._collection.insert_one.assert_called_once()

    def test_log_auth_event(self, service):
        """测试认证事件记录"""
        from src.core.audit import AuditAction
        
        result = service.log_auth_event(
            action=AuditAction.LOGIN,
            user_id="user_001",
            success=True,
            ip_address="192.168.1.1"
        )
        
        assert result["details"]["success"] == True
        assert result["ip_address"] == "192.168.1.1"

    def test_log_data_change(self, service):
        """测试数据变更记录"""
        from src.core.audit import AuditAction
        
        result = service.log_data_change(
            action=AuditAction.PET_UPDATE,
            user_id="user_001",
            resource_type="pet",
            resource_id="pet_001",
            old_value={"name": "小白"},
            new_value={"name": "小黑"},
        )
        
        assert result["old_value"] == {"name": "小白"}
        assert result["new_value"] == {"name": "小黑"}

    def test_log_security_event(self, service):
        """测试安全事件记录"""
        from src.core.audit import AuditAction, AuditLogLevel
        
        result = service.log_security_event(
            action=AuditAction.PERMISSION_CHANGE,
            user_id="admin_001",
            details={"target_user": "user_002"}
        )
        
        assert result["level"] == AuditLogLevel.CRITICAL.value

    def test_query_logs(self, service):
        """测试日志查询"""
        service._collection.count_documents.return_value = 5
        service._collection.find.return_value.sort.return_value.skip.return_value.limit.return_value = iter([])
        
        result = service.query_logs(user_id="user_001", skip=0, limit=10)
        
        assert result["total"] == 5
        assert "logs" in result

    def test_get_security_events(self, service):
        """测试获取安全事件"""
        service._collection.find.return_value.sort.return_value.limit.return_value = iter([])
        
        result = service.get_security_events(hours=24)
        
        assert isinstance(result, list)

    def test_get_user_activity_summary(self, service):
        """测试用户活动摘要"""
        service._collection.aggregate.return_value = iter([
            {"_id": "auth:login", "count": 10, "last_occurrence": datetime.utcnow()}
        ])
        
        result = service.get_user_activity_summary("user_001", days=30)
        
        assert result["user_id"] == "user_001"
        assert result["total_actions"] == 10
