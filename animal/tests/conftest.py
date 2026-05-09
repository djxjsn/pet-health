"""
测试配置
"""
import pytest
from typing import Generator
from unittest.mock import Mock, MagicMock
import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["TESTING"] = "True"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from src.main import app
from src.core.database import Base, get_db
from src.core.config import get_settings

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app=app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user_data() -> dict:
    return {
        "phone": "13800000002",
        "email": "testuser@example.com",
        "password": "test1234"
    }


@pytest.fixture(scope="function")
def second_user_data() -> dict:
    return {
        "phone": "13900000001",
        "email": "seconduser@example.com",
        "password": "test5678"
    }


@pytest.fixture(scope="function")
def registered_user(client: TestClient, test_user_data: dict) -> dict:
    response = client.post("/api/v1/auth/register", json=test_user_data)
    return response.json()


@pytest.fixture(scope="function")
def auth_token(client: TestClient, test_user_data: dict, registered_user: dict) -> str:
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user_data["phone"],
            "password": test_user_data["password"]
        }
    )
    return login_response.json()["access_token"]


@pytest.fixture(scope="function")
def auth_headers(auth_token: str) -> dict:
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="function")
def second_registered_user(client: TestClient, second_user_data: dict) -> dict:
    response = client.post("/api/v1/auth/register", json=second_user_data)
    return response.json()


@pytest.fixture(scope="function")
def second_auth_token(client: TestClient, second_user_data: dict, second_registered_user: dict) -> str:
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": second_user_data["phone"],
            "password": second_user_data["password"]
        }
    )
    return login_response.json()["access_token"]


@pytest.fixture(scope="function")
def second_auth_headers(second_auth_token: str) -> dict:
    return {"Authorization": f"Bearer {second_auth_token}"}


@pytest.fixture(scope="function")
def test_pet_data() -> dict:
    return {
        "name": "旺财",
        "species": "dog",
        "breed": "金毛寻回犬",
        "gender": "male",
        "birth_date": "2022-03-15",
        "weight": "28.50",
        "is_vaccinated": True,
        "is_neutered": False,
    }


@pytest.fixture(scope="function")
def created_pet(client: TestClient, auth_headers: dict, test_pet_data: dict) -> dict:
    response = client.post("/api/v1/pets", json=test_pet_data, headers=auth_headers)
    return response.json()


@pytest.fixture(autouse=True)
def mock_vector_db():
    """自动 mock 向量数据库，避免测试时连接 HuggingFace"""
    from unittest.mock import patch

    mock_vdb = MagicMock()
    mock_vdb.is_available = True
    mock_vdb.query.return_value = {
        'documents': [['测试知识内容']],
        'metadatas': [[{'source': 'test'}]],
        'distances': [[0.5]],
    }
    mock_vdb.add_documents.return_value = None
    mock_vdb.delete_documents.return_value = None

    mock_retriever = MagicMock()
    mock_retriever.is_available = True
    mock_retriever.search.return_value = [
        {"content": "测试知识内容", "metadata": {"source": "test"}, "distance": 0.5}
    ]
    mock_retriever.search_for_symptom_analysis.return_value = [
        {"content": "测试知识内容", "metadata": {"source": "test"}, "distance": 0.5}
    ]
    mock_retriever.search_for_nutrition_advice.return_value = [
        {"content": "测试知识内容", "metadata": {"source": "test"}, "distance": 0.5}
    ]
    mock_retriever.search_for_conversation_context.return_value = [
        {"content": "测试知识内容", "metadata": {"source": "test"}, "distance": 0.5}
    ]
    mock_retriever.search_for_knowledge_enhancement.return_value = [
        {"content": "测试知识内容", "metadata": {"source": "test"}, "distance": 0.5}
    ]

    with patch("src.core.vector_db.get_vector_db", return_value=mock_vdb), \
         patch("src.core.knowledge_retriever.get_vector_db", return_value=mock_vdb), \
         patch("src.core.knowledge_retriever.get_knowledge_retriever", return_value=mock_retriever), \
         patch("src.memory.conversation_memory.get_vector_db", return_value=mock_vdb), \
         patch("src.memory.conversation_memory.get_knowledge_retriever", return_value=mock_retriever), \
         patch("src.tools.pet_health_tools.get_knowledge_retriever", return_value=mock_retriever), \
         patch("src.tools.health_tools.get_vector_db", return_value=mock_vdb), \
         patch("src.tools.behavior_tools.get_vector_db", return_value=mock_vdb):
        yield mock_vdb
