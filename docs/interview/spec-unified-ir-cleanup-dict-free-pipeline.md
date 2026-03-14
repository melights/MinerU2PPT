# Feature Brief: Unified IR Cleanup Order and Dict-Free IR Pipeline

## 1. Overview
当前 clean up 逻辑分散在不同阶段，且 IR 在 normalize_element_ir 之后仍存在 dict 形态，导致处理顺序不直观、类型边界不清晰。该特性旨在统一 clean up 的执行顺序（先 text 对 background 与 image，再 image 对 background），并在全仓库范围内强制 normalize_element_ir 之后仅使用强类型 IR（不再用 dict 表示 IR）。同时，ImageIR 需保存裁剪后的像素副本以支撑局部 clean up 一致化处理。

## 2. Goals
- 在全仓库范围内实现 normalize_element_ir 之后 **IR 表示统一为强类型对象**，禁止 dict 作为 IR 载体。
- 将 clean up 执行顺序统一为：
  1) text → background
  2) text → image
  3) image → background
- 将 text 与 image 的 clean up 逻辑按同一处理阶段组织，避免分散和重复分支。
- ImageIR 保存裁剪像素副本，支持在 IR 层完成 image 内文本相关 clean up。
- 通过“类型门禁 + 测试门禁”双重验收，确保规则可持续执行。

## 3. User Stories

- **US-001: 统一 clean up 顺序**
  - **As a** 转换流程维护者, **I want to** clean up 顺序固定且集中, **so that I can** 避免图层/遮盖相关的回归问题。
  - **Acceptance Criteria:**
    - [ ] 对任一页面，clean up 顺序可被验证为 text→background/image，再 image→background。
    - [ ] clean up 相关处理不再分散在多个无序阶段。

- **US-002: 去除 dict IR**
  - **As a** 架构维护者, **I want to** normalize_element_ir 后只使用强类型 IR, **so that I can** 保证类型一致性和可维护性。
  - **Acceptance Criteria:**
    - [ ] normalize_element_ir 之后的处理链路不再接收或返回 dict 形态 IR。
    - [ ] 相关调用点和中间处理节点均以 IR 类型对象传递。

- **US-003: ImageIR 持有像素副本**
  - **As a** 渲染逻辑维护者, **I want to** ImageIR 携带裁剪像素副本, **so that I can** 在同一逻辑域内完成 text→image 的 clean up。
  - **Acceptance Criteria:**
    - [ ] ImageIR 数据结构包含可用的裁剪像素字段。
    - [ ] text→image clean up 使用 ImageIR 像素副本完成，不依赖零散外部临时结构。

- **US-004: 强制门禁**
  - **As a** 代码审查者, **I want to** 类型与测试双门禁, **so that I can** 阻止 dict IR 回流和顺序退化。
  - **Acceptance Criteria:**
    - [ ] 类型门禁可阻止 normalize_element_ir 后 dict IR 的引入。
    - [ ] 单测/集成测试能覆盖 clean up 顺序与 IR 统一约束。

## 4. Functional Requirements
- **FR-1**: 系统必须定义并使用统一的 IR 类型体系（含 TextIR、ImageIR 等），作为 normalize_element_ir 之后唯一 IR 载体。
- **FR-2**: normalize_element_ir 必须输出强类型 IR，不得输出 dict 形态 IR。
- **FR-3**: normalize_element_ir 之后所有流程节点（转换、合并、渲染前处理、测试辅助流程）必须以 IR 类型对象交互。
- **FR-4**: clean up 流程必须按固定顺序执行：text→background、text→image、image→background。
- **FR-5**: text→background 与 text→image 处理必须在同一逻辑阶段内组织，保证策略一致。
- **FR-6**: ImageIR 必须包含裁剪像素副本字段，并供 text→image clean up 使用。
- **FR-7**: image→background clean up 必须在 text 相关 clean up 完成后执行。
- **FR-8**: 系统必须提供可自动化验证的类型门禁，阻止 normalize_element_ir 后 dict IR 使用。
- **FR-9**: 系统必须提供测试门禁，覆盖 clean up 顺序、ImageIR 像素副本参与处理、以及 dict IR 禁止规则。
- **FR-10**: 对外输入（如 JSON）可为 dict，但一旦进入 normalize_element_ir 后流程，必须转换为 IR 类型对象。

## 5. Non-Goals (Out of Scope)
- 不改动 OCR 识别算法本身及识别阈值策略。
- 不改动与该特性无关的 UI/CLI 交互设计。
- 不引入与本特性无关的性能优化或大规模重构。
- 不改变外部输入文件格式（例如 MinerU JSON 的源格式）。

## 6. Success Metrics
- **SM-1**: normalize_element_ir 后链路中，dict 形态 IR 使用数为 **0**（全仓库范围）。
- **SM-2**: clean up 顺序相关测试通过率 **100%**（新增与既有相关用例）。
- **SM-3**: ImageIR 像素副本相关测试通过率 **100%**（包含 text→image 路径）。
- **SM-4**: 类型门禁在 CI 中启用并为强制项，违反规则时构建必须失败（阻断合并）。
- **SM-5**: 回归测试中不出现因 clean up 顺序变化导致的新增渲染错误（以现有基线样例验证）。

## 7. Open Questions
1. ImageIR 像素副本的生命周期与释放策略是否需要统一规范（避免多页/大图内存峰值问题）？
2. “全仓库强制”是否包含所有测试 fixture 的历史格式迁移，还是允许输入层 fixture 保持 dict、仅限制 normalize 后链路？
3. 类型门禁的实现方式是否指定为静态类型检查、AST 规则、或两者组合？
4. 对于第三方适配层临时结构，是否要求在进入 normalize_element_ir 前完成全部映射，禁止下游透传？
