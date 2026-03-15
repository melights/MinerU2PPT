# 项目初始化蓝图模板

> 使用方式：先输出“草案版”，经用户审批后再落地到 `CLAUDE.md`。

## 1. 项目约束清单（Project Guardrails）

- 项目类型：
- 目标平台：
- 主要技术栈：
- 非功能目标（可靠性/性能/安全/可维护性）：
- 明确非目标（Out of Scope）：

## 2. 架构边界与依赖规则

### 2.1 分层模型
- 采用分层：`presentation -> application -> domain <- infrastructure`
- 组合根：`app/container`

### 2.2 依赖规则（允许/禁止）
- 允许：
- 禁止：

### 2.3 各层职责
- presentation：
- application：
- domain：
- infrastructure：

## 3. 核心规则与约束

### 3.1 命名与模块组织
- 命名规则：
- 模块拆分规则：

### 3.2 编程范式决策（必填）
- 语言：
- 选择：全 OOP / 混合范式 / 过程式优先
- 说明：为何采用该范式，哪些模块例外
- 约束：代码评审与重构时如何判定是否违背范式约束

### 3.3 错误模型
- 错误结构：`code/message/stage/details`
- 错误映射规则：

### 3.4 状态机
- 核心状态：
- 合法迁移：
- 非法迁移处理：

### 3.5 安全边界
- 输入校验边界：
- 外部依赖 allowlist：
- 敏感信息处理：

## 4. 技术选型（推荐 + 备选 + 取舍）

### 4.1 Web/API 框架
- 推荐：
- 备选：
- 取舍：

### 4.2 数据层（数据库/缓存）
- 推荐：
- 备选：
- 取舍：

### 4.3 异步/消息（如适用）
- 推荐：
- 备选：
- 取舍：

### 4.4 测试与质量工具
- 推荐：
- 备选：
- 取舍：

## 5. 测试分层与边界

- Unit：覆盖范围与禁用项
- Integration：覆盖范围与依赖策略
- Functional/E2E：触发策略
- 覆盖率门禁：

## 6. CI 与质量门禁

- lint 命令：
- type-check 命令：
- test 命令：
- architecture-check 命令：
- coverage gate：
- 失败条件：

## 7. 建议目录结构

```text
src/
  presentation/
  application/
  domain/
  infrastructure/
  app/
tests/
  unit/
  integration/
  functional/
```

## 8. 首批任务拆解（按优先级）

1. 建立基础目录与组合根
2. 建立架构导入规则测试
3. 落地统一错误模型与状态机
4. 建立测试脚手架与示例测试
5. 配置 CI 质量门禁

## 9. CLAUDE.md 写入计划

- 将以下章节写入或更新到项目根 `CLAUDE.md`：
  - `## Development Commands`
  - `## Testing Conventions`
  - `## Architecture & Structure`
  - `## Layered Architecture Requirements (Strict)`
  - `## Quality Gates`
