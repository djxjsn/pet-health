"""
LLM 服务层

封装 LangChain LLM 调用，统一管理模型初始化
"""
from functools import lru_cache
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseLLM

from src.core.config import get_settings


@lru_cache()
def get_llm() -> BaseLLM:
    """获取 LLM 实例（单例）

    使用 DeepSeek API（兼容 OpenAI 格式）
    """
    settings = get_settings()

    api_key = settings.DEEPSEEK_API_KEY
    if not api_key:
        raise ValueError(
            "DEEPSEEK_API_KEY 未配置，请在 .env 文件中设置"
        )

    llm = ChatOpenAI(
        model=settings.DEEPSEEK_MODEL,
        openai_api_key=api_key,
        openai_api_base=settings.DEEPSEEK_API_BASE,
        temperature=0.7,
        max_tokens=2048,
        streaming=False,
        request_timeout=60,
    )
    return llm


def get_streaming_llm() -> BaseLLM:
    """获取支持流式输出的 LLM 实例"""
    settings = get_settings()

    api_key = settings.DEEPSEEK_API_KEY
    if not api_key:
        raise ValueError(
            "DEEPSEEK_API_KEY 未配置，请在 .env 文件中设置"
        )

    llm = ChatOpenAI(
        model=settings.DEEPSEEK_MODEL,
        openai_api_key=api_key,
        openai_api_base=settings.DEEPSEEK_API_BASE,
        temperature=0.7,
        max_tokens=2048,
        streaming=True,
        request_timeout=60,
    )
    return llm
