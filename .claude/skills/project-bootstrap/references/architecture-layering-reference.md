# 架构分层参考（可裁剪）

## 适用场景

用于项目初始化阶段快速建立“可执行的分层边界”，避免后续跨层重构。

## 推荐分层

```
presentation -> application -> domain <- infrastructure
                         ^
                    app/container（组合根）
```

说明：
- `presentation`：协议适配层（HTTP/MCP/CLI/Message Handler），只做入参解析、调用应用服务、出参映射。
- `application`：编排层（Use Case / Service / Coordinator），只依赖 domain 抽象，不依赖具体基础设施。
- `domain`：核心业务规则、实体、值对象、领域服务、端口（port）定义。
- `infrastructure`：基础设施实现（DB/HTTP/Browser/Cache/Queue/Filesystem），实现 domain port。
- `app/container`：组合根，负责依赖注入与对象装配。

## 依赖方向（强约束）

允许：
- presentation -> application -> domain
- infrastructure -> domain
- app/container -> presentation/application/domain/infrastructure

禁止：
- infrastructure -> application
- application -> infrastructure
- presentation -> infrastructure（除非经过 container 注入）
- domain -> 任何外层

## 每层职责边界

### presentation
- 做：请求校验、schema 归一化、调用应用层、错误映射。
- 不做：业务规则判断、直接访问数据库/浏览器。

### application
- 做：用例编排、事务边界、跨组件协同、结果组装。
- 不做：直接 new 基础设施实现、处理协议细节。

### domain
- 做：业务不变量、领域模型、错误语义、端口接口。
- 不做：框架绑定、I/O 细节。

### infrastructure
- 做：外部系统对接与 port 实现。
- 不做：承载业务流程编排。

## 组合根与注入规范

- 具体实现只允许在 `app/container` 绑定。
- application 服务构造函数只接收 port/interface，不接收具体 adapter 类型。
- route/handler 从应用上下文（如 `request.app[...]`）拿 service，不依赖模块级单例。

## 错误模型建议

统一错误对象（示例）：
- `code`: 稳定机器可读错误码（如 `INVALID_INPUT`, `TASK_NOT_FOUND`）
- `message`: 面向开发/用户的可读信息
- `stage`: 错误发生阶段（`validate|orchestrate|external|persist`）
- `details`: 可选结构化细节

边界建议：
- presentation 负责把 domain/application 错误映射到协议响应。
- domain 不感知 HTTP 状态码。

## 状态机建议

- 对异步任务统一定义有限状态：
  - `pending -> running -> succeeded|failed`
- 约束：
  - 只允许单向迁移
  - 每次迁移更新 `updated_at`
  - 失败必须有结构化 error

## 安全边界最小集

- 输入只在系统边界做校验（route/schema/consumer）。
- 文件路径拼接前做 ID allowlist 校验。
- 不在日志中输出密钥/token/敏感原文。
- 外部 URL 必须校验 scheme/host allowlist。

## 架构规则测试（建议）

可用测试守护 import 规则：
- `tests/unit/test_architecture_import_rules.py`

示例规则：
- 禁止 `src/infrastructure` import `src/application`
- 禁止 `src/application` import `src/infrastructure`
- 禁止 `src/presentation` import `src/infrastructure`

## 裁剪原则

- 先保留“方向正确 + 规则可测”的最小集合。
- 不提前引入复杂 DDD 战术模式（聚合/领域事件）除非当前需求确实需要。
