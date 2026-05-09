# APIFox 测试快速参考卡片

## 🚀 快速开始（5 分钟上手）

### 步骤 1: 启动服务
```bash
cd animal
uvicorn src.main:app --reload
```

### 步骤 2: 导入接口文档
```
1. 打开 APIFox
2. 新建项目 → AI 宠物健康助手
3. 导入 → URL → http://localhost:8000/openapi.json
4. 确认导入
```

### 步骤 3: 配置环境
```
环境管理 → 新增环境
名称：开发环境
变量：base_url = http://localhost:8000/api/v1
```

### 步骤 4: 运行测试
```
测试模块 → 选择测试集合 → 运行
```

---

## 📋 核心接口速查

### 认证接口
| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 用户注册 | POST | /auth/register | 创建新用户 |
| 用户登录 | POST | /auth/login | 获取 Token |
| Token 刷新 | POST | /auth/refresh | 刷新 Token |

### 对话接口
| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| AI 对话 | POST | /chat | 与 AI 助手对话 |
| 创建对话 | POST | /conversations | 新建对话 |
| 对话列表 | GET | /conversations | 查询列表 |
| 对话详情 | GET | /conversations/{id} | 查看详情 |
| 删除对话 | DELETE | /conversations/{id} | 删除对话 |

---

## 🔧 常用验证规则

### 状态码验证
```javascript
pm.test("状态码 200", () => {
  pm.response.to.have.status(200);
});
```

### 响应体验证
```javascript
pm.test("包含必要字段", () => {
  const data = pm.response.json();
  pm.expect(data).to.have.property("conversation_id");
});
```

### 响应时间验证
```javascript
pm.test("响应时间<2s", () => {
  pm.expect(pm.response.responseTime).to.be.below(2000);
});
```

---

## 🎯 测试用例模板

### 正常流程测试
```
1. 用户注册 → 201
2. 用户登录 → 200，提取 Token
3. 创建对话 → 201，提取 ID
4. AI 对话 → 200
5. 查询列表 → 200
6. 删除对话 → 204
```

### 错误处理测试
```
1. 未认证访问 → 401
2. 无效 Token → 401
3. 资源不存在 → 404
4. 参数错误 → 422
```

---

## 💡 实用技巧

### 1. 自动获取 Token
在前置操作中添加：
```javascript
const loginReq = {
  url: pm.variables.get("base_url") + "/auth/login",
  method: "POST",
  body: { username: "test", password: "1234" }
};
pm.sendRequest(loginReq, (err, res) => {
  pm.environment.set("access_token", res.json().access_token);
});
```

### 2. 提取响应数据
在后置操作中添加：
```javascript
const data = pm.response.json();
pm.environment.set("conversation_id", data.conversation_id);
```

### 3. 批量运行
```
测试集合 → 右键 → 运行
选择环境 → 点击运行
```

### 4. 查看报告
```
测试报告 → 选择日期 → 导出
格式：PDF/HTML/JSON
```

---

## 🐛 常见问题

### Q1: 401 未授权
**解决**: 检查 Token 是否过期，重新登录获取

### Q2: 404 资源不存在
**解决**: 检查 ID 是否正确，环境变量是否设置

### Q3: 响应超时
**解决**: 增加超时时间或优化后端性能

### Q4: 测试用例相互依赖
**解决**: 每个用例使用独立测试数据

---

## 📊 测试检查清单

### 测试前
- [ ] 服务已启动
- [ ] 数据库连接正常
- [ ] 环境变量配置
- [ ] 接口文档导入

### 测试中
- [ ] 监控执行进度
- [ ] 查看失败详情
- [ ] 记录异常数据

### 测试后
- [ ] 查看测试报告
- [ ] 分析失败原因
- [ ] 导出测试报告
- [ ] 通知团队成员

---

## 🔗 相关资源

### 文档
- [APIFox 官方文档](https://www.apifox.cn/help/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [项目 API 文档](./APIFox 接口测试指南.md)

### 工具
- APIFox CLI: `npm install -g @apifox/cli`
- Postman (备选)
- Swagger UI: http://localhost:8000/docs

---

## 📞 技术支持

**项目群组**: AI 宠物健康助手开发群  
**文档维护**: AI 算法工程师  
**最后更新**: 2026-04-10

---

**打印建议**: A4 纸张，横向排版，便于快速查阅
