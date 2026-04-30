# CHANGELOG

All notable changes to the AI Pet Health Assistant project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Shopping cart full CRUD functionality
- CI/CD pipeline (GitHub Actions)
- Production deployment (Docker/Vercel)
- Performance monitoring (APM)
- Internationalization (i18n)
- Mobile responsive optimization

---

## [v9.0.0] - 2026-04-18

### Added - Data Security & Privacy Module (DEV-009 / M7)
- **Encryption Service** (`src/core/encryption.py`)
  - AES-256-GCM authenticated encryption
  - PBKDF2-SHA256 key derivation (100,000 iterations)
  - Random 12-byte nonce per encryption
  - Associated data (AAD) binding for field-name protection
  - Field-level encryption/decryption helpers
  - One-way hashing utility
- **Data Masker** (`src/core/data_masker.py`)
  - 9 built-in masking strategies: phone, email, ID card, name, address, bank card, password, IP address, custom
  - Batch dictionary masking (`mask_dict`)
  - Nested dictionary masking (`mask_nested_dict`)
  - Configurable exclusion fields
- **RBAC Permission Control** (`src/core/rbac.py`)
  - 5-tier role hierarchy: SUPER_ADMIN, ADMIN, VETERINARIAN, USER, GUEST
  - 14 permission categories: user, pet, health, shop, knowledge, admin, audit, security, data
  - FastAPI dependency injection decorators (`require_permission`, `require_role`)
  - Role inheritance with automatic permission aggregation
  - SecurityContext for request-level permission tracking
- **Audit Log Service** (`src/core/audit.py`)
  - MongoDB immutable append-only storage
  - 7 action categories: auth, user, pet, health, shopping, security, system
  - 3 severity levels: INFO, WARNING, CRITICAL
  - Query methods: by user, by type, security events, date range
- **Security API Endpoints** (`src/api/v1/endpoints/security.py`)
  - POST `/security/encrypt` - Encrypt data
  - POST `/security/decrypt` - Decrypt data
  - POST `/security/mask` - Data masking preview
  - GET `/security/roles` - List all roles
  - GET `/security/permissions` - List all permissions
  - GET `/security/role/{name}/permissions` - Role permissions
  - GET `/security/audit/logs` - Query audit logs
  - GET `/security/audit/security-events` - Security events
  - GET `/security/audit/user-activity/{id}` - User activity
  - GET `/security/overview` - Security overview
- **Tests** (`tests/test_dev009_security.py`)
  - 47 test cases covering all security components
  - 100% pass rate

### Changed
- Updated project README with v9.0 status
- Updated animal README with all completed modules
- Updated project progress report to v9.0 (99% complete)
- Updated task tracking table to v9.0
- Updated risk assessment report to v9.0 (R9 closed)
- Registered security endpoints in API router

### Security
- Industrial-grade encryption with AES-256-GCM
- Brute-force resistant key derivation (PBKDF2, 100k iterations)
- Tamper detection via GCM authentication tags
- Immutable audit trail for compliance

---

## [v8.0.0] - 2026-04-17

### Added - Tool Integration Module (DEV-008 / M6)
- **External API Tools** (`src/tools/external_tools.py`)
  - WeatherTool - 7-day forecast + pet activity suggestions
  - MapServiceTool - Nearby hospitals/stores/parks (6 categories)
  - WebSearchTool - News/knowledge/reviews search
  - ImageRecognitionTool - Breed/symptom/food/label recognition
  - KnowledgeEnhanceTool - Multi-source knowledge enhancement
- **Tool Execution Framework** (`src/tools/tool_executor.py`)
  - Unified executor with configurable parameters
  - Result caching with TTL
  - Automatic retry with exponential backoff
  - Parallel execution (ThreadPoolExecutor)
  - Chain execution with context passing
  - Standardized ToolCallResult model
- **Tool Registry** (`src/tools/tool_registry.py`)
  - 15 tools registered (10 internal + 5 external)
  - Unified discovery and execution interface
- **Tests**
  - ~110 test cases covering all tool components
  - 100% pass rate

### Changed
- Token expiry extended from 30 minutes to 2 hours (120 minutes)
- Sidebar toggle button UI improved
- Chat history integrated into dropdown menu
- DEV-007 shopping module testing expanded (9 → 109 test cases)
- DEV-007 documentation expanded (3 → 6 documents)

