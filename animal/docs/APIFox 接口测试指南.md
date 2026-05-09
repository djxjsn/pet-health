# AI 宠物健康助手 - APIFox 接口测试指南

## 目录
1. [测试环境配置](#一测试环境配置)
2. [接口文档导入](#二接口文档导入)
3. [测试用例设计](#三测试用例设计)
4. [测试执行步骤](#四测试执行步骤)
5. [测试结果验证](#五测试结果验证)
6. [测试报告生成与分析](#六测试报告生成与分析)
7. [自动化测试配置](#七自动化测试配置)
8. [常见问题与解决方案](#八常见问题与解决方案)

---

## 一、测试环境配置

### 1.1 安装与初始化

#### 步骤 1: 下载并安装 APIFox
```
访问官网：https://apifox.com/
下载对应版本（Windows/Mac/Linux）
安装完成后启动应用
```

#### 步骤 2: 创建新项目
1. 点击「新建项目」
2. 项目名称：`AI 宠物健康助手`
3. 项目描述：`基于 LangChain 的 AI 宠物健康助手 API 接口测试`
4. 项目标签：`宠物健康`、`AI`、`FastAPI`
5. 点击「创建」

### 1.2 环境配置

#### 创建测试环境
1. 进入「项目设置」 → 「环境管理」
2. 点击「新增环境」，创建以下环境：

**开发环境 (dev)**
```json
{
  "name": "开发环境",
  "domain": "http://localhost:8000",
  "basePath": "/api/v1",
  "variables": {
    "base_url": "http://localhost:8000/api/v1"
  }
}
```

**测试环境 (test)**
```json
{
  "name": "测试环境",
  "domain": "https://test-api.pet-health.com",
  "basePath": "/api/v1"
}
```

**生产环境 (prod)**
```json
{
  "name": "生产环境",
  "domain": "https://api.pet-health.com",
  "basePath": "/api/v1"
}
```

### 1.3 全局认证配置

#### JWT Token 认证设置
1. 进入「项目设置」 → 「认证设置」
2. 选择「Token 认证」
3. 配置如下：

```
认证类型：Bearer Token
Token 变量名：{{access_token}}
应用范围：全局生效（或指定接口）
```

#### 前置脚本自动获取 Token
```javascript
// 在「前置操作」中添加以下脚本
const loginRequest = {
  url: pm.variables.get("base_url") + "/auth/login",
  method: "POST",
  header: {
    "Content-Type": "application/x-www-form-urlencoded"
  },
  body: {
    mode: "urlencoded",
    urlencoded: [
      { key: "username", value: "13800000001" },
      { key: "password", value: "test1234" }
    ]
  }
};

pm.sendRequest(loginRequest, (err, response) => {
  if (err) {
    console.error("获取 Token 失败:", err);
  } else {
    const jsonData = response.json();
    pm.environment.set("access_token", jsonData.access_token);
    console.log("Token 获取成功:", jsonData.access_token);
  }
});
```

### 1.4 全局请求头配置

#### 常用请求头
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
User-Agent: APIFox-Test/1.0
X-Request-ID: {{$randomUUID}}
```

#### 配置步骤
1. 进入「项目设置」 → 「请求头」
2. 添加公共请求头
3. 勾选「继承到所有接口」

---

## 二、接口文档导入

### 2.1 从 OpenAPI/Swagger 导入

#### 方法 1: URL 导入（推荐）
1. 启动 FastAPI 应用：
```bash
cd animal
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

2. 访问 Swagger 文档：
```
http://localhost:8000/openapi.json
```

3. 在 APIFox 中：
   - 点击「导入」 → 「URL」
   - 输入：`http://localhost:8000/openapi.json`
   - 点击「确定导入」

#### 方法 2: 文件导入
1. 导出 OpenAPI 文档：
```bash
curl http://localhost:8000/openapi.json -o openapi.json
```

2. 在 APIFox 中：
   - 点击「导入」 → 「OpenAPI/Swagger」
   - 选择 `openapi.json` 文件
   - 点击「导入」

### 2.2 手动创建接口（补充测试用例）

#### 创建认证相关接口

**接口 1: 用户注册**
```
接口名称：用户注册
请求路径：POST {{base_url}}/auth/register
Content-Type: application/json

请求体:
{
  "phone": "13800000010",
  "email": "test_user@example.com",
  "password": "test1234"
}

预期响应:
- 状态码：201 Created
- 响应体包含：user_id, phone, email
```

**接口 2: 用户登录**
```
接口名称：用户登录
请求路径：POST {{base_url}}/auth/login
Content-Type: application/x-www-form-urlencoded

请求体:
username: 13800000010
password: test1234

预期响应:
- 状态码：200 OK
- 响应体包含：access_token, refresh_token, token_type
- 提取 Token 到环境变量
```

#### 创建对话相关接口

**接口 3: AI 对话**
```
接口名称：AI 健康咨询对话
请求路径：POST {{base_url}}/chat
认证：Bearer Token
Content-Type: application/json

请求体:
{
  "message": "你好，我想咨询宠物健康问题",
  "conversation_id": "",
  "pet_id": "",
  "context": {}
}

预期响应:
- 状态码：200 OK
- 响应体包含：conversation_id, response, relevant_context
- 响应时间：< 2000ms
```

**接口 4: 创建对话**
```
接口名称：创建新对话
请求路径：POST {{base_url}}/conversations
认证：Bearer Token
Content-Type: application/json

请求体:
{
  "title": "健康咨询",
  "pet_id": ""
}

预期响应:
- 状态码：201 Created
- 响应体包含：conversation_id, user_id, created_at
```

**接口 5: 查询对话列表**
```
接口名称：查询对话列表
请求路径：GET {{base_url}}/conversations?skip=0&limit=20
认证：Bearer Token

预期响应:
- 状态码：200 OK
- 响应体：对话数组
- 包含字段：conversation_id, title, message_count
```

**接口 6: 获取对话详情**
```
接口名称：获取对话详情（含消息）
请求路径：GET {{base_url}}/conversations/{{conversation_id}}
认证：Bearer Token

预期响应:
- 状态码：200 OK
- 响应体包含：conversation 信息 + messages 数组
```

**接口 7: 删除对话**
```
接口名称：删除对话
请求路径：DELETE {{base_url}}/conversations/{{conversation_id}}
认证：Bearer Token

预期响应:
- 状态码：204 No Content
```

---

## 三、测试用例设计

### 3.1 测试用例组织

#### 测试集合结构
```
AI 宠物健康助手测试
├── 01-用户认证模块
│   ├── 用户注册测试
│   ├── 用户登录测试
│   ├── Token 刷新测试
│   └── 认证失败测试
├── 02-对话管理模块
│   ├── 创建对话测试
│   ├── 查询对话列表测试
│   ├── 获取对话详情测试
│   └── 删除对话测试
├── 03-AI 对话功能测试
│   ├── 单轮对话测试
│   ├── 多轮对话测试
│   ├── 带宠物上下文对话测试
│   └── 对话上下文保持测试
└── 04-错误处理测试
    ├── 未认证访问测试
    ├── 无效 Token 测试
    ├── 参数验证测试
    └── 资源不存在测试
```

### 3.2 详细测试用例

#### 测试集合 1: 用户认证模块

**用例 1.1: 用户注册 - 正常流程**
```
测试名称：用户注册成功
前置条件：无
请求：
  POST {{base_url}}/auth/register
  Body: {
    "phone": "13800000011",
    "email": "register_test@example.com",
    "password": "test1234"
  }

验证规则:
  ✓ 状态码 = 201
  ✓ 响应体.user_id 不为空
  ✓ 响应体.phone = "13800000011"
  ✓ 响应体.is_active = true
  ✓ 响应时间 < 1000ms

后置操作：保存 user_id 到环境变量
```

**用例 1.2: 用户注册 - 手机号重复**
```
测试名称：注册失败 - 手机号已存在
前置条件：已存在手机号 13800000011
请求：
  POST {{base_url}}/auth/register
  Body: {
    "phone": "13800000011",
    "email": "another@example.com",
    "password": "test1234"
  }

验证规则:
  ✓ 状态码 = 400 或 409
  ✓ 响应体.detail 包含 "手机号" 或 "已存在"
```

**用例 1.3: 用户注册 - 参数验证**
```
测试名称：注册失败 - 手机号格式错误
请求：
  POST {{base_url}}/auth/register
  Body: {
    "phone": "12345",  // 无效手机号
    "email": "test@example.com",
    "password": "test1234"
  }

验证规则:
  ✓ 状态码 = 422
  ✓ 响应体.detail 包含 "手机号" 或 "验证"
```

**用例 1.4: 用户登录 - 成功**
```
测试名称：登录成功
前置条件：已注册用户
请求：
  POST {{base_url}}/auth/login
  Body: 
    username=13800000011
    password=test1234

验证规则:
  ✓ 状态码 = 200
  ✓ 响应体.access_token 不为空
  ✓ 响应体.token_type = "bearer"
  ✓ 响应体.expires_in > 0

后置操作:
  - 提取 access_token 到环境变量
  - 提取 refresh_token 到环境变量
```

**用例 1.5: 用户登录 - 密码错误**
```
测试名称：登录失败 - 密码错误
请求：
  POST {{base_url}}/auth/login
  Body:
    username=13800000011
    password=wrong_password

验证规则:
  ✓ 状态码 = 401
  ✓ 响应体.detail 包含 "密码" 或 "认证"
```

#### 测试集合 2: 对话管理模块

**用例 2.1: 创建对话 - 正常**
```
测试名称：创建新对话成功
前置条件：已登录
请求：
  POST {{base_url}}/conversations
  Headers: Authorization: Bearer {{access_token}}
  Body: {
    "title": "测试对话",
    "pet_id": ""
  }

验证规则:
  ✓ 状态码 = 201
  ✓ 响应体.conversation_id 不为空
  ✓ 响应体.user_id = 当前用户 ID
  ✓ 响应体.message_count = 0

后置操作：保存 conversation_id 到环境变量
```

**用例 2.2: 查询对话列表 - 分页**
```
测试名称：查询对话列表（分页）
前置条件：已登录，存在多个对话
请求：
  GET {{base_url}}/conversations?skip=0&limit=5
  Headers: Authorization: Bearer {{access_token}}

验证规则:
  ✓ 状态码 = 200
  ✓ 响应体为数组
  ✓ 数组长度 <= 5
  ✓ 每个元素包含 conversation_id, title
```

**用例 2.3: 获取对话详情**
```
测试名称：获取对话详情成功
前置条件：已创建对话
请求：
  GET {{base_url}}/conversations/{{conversation_id}}
  Headers: Authorization: Bearer {{access_token}}

验证规则:
  ✓ 状态码 = 200
  ✓ 响应体.conversation_id = {{conversation_id}}
  ✓ 响应体.messages 为数组
  ✓ 响应体.message_count >= 0
```

**用例 2.4: 删除对话**
```
测试名称：删除对话成功
前置条件：已创建测试对话
请求：
  DELETE {{base_url}}/conversations/{{conversation_id}}
  Headers: Authorization: Bearer {{access_token}}

验证规则:
  ✓ 状态码 = 204
  
验证后续:
  - 再次查询该对话应返回 404
```

#### 测试集合 3: AI 对话功能测试

**用例 3.1: 单轮对话**
```
测试名称：AI 单轮对话成功
前置条件：已登录
请求：
  POST {{base_url}}/chat
  Headers: Authorization: Bearer {{access_token}}
  Body: {
    "message": "你好，我想了解狗狗疫苗接种知识"
  }

验证规则:
  ✓ 状态码 = 200
  ✓ 响应体.conversation_id 不为空
  ✓ 响应体.response 不为空
  ✓ 响应体.response 长度 > 10
  ✓ 响应时间 < 5000ms
```

**用例 3.2: 多轮对话 - 上下文保持**
```
测试名称：多轮对话上下文保持
前置条件：已完成第一轮对话

第一轮:
  POST {{base_url}}/chat
  Body: {
    "message": "我的狗叫旺财，今年 2 岁"
  }
  保存返回的 conversation_id

第二轮:
  POST {{base_url}}/chat
  Body: {
    "message": "它需要打什么疫苗？",
    "conversation_id": "{{conversation_id}}"
  }

验证规则:
  ✓ 两轮对话使用相同 conversation_id
  ✓ 第二轮响应包含对"旺财"的上下文理解
  ✓ 响应体提及"狗狗"或"宠物"
```

**用例 3.3: 带宠物上下文的对话**
```
测试名称：指定宠物的个性化对话
前置条件：已创建宠物档案
请求：
  POST {{base_url}}/chat
  Headers: Authorization: Bearer {{access_token}}
  Body: {
    "message": "我的宠物应该吃什么？",
    "pet_id": "{{pet_id}}"
  }

验证规则:
  ✓ 状态码 = 200
  ✓ 响应体.response 包含宠物相关信息
  ✓ 响应体.relevant_context 不为空（可选）
```

#### 测试集合 4: 错误处理测试

**用例 4.1: 未认证访问**
```
测试名称：未登录访问受保护接口
请求：
  POST {{base_url}}/chat
  Headers: (无 Authorization)
  Body: {
    "message": "测试"
  }

验证规则:
  ✓ 状态码 = 401
  ✓ 响应体.detail 包含 "认证" 或 "未授权"
```

**用例 4.2: 无效 Token**
```
测试名称：使用过期/无效 Token
请求：
  POST {{base_url}}/chat
  Headers: Authorization: Bearer invalid_token_12345
  Body: {
    "message": "测试"
  }

验证规则:
  ✓ 状态码 = 401 或 403
  ✓ 响应体.detail 包含 "令牌" 或 "无效"
```

**用例 4.3: 访问他人对话**
```
测试名称：权限隔离测试
前置条件：用户 A 创建了对话
请求：
  用户 B 登录获取 token
  GET {{base_url}}/conversations/{{userA_conversation_id}}
  Headers: Authorization: Bearer {{userB_token}}

验证规则:
  ✓ 状态码 = 403 或 404
  ✓ 响应体.detail 包含 "权限" 或 "不存在"
```

**用例 4.4: 空消息处理**
```
测试名称：发送空消息
请求：
  POST {{base_url}}/chat
  Headers: Authorization: Bearer {{access_token}}
  Body: {
    "message": ""
  }

验证规则:
  ✓ 状态码 = 422 或 200（根据实现）
  ✓ 如返回 200，response 应提示输入有效内容
```

### 3.3 边界条件测试

**用例 3.1: 超长消息**
```
测试名称：处理超长消息（10000 字符）
请求：
  POST {{base_url}}/chat
  Body: {
    "message": "{{random_string_10000}}"
  }

验证规则:
  ✓ 状态码 = 200 或 400（根据设计）
  ✓ 如接受，响应时间 < 10000ms
  ✓ 如拒绝，返回明确错误信息
```

**用例 3.2: 特殊字符**
```
测试名称：消息包含特殊字符
请求：
  POST {{base_url}}/chat
  Body: {
    "message": "测试<script>alert('xss')</script> 中文🎉"
  }

验证规则:
  ✓ 状态码 = 200
  ✓ 响应正常，无 XSS 攻击
  ✓ 特殊字符正确处理
```

**用例 3.3: 并发请求**
```
测试名称：并发多请求测试
场景：使用「自动化测试」→ 「并发模式」
并发数：10
请求：
  同时发送 10 个 POST /chat 请求

验证规则:
  ✓ 所有请求状态码 = 200
  ✓ 平均响应时间 < 3000ms
  ✓ 无 500 错误
```

---

## 四、测试执行步骤

### 4.1 导入接口文档

#### 步骤 1: 准备 OpenAPI 文档
```bash
# 确保 FastAPI 应用运行
cd animal
uvicorn src.main:app --reload
```

#### 步骤 2: 导入到 APIFox
1. 打开 APIFox
2. 选择项目 → 点击「导入」
3. 选择「URL」标签
4. 输入：`http://localhost:8000/openapi.json`
5. 点击「导入」
6. 确认导入成功（应看到所有接口）

### 4.2 创建测试集合

#### 方法 1: 手动创建（推荐）
1. 进入「测试」模块
2. 点击「新建测试集合」
3. 命名：`AI 对话功能完整测试`
4. 从接口列表拖拽接口到测试集合
5. 为每个接口配置测试数据和验证规则

#### 方法 2: 批量生成
1. 进入「接口」模块
2. 选择多个接口（Ctrl+A 全选）
3. 右键 → 「批量生成测试用例」
4. 选择生成策略（正常/边界/错误）
5. 点击「生成」

### 4.3 配置测试数据

#### 使用前置脚本准备数据
```javascript
// 在测试集合的「前置操作」中
// 1. 创建测试用户
const registerReq = {
  url: pm.variables.get("base_url") + "/auth/register",
  method: "POST",
  header: { "Content-Type": "application/json" },
  body: {
    mode: "raw",
    raw: JSON.stringify({
      phone: "13800000099",
      email: "apifox_test@example.com",
      password: "test1234"
    })
  }
};

// 2. 登录获取 Token
pm.sendRequest(registerReq, (err, regRes) => {
  const loginReq = {
    url: pm.variables.get("base_url") + "/auth/login",
    method: "POST",
    header: { "Content-Type": "application/x-www-form-urlencoded" },
    body: {
      mode: "urlencoded",
      urlencoded: [
        { key: "username", value: "13800000099" },
        { key: "password", value: "test1234" }
      ]
    }
  };
  
  pm.sendRequest(loginReq, (err, loginRes) => {
    const token = loginRes.json().access_token;
    pm.environment.set("access_token", token);
    console.log("测试准备完成，Token:", token);
  });
});
```

### 4.4 执行测试

#### 单个接口测试
1. 在「接口」模块找到目标接口
2. 点击「发送」按钮
3. 查看实时响应

#### 测试集合批量执行
1. 进入「测试」模块
2. 选择测试集合
3. 选择环境（开发/测试/生产）
4. 点击「运行」
5. 查看执行进度和结果

#### 自动化测试（定时执行）
1. 进入「自动化测试」 → 「测试计划」
2. 新建测试计划
3. 选择测试集合
4. 配置执行频率（如：每天 9:00）
5. 配置通知方式（邮件/钉钉/企业微信）
6. 点击「保存并启用」

### 4.5 WebSocket 测试

#### 配置 WebSocket 连接
```
接口类型：WebSocket
URL: ws://localhost:8000/api/v1/ws/chat
认证：Bearer Token（在连接时发送）
```

#### 测试步骤
1. 创建 WebSocket 接口
2. 点击「连接」
3. 发送测试消息：
```json
{
  "type": "message",
  "data": {
    "message": "你好，我想咨询宠物健康问题"
  }
}
```
4. 接收响应消息
5. 验证响应格式和内容

#### 验证规则
```javascript
// 在后置脚本中验证
const response = pm.response.json();
pm.test("响应格式正确", () => {
  pm.expect(response).to.have.property("type");
  pm.expect(response.type).to.be.oneOf(["response", "error", "processing"]);
});

pm.test("响应包含有效内容", () => {
  if (response.type === "response") {
    pm.expect(response.data).to.have.property("response");
    pm.expect(response.data.response.length).to.be.above(0);
  }
});
```

---

## 五、测试结果验证

### 5.1 响应状态码验证

#### 常用状态码检查
```javascript
// 在「后置操作」中添加验证脚本

// 检查状态码
pm.test("状态码为 200", () => {
  pm.response.to.have.status(200);
});

// 检查状态码范围
pm.test("状态码为成功状态", () => {
  pm.expect(pm.response.code).to.be.within(200, 299);
});

// 检查特定状态码
pm.test("创建成功返回 201", () => {
  pm.response.to.have.status(201);
});

pm.test("未授权返回 401", () => {
  pm.response.to.have.status(401);
});
```

### 5.2 响应体内容验证

#### JSON 结构验证
```javascript
// 检查字段存在性
pm.test("响应体包含必要字段", () => {
  const jsonData = pm.response.json();
  pm.expect(jsonData).to.have.property("conversation_id");
  pm.expect(jsonData).to.have.property("response");
  pm.expect(jsonData).to.have.property("relevant_context");
});

// 检查字段类型
pm.test("字段类型正确", () => {
  const jsonData = pm.response.json();
  pm.expect(jsonData.conversation_id).to.be.a("string");
  pm.expect(jsonData.response).to.be.a("string");
  pm.expect(jsonData.relevant_context).to.be.a("array");
});

// 检查字段值
pm.test("Token 类型为 bearer", () => {
  const jsonData = pm.response.json();
  pm.expect(jsonData.token_type).to.equal("bearer");
});

// 检查数组长度
pm.test("对话列表不超过限制", () => {
  const jsonData = pm.response.json();
  pm.expect(jsonData).to.be.an("array");
  pm.expect(jsonData.length).to.be.at.most(20);
});

// 检查字符串长度
pm.test("回复内容长度合理", () => {
  const jsonData = pm.response.json();
  pm.expect(jsonData.response.length).to.be.above(10);
  pm.expect(jsonData.response.length).to.be.below(10000);
});
```

#### 嵌套结构验证
```javascript
pm.test("消息列表结构正确", () => {
  const jsonData = pm.response.json();
  pm.expect(jsonData.messages).to.be.an("array");
  
  jsonData.messages.forEach((msg, index) => {
    pm.expect(msg).to.have.property("message_id");
    pm.expect(msg).to.have.property("role");
    pm.expect(msg).to.have.property("content");
    pm.expect(msg.role).to.be.oneOf(["user", "assistant", "system"]);
  });
});
```

### 5.3 响应时间验证

```javascript
// 检查响应时间
pm.test("响应时间小于 2 秒", () => {
  pm.expect(pm.response.responseTime).to.be.below(2000);
});

pm.test("响应时间在合理范围", () => {
  const time = pm.response.responseTime;
  pm.expect(time).to.be.within(100, 5000);
});

// 性能分级验证
pm.test("性能优秀 (<500ms)", () => {
  pm.expect(pm.response.responseTime).to.be.below(500);
});
```

### 5.4 数据一致性验证

```javascript
// 验证返回数据与请求数据一致
pm.test("返回的手机号与请求一致", () => {
  const jsonData = pm.response.json();
  const requestBody = JSON.parse(pm.request.body.raw);
  pm.expect(jsonData.phone).to.equal(requestBody.phone);
});

// 验证时间戳逻辑
pm.test("更新时间不早于创建时间", () => {
  const jsonData = pm.response.json();
  const createdAt = new Date(jsonData.created_at);
  const updatedAt = new Date(jsonData.updated_at);
  pm.expect(updatedAt.getTime()).to.be.at.least(createdAt.getTime());
});

// 验证分页逻辑
pm.test("分页参数正确", () => {
  const jsonData = pm.response.json();
  const queryParams = pm.request.url.query;
  const limit = parseInt(queryParams.get("limit"));
  pm.expect(jsonData.length).to.be.at.most(limit);
});
```

### 5.5 安全性验证

```javascript
// 检查敏感信息不泄露
pm.test("响应不包含密码", () => {
  const responseText = pm.response.text();
  pm.expect(responseText).to.not.include("password");
  pm.expect(responseText).to.not.include("secret");
});

// 检查 CORS 头
pm.test("CORS 头配置正确", () => {
  pm.response.to.have.header("Access-Control-Allow-Origin");
});

// 检查安全头
pm.test("包含安全头", () => {
  pm.response.to.have.header("X-Content-Type-Options");
  pm.response.to.have.header("X-Frame-Options");
});
```

### 5.6 提取数据供后续使用

```javascript
// 提取 Token 到环境变量
pm.test("提取 Access Token", () => {
  const jsonData = pm.response.json();
  pm.environment.set("access_token", jsonData.access_token);
  pm.expect(jsonData.access_token).to.exist;
});

// 提取 ID 供后续接口使用
pm.test("提取 Conversation ID", () => {
  const jsonData = pm.response.json();
  pm.environment.set("current_conversation_id", jsonData.conversation_id);
});

// 提取动态参数
pm.test("提取用户 ID", () => {
  const jsonData = pm.response.json();
  pm.environment.set("test_user_id", jsonData.user_id);
});
```

---

## 六、测试报告生成与分析

### 6.1 查看测试报告

#### 单次执行报告
1. 测试执行完成后，自动跳转到报告页面
2. 查看以下指标：
   - 总用例数
   - 通过数/失败数
   - 通过率
   - 平均响应时间
   - 最长/最短响应时间

#### 历史趋势报告
1. 进入「测试」 → 「测试报告」
2. 选择时间范围
3. 查看趋势图：
   - 每日通过率趋势
   - 响应时间变化趋势
   - 失败用例分布

### 6.2 导出测试报告

#### 导出格式
- PDF 格式（适合汇报）
- HTML 格式（适合在线查看）
- JSON 格式（适合数据分析）
- Markdown 格式（适合文档归档）

#### 导出步骤
1. 在测试报告页面点击「导出」
2. 选择格式
3. 选择时间范围
4. 点击「导出」

### 6.3 分析报告指标

#### 关键指标解读
```
通过率 = 通过用例数 / 总用例数 × 100%
  - 优秀：> 95%
  - 良好：> 85%
  - 合格：> 70%
  - 需改进：< 70%

平均响应时间
  - 优秀：< 500ms
  - 良好：< 1000ms
  - 合格：< 2000ms
  - 需优化：> 2000ms

失败用例分布
  - 按接口分组：找出问题集中的模块
  - 按错误类型：分析是参数问题、逻辑问题还是性能问题
```

### 6.4 问题定位与调试

#### 查看失败详情
1. 在报告中点击失败用例
2. 查看：
   - 请求详情（URL、Headers、Body）
   - 响应详情（Status、Headers、Body）
   - 验证失败的具体规则
   - 控制台日志

#### 复现问题
1. 点击「重新运行」
2. 或点击「在接口中打开」
3. 修改参数后重新测试

#### 添加调试日志
```javascript
// 在前置或后置脚本中
console.log("请求 URL:", pm.request.url.toString());
console.log("请求体:", pm.request.body.raw);
console.log("响应时间:", pm.response.responseTime);
console.log("响应体:", pm.response.json());

// 输出到控制台，便于调试
```

### 6.5 生成质量评估报告

#### 模板示例
```markdown
# API 测试质量报告

## 测试概况
- 测试时间：2026-04-10 14:00-15:30
- 测试环境：开发环境 (localhost:8000)
- 测试人员：AI 算法工程师
- 测试集合：AI 对话功能完整测试

## 测试结果
- 总用例数：45
- 通过数：43
- 失败数：2
- 通过率：95.6%

## 性能指标
- 平均响应时间：856ms
- 最快响应：120ms
- 最慢响应：3200ms
- P95 响应时间：1800ms

## 问题分析

### 失败用例 1: 多轮对话上下文保持
- 失败原因：第二轮对话未正确关联 conversation_id
- 严重等级：高
- 建议修复：检查 Agent.chat() 方法的 conversation_id 参数传递

### 失败用例 2: 超长消息处理
- 失败原因：10000 字符消息导致超时（>10s）
- 严重等级：中
- 建议修复：添加消息长度限制或优化处理性能

## 改进建议
1. 优化 Agent 响应速度，目标 P95 < 1500ms
2. 添加消息长度验证（建议上限 5000 字符）
3. 增强错误提示信息，便于前端展示
4. 考虑添加请求限流保护

## 质量评级
综合评分：A- (95.6 分)
- 功能完整性：A
- 性能表现：B+
- 错误处理：A
- 安全性：A
```

---

## 七、自动化测试配置

### 7.1 创建自动化测试计划

#### 步骤
1. 进入「自动化测试」 → 「测试计划」
2. 点击「新建测试计划」
3. 配置基本信息：
   - 名称：`每日回归测试`
   - 描述：每天自动执行核心功能测试
   - 负责人：测试工程师

4. 选择测试集合：
   - 勾选 `AI 对话功能完整测试`
   - 勾选 `错误处理测试`

5. 配置执行策略：
   - 执行频率：每天
   - 执行时间：09:00
   - 时区：UTC+8 (北京)

6. 配置通知：
   - 邮件通知：test-team@company.com
   - 钉钉机器人：https://oapi.dingtalk.com/robot/send?access_token=xxx
   - 失败时通知：是

7. 点击「保存并启用」

### 7.2 CI/CD集成

#### GitHub Actions 示例
```yaml
# .github/workflows/api-test.yml
name: API 自动化测试

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  apifox-test:
    runs-on: ubuntu-latest
    
    steps:
    - name: 启动 FastAPI 服务
      run: |
        cd animal
        pip install -r requirements.txt
        uvicorn src.main:app --host 0.0.0.0 --port 8000 &
        sleep 10
    
    - name: 运行 APIFox 测试
      uses: apifox/apifox-github-action@v1
      with:
        project-id: ${{ secrets.APIFOX_PROJECT_ID }}
        token: ${{ secrets.APIFOX_TOKEN }}
        test-suite-id: ${{ secrets.TEST_SUITE_ID }}
        environment: dev
    
    - name: 上传测试报告
      uses: actions/upload-artifact@v3
      with:
        name: api-test-report
        path: apifox-report.html
```

#### Jenkins 集成
```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('启动服务') {
            steps {
                sh 'cd animal && uvicorn src.main:app --host 0.0.0.0 --port 8000 &'
                sh 'sleep 10'
            }
        }
        
        stage('APIFox 测试') {
            steps {
                script {
                    def apifoxResult = sh(
                        script: 'apifox-cli run --project-id=xxx --suite-id=xxx',
                        returnStatus: true
                    )
                    
                    if (apifoxResult != 0) {
                        error('API 测试失败')
                    }
                }
            }
        }
        
        stage('生成报告') {
            steps {
                sh 'apifox-cli export-report --format=html --output=report.html'
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: '.',
                    reportFiles: 'report.html',
                    reportName: 'API 测试报告'
                ])
            }
        }
    }
    
    post {
        always {
            echo '测试完成'
        }
        failure {
            mail to: 'team@example.com',
                 subject: "API 测试失败 - ${env.BUILD_NUMBER}",
                 body: "请查看：${env.BUILD_URL}/api%20测试报告/"
        }
    }
}
```

### 7.3 命令行工具集成

#### 安装 APIFox CLI
```bash
npm install -g @apifox/cli
```

#### 命令行执行测试
```bash
# 登录
apifox login --token YOUR_TOKEN

# 运行测试集合
apifox run --project-id=123456 --suite-id=789012 --environment=dev

# 导出报告
apifox export-report \
  --project-id=123456 \
  --format=html \
  --output=./reports/test-report.html

# 查看帮助
apifox --help
```

---

## 八、常见问题与解决方案

### 8.1 认证问题

#### 问题 1: Token 过期
**现象**: 测试执行到一半提示 401 未授权

**解决方案**:
```javascript
// 在每个接口的前置操作中添加 Token 检查
const token = pm.environment.get("access_token");
if (!token) {
  // 自动重新登录获取 Token
  const loginReq = {
    url: pm.variables.get("base_url") + "/auth/login",
    method: "POST",
    body: { /* 登录参数 */ }
  };
  
  pm.sendRequest(loginReq, (err, res) => {
    pm.environment.set("access_token", res.json().access_token);
  });
}
```

#### 问题 2: Token 未正确传递
**现象**: 所有受保护接口返回 401

**检查清单**:
- [ ] 环境变量中是否存在 access_token
- [ ] 接口请求头是否正确配置 `Authorization: Bearer {{access_token}}`
- [ ] 登录接口后置脚本是否正确提取 Token

### 8.2 数据依赖问题

#### 问题：测试用例相互依赖
**现象**: 第一个用例失败导致后续全部失败

**解决方案**:
```javascript
// 在每个用例的前置操作中准备独立数据
// 例如：每个测试创建独立用户，而非共用用户

const timestamp = Date.now();
pm.environment.set("test_phone", `1380000${timestamp}`);

// 请求中使用
{
  "phone": "{{test_phone}}",
  "email": "test_{{test_phone}}@example.com"
}
```

### 8.3 环境问题

#### 问题：跨环境配置不一致
**解决方案**:
1. 使用环境变量隔离：
```
开发环境：{{base_url}} = http://localhost:8000/api/v1
测试环境：{{base_url}} = https://test-api.com/api/v1
生产环境：{{base_url}} = https://api.com/api/v1
```

2. 在接口中使用变量而非硬编码：
```
❌ http://localhost:8000/api/v1/chat
✅ {{base_url}}/chat
```

### 8.4 性能问题

#### 问题：测试执行缓慢
**优化方案**:
1. 减少不必要的等待时间
2. 使用并发模式执行独立用例
3. 批量接口合并请求
4. 优化数据库查询（针对后端）

```javascript
// 在测试集合级别配置并发
// 自动化测试 → 测试计划 → 高级设置
并发模式：启用
最大并发数：10
```

### 8.5 WebSocket 测试问题

#### 问题：连接不稳定
**解决方案**:
```javascript
// 添加重连机制
let reconnectCount = 0;
const maxReconnects = 3;

function connect() {
  pm.websocket.connect(wsUrl, () => {
    console.log("WebSocket 连接成功");
  });
}

pm.websocket.onClose(() => {
  if (reconnectCount < maxReconnects) {
    reconnectCount++;
    console.log(`连接断开，${reconnectCount}秒后重连...`);
    setTimeout(connect, reconnectCount * 1000);
  }
});

connect();
```

---

## 附录：测试检查清单

### 测试前检查
- [ ] FastAPI 服务已启动
- [ ] 数据库连接正常
- [ ] 环境变量配置正确
- [ ] APIFox 项目已创建
- [ ] 接口文档已导入
- [ ] 测试集合已创建
- [ ] 测试数据已准备

### 测试中监控
- [ ] 实时查看测试执行进度
- [ ] 关注失败用例详情
- [ ] 记录异常响应时间
- [ ] 检查控制台日志
- [ ] 验证数据提取正确

### 测试后验证
- [ ] 查看测试报告
- [ ] 分析失败原因
- [ ] 生成质量评估
- [ ] 导出测试报告
- [ ] 发送团队通知
- [ ] 更新问题追踪系统

---

**文档版本**: v1.0  
**更新日期**: 2026-04-10  
**维护人**: AI 算法工程师  
**适用范围**: AI 宠物健康助手项目
