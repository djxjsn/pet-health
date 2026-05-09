"""
文档加载器

支持从多种格式（TXT, Markdown, JSON）加载知识文档，
并提供统一的文档数据结构。
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


class Document:
    """文档数据类"""
    
    def __init__(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None
    ):
        self.content = content
        self.metadata = metadata or {}
        self.source = source
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "content": self.content,
            "metadata": self.metadata,
            "source": self.source
        }


class DocumentLoader:
    """文档加载器"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """初始化文档加载器
        
        Args:
            base_dir: 文档根目录，默认为项目的 data/knowledge 目录
        """
        if base_dir is None:
            project_root = Path(__file__).parent.parent.parent
            base_dir = project_root / "data" / "knowledge"
        
        self.base_dir = Path(base_dir)
    
    def load_file(self, file_path: str, category: str, source: Optional[str] = None) -> Document:
        """加载单个文件
        
        Args:
            file_path: 文件路径
            category: 文档分类
            source: 知识来源
        
        Returns:
            Document对象
        
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 不支持的文件格式
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        suffix = path.suffix.lower()
        
        if suffix in ['.txt', '.md', '.markdown']:
            content = self._load_text_file(path)
        elif suffix == '.json':
            content = self._load_json_file(path)
        else:
            raise ValueError(f"不支持的文件格式: {suffix}")
        
        metadata = {
            "filename": path.name,
            "category": category,
            "file_size": path.stat().st_size
        }
        
        if source is None:
            source = path.name
        
        return Document(
            content=content,
            metadata=metadata,
            source=source
        )
    
    def load_directory(
        self,
        directory: Optional[str] = None,
        category: Optional[str] = None,
        source_prefix: Optional[str] = None
    ) -> List[Document]:
        """加载目录下的所有文档文件
        
        Args:
            directory: 目录路径，默认为base_dir下的子目录
            category: 文档分类，如果未提供则从目录名推断
            source_prefix: 知识来源前缀
        
        Returns:
            Document对象列表
        """
        if directory is None:
            dir_path = self.base_dir
        else:
            dir_path = Path(directory)
            if not dir_path.is_absolute():
                dir_path = self.base_dir / directory
        
        if not dir_path.exists():
            return []
        
        documents = []
        
        for file_path in dir_path.glob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.txt', '.md', '.markdown', '.json']:
                try:
                    if category is None:
                        category = dir_path.name
                    
                    source = f"{source_prefix}/{file_path.name}" if source_prefix else file_path.name
                    
                    doc = self.load_file(str(file_path), category=category, source=source)
                    documents.append(doc)
                except Exception as e:
                    print(f"加载文件失败 {file_path}: {e}")
        
        return documents
    
    def load_all_categories(self) -> Dict[str, List[Document]]:
        """加载所有分类的知识文档
        
        Returns:
            分类到文档列表的映射
        """
        categories = {
            "disease": [],
            "medication": [],
            "first_aid": [],
            "nutrition": [],
            "behavior": []
        }
        
        if not self.base_dir.exists():
            return categories
        
        for category in categories.keys():
            category_dir = self.base_dir / category
            if category_dir.exists():
                categories[category] = self.load_directory(
                    directory=category_dir,
                    category=category,
                    source_prefix=f"knowledge_base/{category}"
                )
        
        return categories
    
    def _load_text_file(self, file_path: Path) -> str:
        """加载文本文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _load_json_file(self, file_path: Path) -> str:
        """加载JSON文件，提取content字段"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict):
            return data.get('content', json.dumps(data, ensure_ascii=False))
        elif isinstance(data, list):
            return json.dumps(data, ensure_ascii=False)
        else:
            return str(data)
