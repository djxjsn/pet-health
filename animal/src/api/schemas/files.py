"""
文件上传相关的 Pydantic Schema 定义
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    """文件上传响应"""
    success: bool = Field(..., description="是否上传成功")
    file_url: str = Field(..., description="文件访问 URL")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    file_type: str = Field(..., description="文件类型")
    message: Optional[str] = Field(None, description="消息")


class ImageUploadResponse(BaseModel):
    """图片上传响应"""
    success: bool = Field(..., description="是否上传成功")
    image_url: str = Field(..., description="图片访问 URL")
    file_name: str = Field(..., description="文件名")
    width: Optional[int] = Field(None, description="图片宽度")
    height: Optional[int] = Field(None, description="图片高度")
    thumbnail_url: Optional[str] = Field(None, description="缩略图 URL")
    message: Optional[str] = Field(None, description="消息")


class FileDeleteResponse(BaseModel):
    """文件删除响应"""
    success: bool = Field(..., description="是否删除成功")
    message: str = Field(..., description="消息")


class FileUploadConfigResponse(BaseModel):
    """文件上传配置响应"""
    max_upload_size: int = Field(..., description="最大上传大小（字节）")
    allowed_image_extensions: List[str] = Field(..., description="允许的图片格式")
    allowed_file_extensions: List[str] = Field(..., description="允许的文件格式")
    storage_provider: str = Field(..., description="存储服务商")
