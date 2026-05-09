"""
数据加密服务

提供 AES-256-GCM 对称加密/解密功能，用于：
- 敏感字段加密存储（手机号、邮箱、身份证等）
- 数据传输加密
- 密钥管理
"""
import base64
import os
import hashlib
import logging
from typing import Optional, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidTag

from src.core.config import get_settings

logger = logging.getLogger(__name__)


class EncryptionService:
    """
    AES-256-GCM 加密服务
    
    特性：
    - 使用 AES-256-GCM 认证加密
    - 每次加密生成随机 nonce，防止密文分析
    - 支持 PBKDF2 密钥派生
    - 自动 Base64 编码存储
    """

    NONCE_SIZE = 12
    KEY_SIZE = 32
    TAG_SIZE = 16
    KDF_ITERATIONS = 100000

    def __init__(self, master_key: Optional[str] = None):
        settings = get_settings()
        self._master_key = master_key or settings.SECRET_KEY
        self._derived_key = self._derive_key(self._master_key)

    def encrypt(self, plaintext: str, associated_data: Optional[bytes] = None) -> str:
        """
        加密字符串
        
        Args:
            plaintext: 明文字符串
            associated_data: 关联数据（用于认证但不加密）
            
        Returns:
            Base64编码的密文（nonce + ciphertext + tag）
        """
        if not plaintext:
            return ""
        
        nonce = os.urandom(self.NONCE_SIZE)
        aesgcm = AESGCM(self._derived_key)
        
        ciphertext = aesgcm.encrypt(
            nonce=nonce,
            data=plaintext.encode("utf-8"),
            associated_data=associated_data
        )
        
        encrypted_data = nonce + ciphertext
        return base64.b64encode(encrypted_data).decode("ascii")

    def decrypt(self, encrypted_text: str, associated_data: Optional[bytes] = None) -> str:
        """
        解密字符串
        
        Args:
            encrypted_text: Base64编码的密文
            associated_data: 关联数据（必须与加密时一致）
            
        Returns:
            解密后的明文字符串
        """
        if not encrypted_text:
            return ""
        
        try:
            encrypted_data = base64.b64decode(encrypted_text)
            
            nonce = encrypted_data[:self.NONCE_SIZE]
            ciphertext = encrypted_data[self.NONCE_SIZE:]
            
            aesgcm = AESGCM(self._derived_key)
            plaintext = aesgcm.decrypt(
                nonce=nonce,
                data=ciphertext,
                associated_data=associated_data
            )
            
            return plaintext.decode("utf-8")
        except InvalidTag:
            logger.warning("解密失败：认证标签无效，数据可能被篡改")
            raise ValueError("解密失败：数据完整性校验不通过")
        except Exception as e:
            logger.error(f"解密异常: {e}")
            raise ValueError(f"解密失败: {str(e)}")

    def encrypt_field(self, value: str, field_name: str = "") -> str:
        """
        加密数据库字段值
        
        使用字段名作为关联数据，增强安全性
        """
        associated_data = field_name.encode("utf-8") if field_name else None
        return self.encrypt(value, associated_data)

    def decrypt_field(self, encrypted_value: str, field_name: str = "") -> str:
        """
        解密数据库字段值
        """
        associated_data = field_name.encode("utf-8") if field_name else None
        return self.decrypt(encrypted_value, associated_data)

    def _derive_key(self, master_key: str) -> bytes:
        """
        使用 PBKDF2 从主密钥派生加密密钥
        """
        salt = hashlib.sha256(master_key.encode()).digest()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=salt,
            iterations=self.KDF_ITERATIONS,
        )
        
        return kdf.derive(master_key.encode("utf-8"))

    def generate_key(self) -> str:
        """
        生成新的随机密钥（用于密钥轮换等场景）
        """
        return base64.b64encode(os.urandom(self.KEY_SIZE)).decode("ascii")

    def hash_data(self, data: str) -> str:
        """
        不可逆哈希（用于不需要解密的场景，如密码验证）
        """
        return hashlib.sha256(data.encode("utf-8")).hexdigest()


class FieldEncryptionMixin:
    """
    字段加密 Mixin
    
    可用于 SQLAlchemy Model，自动加密/解密指定字段
    """

    _encrypted_fields: list = []
    _encryption_service: Optional[EncryptionService] = None

    @classmethod
    def get_encryption_service(cls) -> EncryptionService:
        if cls._encryption_service is None:
            cls._encryption_service = EncryptionService()
        return cls._encryption_service

    def encrypt_fields(self):
        """加密所有标记字段"""
        service = self.get_encryption_service()
        for field_name in self._encrypted_fields:
            value = getattr(self, field_name, None)
            if value and not self._is_encrypted(value):
                encrypted = service.encrypt_field(str(value), field_name)
                setattr(self, field_name, encrypted)

    def decrypt_fields(self):
        """解密所有标记字段"""
        service = self.get_encryption_service()
        for field_name in self._encrypted_fields:
            value = getattr(self, field_name, None)
            if value and self._is_encrypted(value):
                try:
                    decrypted = service.decrypt_field(value, field_name)
                    setattr(self, field_name, decrypted)
                except ValueError:
                    pass

    @staticmethod
    def _is_encrypted(value: str) -> bool:
        """判断值是否已加密（简单启发式）"""
        try:
            decoded = base64.b64decode(value)
            return len(decoded) > EncryptionService.NONCE_SIZE
        except Exception:
            return False


def get_encryption_service() -> EncryptionService:
    """获取加密服务实例"""
    return EncryptionService()
