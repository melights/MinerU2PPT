---
name: project-bootstrap
description: 手工调用的项目初始化技能：通过中文澄清与迭代，生成并落地工程蓝图（docs），再将高频编码规则同步到 CLAUDE.md 并添加蓝图引用。
argument-hint: "[项目类型/语言/框架偏好，可选]"
user-invocable: true
disable-model-invocation: true
---

# 项目初始化蓝图生成器（手工触发）

仅在用户**手工调用** `/project-bootstrap` 时执行。不要自动触发。

## 目标

在项目初始化阶段建立“最小但关键”的工程护栏：先沉淀完整蓝图到 `docs/`，再把编码高频规则写入 `CLAUDE.md`，并在 `CLAUDE.md` 增加蓝图引用。

## 何时使用

- 新项目启动，需要先定架构、规则、测试与 CI
- 老项目准备补齐工程基础规范
- 希望把技术选型与架构决策沉淀为可执行规则

## 输入与澄清

1. 读取技能参数与最近对话。
2. 若关键信息不足，使用 `AskUserQuestion` 分批提问（每轮 1-3 个问题）。
3. 必须优先澄清：
   - 项目类型（API/爬虫/前端/全栈/任务处理）
   - 语言与框架偏好
   - 数据存储与消息需求
   - 运行环境（本地/容器/云）
   - 非功能目标（安全/性能/可维护性）
   - 编程范式偏好（尤其 Python：是否要求“全 OOP”）
4. 若技术栈包含 Python，必须显式询问并记录：
   - 是否采用全 OOP（类/对象为主）
   - 或采用混合范式（函数式 + 面向对象）
   - 或采用过程式优先（脚本化）
5. 该决策必须进入蓝图与 `CLAUDE.md`，作为后续编码约束。

## 技术栈推荐（必须提供）

在输出草案时，必须给出“推荐方案 + 备选方案 + 取舍理由”，至少覆盖：
- Web/API 框架
- 数据库/缓存
- 异步任务或消息组件（如需要）
- 测试框架与分层
- 代码质量工具（lint/type/format）

推荐格式：
- 推荐：`<方案>`
- 备选：`<方案A>/<方案B>`
- 取舍：`为什么选推荐，代价是什么`

## 参考资料加载规则

- 生成蓝图草案前，优先阅读：
  - `references/blueprint-template.md`
- 当需要定义或裁剪分层边界时，阅读：
  - `references/architecture-layering-reference.md`
- 若用户已明确给出不同分层约束，以用户约束为准，并在草案中标注差异。

## 工作流（强制）

### 1) 输出“蓝图草案”（不得直接定稿）

草案必须包含：
1. 架构边界与依赖方向（如 `presentation -> application -> domain <- infrastructure`）
2. 核心规则（命名、错误模型、状态机、安全边界、输入校验边界、编程范式约束）
3. 技术选型决策（推荐/备选/取舍）
4. 测试分层边界（unit/integration/functional）与覆盖率门禁
5. CI 质量门禁（lint/type/test/架构依赖检查）
6. 首批任务拆解（按优先级）

### 2) 迭代修订（必须）

- 明确告诉用户当前是“草案”。
- 根据反馈持续修订，直到用户明确批准。
- 用户最新约束优先级最高。

### 3) 审批后先落地蓝图到 `docs/`（必须）

仅在用户明确同意后执行写入：

- 蓝图目标目录：`docs/bootstrap/`
- 蓝图文件名规则（优先级从高到低）：
  1. 用户显式指定路径/命名 -> 按用户要求
  2. 未指定时默认固定为：`architecture-bootstrap.md`
  3. 若用户明确要求按范围区分，可使用：`<scope>-bootstrap.md`
- 推荐团队默认使用固定文件名，便于统一引用与检索。

写入内容必须基于已批准草案，且结构完整。

### 4) 再同步“编码高频规则”到 `CLAUDE.md`（必须）

- 目标文件：项目根目录 `CLAUDE.md`
- 若文件已存在：**只更新/补充相关章节，保留无关内容**
- 若文件不存在：创建最小可用 `CLAUDE.md`

`CLAUDE.md` 至少写入：
1. `## Development Commands`
   - 本地启动命令
   - 常用开发命令
2. `## Testing Conventions`
   - 测试分层定义
   - 统一测试入口与专项测试命令
3. `## Architecture & Structure`
   - 分层说明与模块职责
   - 编程范式决策（如 Python 全 OOP/混合/过程式）
4. `## Layered Architecture Requirements (Strict)`
   - 依赖方向
   - 禁止导入规则
   - 组合根/注入约束
5. `## Quality Gates`
   - lint/type/test/coverage/architecture-check 的准入要求
6. `## Blueprint References`
   - 默认指向 `docs/bootstrap/architecture-bootstrap.md`
   - 若采用范围化命名，则指向对应 `docs/bootstrap/<scope>-bootstrap.md`
   - 如存在 ADR 目录，可补充 ADR 索引路径

命令必须是可执行的具体命令，不要写空泛描述。

## 交付检查清单

在请求用户最终确认前，核对：
- [ ] 是否给出推荐技术栈与备选取舍
- [ ] 是否定义清晰的分层依赖与禁止导入
- [ ] 是否包含统一错误模型与关键状态机约束
- [ ] 是否已确认并记录编程范式决策（含 Python 是否全 OOP）
- [ ] 是否将完整蓝图写入 `docs/bootstrap/`
- [ ] 是否将高频编码规则同步到 `CLAUDE.md`
- [ ] 是否在 `CLAUDE.md` 中添加蓝图引用
- [ ] 是否给出可直接运行的开发/测试命令
- [ ] 是否定义 CI 质量门禁（含失败条件）
- [ ] 是否有首批任务拆解

## 输出约束

- 不在本技能内直接实现业务功能代码。
- 不跳过“草案 -> 审批 -> 写入 docs 蓝图 -> 回填 CLAUDE.md 引用”流程。
- 输出必须可执行、可检查、可落地，避免空泛原则。
