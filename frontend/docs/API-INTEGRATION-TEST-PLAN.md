# 后端 API 对接联调测试计划

**项目**: AI 宠物健康助手前端
**日期**: 2026-04-15
**版本**: v1.0

---

## 一、后端 API 端点清单

### 1.1 认证模块 (M0)

| 方法 | 路径 | 功能 | 请求体 | 响应 |
|------|------|------|--------|------|
| POST | `/auth/login` | 登录 | FormData(username, password) | TokenData |
| POST | `/auth/register` | 注册 | RegisterRequest | User |
| POST | `/auth/refresh` | 刷新Token | RefreshTokenRequest | TokenData |
| GET | `/auth/forgot-password` | 忘记密码 | ?phone=xxx | {message} |
| POST | `/auth/reset-password` | 重置密码 | ResetPasswordRequest | {message} |

### 1.2 宠物管理 (M1)

| 方法 | 路径 | 功能 | 请求体 | 响应 |
|------|------|------|--------|------|
| GET | `/pets` | 宠物列表 | ?page=&page_size= | PetListResponse |
| GET | `/pets/{pet_id}` | 宠物详情 | - | Pet |
| POST | `/pets` | 新建宠物 | PetCreateRequest | Pet |
| PUT | `/pets/{pet_id}` | 更新宠物 | PetUpdateRequest | Pet |
| DELETE | `/pets/{pet_id}` | 删除宠物 | - | - |

### 1.3 健康咨询 (M2)

| 方法 | 路径 | 功能 | 请求体 | 响应 |
|------|------|------|--------|------|
| POST | `/health/consult` | 健康咨询 | HealthConsultRequest | HealthConsultResult |
| POST | `/health/analyze` | 症状分析 | SymptomAnalysisRequest | SymptomAnalysisResult |
| GET | `/health/consultations` | 咨询记录 | ?skip=&limit= | HealthConsultation[] |
| GET | `/health/records/{pet_id}` | 健康记录 | ?skip=&limit= | HealthRecord[] |

### 1.4 行为分析 (M3)

| 方法 | 路径 | 功能 | 请求体 | 响应 |
|------|------|------|--------|------|
| POST | `/behavior/analyze` | 行为分析 | BehaviorAnalyzeRequest | BehaviorAnalyzeResult |
| GET | `/behavior/history` | 分析历史 | ?skip=&limit= | BehaviorAnalysis[] |
| GET | `/behavior/history/{pet_id}` | 单宠历史 | ?skip=&limit= | BehaviorAnalysis[] |
| POST | `/behavior/training` | 训练建议 | TrainingRecommendationRequest | TrainingRecommendationResult |

### 1.5 对话模块

| 方法 | 路径 | 功能 | 请求体 | 响应 |
|------|------|------|--------|------|
| POST | `/chat` | 发送消息 | ChatRequest | ChatResponse |
| GET | `/conversations` | 会话列表 | ?skip=&limit= | Conversation[] |
| GET | `/conversations/{id}` | 会话详情 | - | ConversationDetail |
| GET | `/conversations/{id}/messages` | 消息列表 | ?skip=&limit= | Message[] |
| POST | `/conversations` | 创建会话 | {pet_id?} | CreateConversationResponse |
| DELETE | `/conversations/{id}` | 删除会话 | - | - |

### 1.6 WebSocket 实时对话

| 方向 | 类型 | 数据格式 |
|------|------|---------|
| C→S | auth | `{ type: "auth", token: "..." }` |
| S→C | connected | `{ type: "connected", user_id, message }` |
| C→S | heartbeat | `{ type: "heartbeat" }` |
| S→C | ping | `{ type: "ping" }` → C→S pong |
| C→S | message | `{ type: "message", data: { message, conversation_id?, pet_id? } }` |
| S→C | processing | `{ type: "processing", conversation_id, message }` |
| S→C | response | `{ type: "response", data: { conversation_id, response, relevant_context? } }` |
| S→C | error | `{ type: "error", message }` |

---

## 二、正常流程测试用例

### TC-001: 用户登录完整流程
```
前置条件: 已注册用户 (phone: 13800138000, password: Test123456)
步骤:
  1. 调用 authApi.login({ username: '13800138000', password: 'Test123456' })
  2. 验证返回 TokenData 包含 access_token, refresh_token
  3. 验证 token 写入 Zustand useAuthStore
  4. 验证 isAuthenticated = true
预期结果: 登录成功，token 存储，状态更新
```

