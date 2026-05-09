"""
文件上传 API 路由

提供文件上传、下载、删除等接口。
"""
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
import logging
import os
from pathlib import Path

from src.api.schemas.files import (
    FileUploadResponse,
    ImageUploadResponse,
    FileDeleteResponse,
    FileUploadConfigResponse
)
from src.services.tool_services.factory import get_file_storage
from src.config.third_party_config import get_third_party_config

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["文件管理"])


@router.post("/upload", response_model=FileUploadResponse, summary="上传文件")
async def upload_file(file: UploadFile = File(...), folder: Optional[str] = Query(None)):
    """
    上传通用文件
    
    - **file**: 要上传的文件
    - **folder**: 目标文件夹（可选）
    
    支持格式：PDF, DOC, DOCX, TXT 等
    """
    try:
        config = get_third_party_config()
        
        # 检查文件大小
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > config.max_upload_size:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制 ({config.max_upload_size / 1024 / 1024:.1f}MB)"
            )
        
        # 检查文件扩展名
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in config.allowed_file_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式：{file_ext}，允许的格式：{config.allowed_file_extensions}"
            )
        
        # 保存临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(file_content)
            tmp_path = tmp_file.name
        
        try:
            # 上传到存储服务
            storage = get_file_storage()
            file_url = storage.upload_file(tmp_path, folder=folder)
            
            return FileUploadResponse(
                success=True,
                file_url=file_url,
                file_name=file.filename,
                file_size=file_size,
                file_type=file.content_type or "application/octet-stream",
                message="文件上传成功"
            )
        finally:
            # 清理临时文件
            os.unlink(tmp_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传文件失败：{e}")
        raise HTTPException(status_code=500, detail=f"上传文件失败：{str(e)}")


@router.post("/upload/image", response_model=ImageUploadResponse, summary="上传图片")
async def upload_image(
    image: UploadFile = File(...),
    folder: Optional[str] = Query(None),
    generate_thumbnail: bool = Query(True, description="是否生成缩略图")
):
    """
    上传图片
    
    - **image**: 要上传的图片
    - **folder**: 目标文件夹（可选）
    - **generate_thumbnail**: 是否生成缩略图
    
    支持格式：JPG, JPEG, PNG, GIF, WEBP
    """
    try:
        config = get_third_party_config()
        
        # 检查文件大小
        image_content = await image.read()
        file_size = len(image_content)
        
        if file_size > config.max_upload_size:
            raise HTTPException(
                status_code=400,
                detail=f"图片大小超过限制 ({config.max_upload_size / 1024 / 1024:.1f}MB)"
            )
        
        # 检查图片格式
        image_ext = Path(image.filename).suffix.lower()
        if image_ext not in config.allowed_image_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的图片格式：{image_ext}，允许的格式：{config.allowed_image_extensions}"
            )
        
        # 保存临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=image_ext) as tmp_file:
            tmp_file.write(image_content)
            tmp_path = tmp_file.name
        
        try:
            # 上传到存储服务
            storage = get_file_storage()
            image_url = storage.upload_image(tmp_path, folder=folder or "images")
            
            # 获取图片尺寸（可选）
            width = None
            height = None
            thumbnail_url = None
            
            if generate_thumbnail:
                # TODO: 实现缩略图生成
                pass
            
            return ImageUploadResponse(
                success=True,
                image_url=image_url,
                file_name=image.filename,
                width=width,
                height=height,
                thumbnail_url=thumbnail_url,
                message="图片上传成功"
            )
        finally:
            # 清理临时文件
            os.unlink(tmp_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传图片失败：{e}")
        raise HTTPException(status_code=500, detail=f"上传图片失败：{str(e)}")


@router.delete("/delete", response_model=FileDeleteResponse, summary="删除文件")
async def delete_file(file_url: str = Query(..., description="文件 URL")):
    """删除指定文件"""
    try:
        storage = get_file_storage()
        success = storage.delete_file(file_url)
        
        if not success:
            raise HTTPException(status_code=404, detail="文件不存在或删除失败")
        
        return FileDeleteResponse(
            success=True,
            message="文件删除成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除文件失败：{e}")
        raise HTTPException(status_code=500, detail=f"删除文件失败：{str(e)}")


@router.get("/config", response_model=FileUploadConfigResponse, summary="获取上传配置")
async def get_upload_config():
    """获取文件上传配置信息"""
    try:
        config = get_third_party_config()
        
        return FileUploadConfigResponse(
            max_upload_size=config.max_upload_size,
            allowed_image_extensions=config.allowed_image_extensions,
            allowed_file_extensions=config.allowed_file_extensions,
            storage_provider=config.storage_provider
        )
    except Exception as e:
        logger.error(f"获取上传配置失败：{e}")
        raise HTTPException(status_code=500, detail=f"获取配置失败：{str(e)}")