### Fixed
- BUG-001: Pydantic model field missing errors (supplemented complete fields)
- BUG-002: patch.object mock failure (fixed mock approach)
- BUG-003: AllergenWarning field structure mismatch (added missing fields)
- BUG-004: Pydantic ClassVar annotation errors (added ClassVar type hints)
- ISSUE-001: Token expiry too short (user feedback)
- ISSUE-002: Sidebar button position (user feedback)
- ISSUE-003: Chat history navigation (user feedback)

---

## [v7.0.0] - 2026-04-17

### Added - Knowledge Management Module (DEV-006 / M5)
- Document loading and chunking
- Vector storage and retrieval (ChromaDB/Milvus)
- RAG (Retrieval-Augmented Generation) pipeline
- Knowledge base CRUD management
- ~30 test cases

### Changed
- Project progress reached 97%
- All frontend modules completed

---

## [v6.0.0] - 2026-04-16

### Added - Frontend Modules
- FE-P0: Core components (62 tests)
- FE-P1: Functional pages
- FE-P2: Enhanced experience
- FE-INFRA: Infrastructure layer
- FE-TEST: Testing system (11 E2E tests)
- FE-P0-OPT: Performance optimization
- FE-API: Backend API integration
- REAL-TEST: Real environment integration testing (100% pass)

### Changed
- Project progress reached 95%
- Frontend 8/8 modules completed

---

## [v5.0.0] - 2026-04-15

### Added - Behavior Analysis Module (DEV-005 / M3)
- Behavior recognition and classification
- Breed-specific behavior analysis
- Training recommendations
- 25+ test cases

### Fixed
- R1: HuggingFace network unreachable (implemented fallback)
- R2: DB Schema vs ORM mismatch (ALTER TABLE fix)
- R3: OAuth2 FormData format issue (parameter adjustment)
- R4: Uvicorn hot-reload test crash (non-reload mode)

### Changed
- Project progress reached 90%
- Risk assessment established

---

## [v4.0.0] - 2026-04-12

### Added - Health Consultation Module (DEV-004 / M2)
- Symptom analysis engine
- Urgency level assessment
- LLM-powered diagnostic suggestions
- 22+ test cases

### Changed
- Project progress reached 85%

---

## [v3.0.0] - 2026-04-12

### Added - Agent Orchestration Module (DEV-003 / M8)
- Multi-agent collaboration framework
- Tool calling integration
- RAG retrieval pipeline
- 18+ test cases

### Changed
- Project progress reached 80%

---

## [v2.0.0] - 2026-04-10

### Added - Pet Profile Module (DEV-002 / M1)
- Pet CRUD operations
- Breed database with health characteristics
- Vaccine record management
- Photo management
- 20+ test cases

### Changed
- Project progress reached 70%

---

## [v1.0.0] - 2026-04-09

### Added - Authentication Module (DEV-001 / M0)
- User registration (phone/email)
- User login with JWT
- Token refresh mechanism
- Password reset (email pending integration)
- User profile management
- OAuth2 integration
- 15+ test cases

### Infrastructure
- FastAPI project setup
- MySQL database configuration
- SQLAlchemy ORM models
- Alembic migration
- Pydantic v2 schemas
- Environment configuration
- Project documentation (PRD, Architecture, UI Design)

---

## Summary Statistics

| Version | Date | Key Feature | Progress |
|---------|------|-------------|----------|
| v1.0.0 | 2026-04-09 | Authentication (M0) | 10% |
| v2.0.0 | 2026-04-10 | Pet Profiles (M1) | 20% |
| v3.0.0 | 2026-04-12 | Agent Orchestration (M8) | 35% |
| v4.0.0 | 2026-04-12 | Health Consultation (M2) | 50% |
| v5.0.0 | 2026-04-15 | Behavior Analysis (M3) | 65% |
| v6.0.0 | 2026-04-16 | Frontend Complete | 85% |
| v7.0.0 | 2026-04-17 | Knowledge Management (M5) | 95% |
| v8.0.0 | 2026-04-17 | Tool Integration (M6) + DEV-007 Polish | 98% |
| v9.0.0 | 2026-04-18 | Data Security (M7) | 99% |

---

**Maintained by**: AI Assistant  
**Last Updated**: 2026-04-18