### TC-002: 完整对话流程 (HTTP)
```
前置条件: 已登录 + 有宠物
步骤:
  1. chatApi.createConversation(petId) → 获得 conversationId
  2. chatApi.sendMessage({ message: '我的狗最近食欲不振', conversation_id, pet_id })
  3. 验证返回 response 字段非空
  4. chatApi.getMessages(conversationId) → 验证消息列表包含用户和助手消息
  5. chatApi.listConversations() → 验证会话出现在列表中
预期结果: 消息发送成功，回复内容合理，历史可查
```

### TC-003: WebSocket 实时对话流程
```
前置条件: 已登录
步骤:
  1. useWebSocket() → 自动连接
  2. 验证 status 变为 'connected'
  3. sendMessage('狗狗呕吐怎么办', { pet_id })
  4. 验证 isProcessing = true
  5. 验证收到 assistant role 的响应消息
  6. 验证 messages 数组包含 user + assistant 两条
预期结果: WS 连接稳定，消息收发实时完成
```

### TC-004: 宠物 CRUD 完整流程
```
前置条件: 已登录
步骤:
  1. petApi.create({ name: '测试猫', species: 'cat', breed: '英短' }) → petId
  2. petApi.getById(petId) → 验证数据正确
  3. petApi.update(petId, { weight: 4.5 }) → 验证 weight 更新
  4. petApi.list() → 验证列表包含新宠物
  5. petApi.delete(petId) → 验证删除成功
  6. petApi.list() → 验证已不在列表中
预期结果: CRUD 全流程无异常
```

### TC-005: 健康咨询流程
```
前置条件: 已登录 + 有宠物
步骤:
  1. healthApi.consult({ pet_id, symptoms: ['呕吐', '腹泻'], description: '持续2天' })
  2. 验证返回 diagnosis_result.possible_conditions 非空
  3. 验证 urgency_level 在 1-5 范围内
  4. 验证 recommendations 数组有内容
预期结果: 咨询结果结构完整，诊断合理
```

---

## 三、边界条件测试用例

### TC-101: Token 过期自动刷新
```
步骤:
  1. 使用过期或即将过期的 access_token 发起请求
  2. ApiClient 检测到 401 响应
  3. 自动调用 refresh_token 接口
  4. 使用新 token 重试原请求
预期结果: 用户无感知地完成续期，请求最终成功
```

### TC-102: 大量消息并发
```
步骤:
  1. 通过 WebSocket 快速连续发送 10 条消息
  2. 监控每条消息的响应顺序和完整性
  3. 验证无消息丢失或乱序
预期结果: 所有消息按序收到响应，无丢包
```

### TC-103: 网络中断恢复
```
步骤:
  1. 建立 WS 连接并确认 connected
  2. 断开网络（DevTools Offline）
  3. 验证 status 变为 disconnected
  4. 验证自动重连机制启动（最多 MAX_RECONNECT 次）
  5. 恢复网络
  6. 验证重连成功，status 回到 connected
预期结果: 断网检测及时，恢复后自动重连
```

### TC-104: 极端输入参数
```
场景:
  a) message 为空字符串 → 应被前端拦截或后端返回 400
  b) message 为 10000 字符超长文本 → 应正常处理或截断
  c) pet_name 含特殊字符 <script>alert(1)</script> → 应被转义
  d) symptoms 数组为空 [] → 返回提示信息
  e) page_size = 0 或负数 → 返回空列表或默认值
预期结果: 各边界输入均有合理处理，不导致崩溃
```

### TC-105: 并发 Tab 共享状态
```
步骤:
  1. 在 Tab A 登录
  2. 在同一浏览器打开 Tab B
  3. 验证 Tab B 通过 localStorage 读取到登录状态
  4. 在 Tab B 发送消息
  5. 切回 Tab A，验证状态同步
预期结果: 多 Tab 状态通过 localStorage 同步一致
```

---

## 四、异常场景测试用例

### TC-201: 401 未认证访问受保护资源
```
步骤:
  1. 清除所有认证状态（logout / 清除 localStorage）
  2. 直接调用 petApi.list()
  3. 验证抛出 ApiClientError (status: 401)
  4. 验证 Toast 显示 "请重新登录"
  5. 验证自动跳转到 /login?redirect=/...
预期结果: 错误捕获友好提示，自动引导至登录页
```

### TC-202: 403 权限不足
```
步骤:
  1. 用普通用户 token 尝试调用管理员接口
  2. 验证返回 403 错误
  3. 验证 Toast 显示权限提示
预期结果: 权限错误清晰展示，无崩溃
```

### TC-203: 500 服务器内部错误
```
步骤:
  1. 后端模拟 500 错误（可通过代理工具或 mock）
  2. 调用任意 API 接口
  3. 验证 ApiClient 自动重试 MAX_RETRIES 次
  4. 重试失败后显示 Toast 提示
  5. 提供"重试"按钮
预期结果: 自动重试 + 友好降级提示
```

### TC-204: 网络完全不可达
```
步骤:
  1. 后端服务未启动
  2. 调用任意 HTTP API
  3. 验证 NetworkError 抛出
  4. 验证分类为 ErrorCategory.NETWORK
  5. 验证 Toast 显示网络异常提示
预期结果: 网络错误统一处理，用户体验友好
```

### TC-205: WebSocket 连接失败
```
步骤:
  1. 配置错误的 WS URL（指向不存在的主机）
  2. 调用 useWebSocket()
  3. 验证 status 经过 connecting → error
  4. 验证重连尝试达到上限后停止
  5. 验证 onError 回调触发
预期结果: 连接失败有明确状态反馈，不会无限重连
```

### TC-206: JSON 解析失败
```
步骤:
  1. 后端返回非 JSON 格式响应（如 HTML 错误页面）
  2. ApiClient 尝试解析响应体
  3. 验证 catch 解析错误
  4. 分类为 ErrorCategory.PARSE_ERROR
预期结果: 解析错误安全处理，不暴露原始错误给用户
```

### TC-207: React 组件渲染异常
```
步骤:
  1. 某组件在渲染时抛出运行时错误
  2. ErrorBoundary 捕获错误
  3. 显示错误 UI（emoji + 错误信息 + 重试/首页按钮）
  4. 点击重试 → 组件重新挂载
预期结果: 单组件错误不影响整个应用，提供恢复路径
```

---

## 五、性能与稳定性测试

### TP-01: API 响应时间基准
| 接口 | 目标 P95 | 测量方法 |
|------|---------|---------|
| 登录 | < 800ms | performance.mark |
| 宠物列表 | < 500ms | performance.mark |
| 发送消息(HTTP) | < 3000ms | performance.mark |
| WS 消息往返 | < 2000ms | timestamp diff |
| 健康咨询 | < 5000ms | performance.mark |

### TP-02: 内存泄漏检测
```
方法:
  1. 打开 DevTools Memory 面板
  2. 执行 Heap Snapshot (baseline)
  3. 反复执行: 登录 → 发送消息 → 切换页面 × 20 次
  4. 再次 Heap Snapshot
  5. 对比内存增长，确认无显著泄漏
标准: 内存增长 < 10MB
```

### TP-03: WebSocket 心跳稳定性
```
方法:
  1. 保持 WS 连接 30 分钟
  2. 监控心跳间隔是否稳定 (~25s)
  3. 验证无心跳丢失导致的断连
  4. 验证 CPU 占用率在合理范围 (< 5%)
标准: 长连接无异常断开
```

---

## 六、验收检查清单

### 代码质量
- [ ] ESLint 0 errors
- [ ] TypeScript 编译通过
- [ ] Production Build 成功
- [ ] 62 个单元测试全部通过
- [ ] 无 console.error/console.warn 残留（仅允许 console.log 用于调试）

### API 对接完整性
- [ ] 所有 25+ REST 端点有对应的前端 API 函数
- [ ] 所有请求/响应类型与后端 Schema 一致
- [ ] Token 自动注入到 Authorization header
- [ ] 401 时自动尝试刷新 token
- [ ] 请求超时有明确的错误提示

### WebSocket 协议一致性
- [ ] auth 消息格式匹配后端期望
- [ ] heartbeat/ping-pong 机制工作正常
- [ ] message/response 类型字段对齐
- [ ] error 类型正确处理
- [ ] 重连策略符合设计（指数退避 + 最大次数）

### 错误处理覆盖
- [ ] 8 种 ErrorCategory 全部有对应处理逻辑
- [ ] Toast 通知正确展示用户友好的错误信息
- [ ] Auth 错误自动跳转登录页
- [ ] 可重试错误提供重试按钮
- [ ] ErrorBoundary 捕获 React 渲染异常
- [ ] withErrorHandling 包装器可用于任何异步操作

---

*文档生成时间: 2026-04-15*
