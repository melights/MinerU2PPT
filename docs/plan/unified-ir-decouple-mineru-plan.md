# Technical Blueprint: 统一IR解耦MinerU（Text/Image双类型，多Adapter统一合并）

**Functional Spec:** `docs/interview/spec-unified-ir-decouple-mineru.md`

## 1. Technical Approach Overview

本期采用“**多解析源 Adapter -> 统一 IR -> 统一 IR Merge -> 双通道渲染(text/image)**”的目标架构，核心变更如下：

- OCR 不再是 MinerU 后处理，而是**独立解析源**：
  - `MinerUAdapter`: MinerU JSON -> IR
  - `OCRAdapter`: OCR结果 -> IR
- 合并不再是“MinerU + OCR 专用逻辑”，而是**对所有 Adapter 产出的 IR 做统一合并**。
- Generator 只消费 merged IR，不再读取 MinerU 原始结构（`para_blocks/images/tables/discarded_blocks`）。

当前耦合证据与改造目标：
- `converter/generator.py:838-903` 当前入口直接解析 MinerU 结构 -> 改为“加载页面 -> 调用 adapters -> IR merge -> render”。
- `converter/generator.py:760-767` 当前按 list/title/table 等分流 -> 改为仅 `text|image`。
- `converter/generator.py:790-810` 当前 OCR 提取后立即走 MinerU 结构合并 -> 改为 Adapter 产出 IR 后统一 merge。
- `converter/ocr_merge.py:313-425` 当前 merge 深度依赖 MinerU list/block -> 拆分为通用 IR merge 逻辑。

实现阶段：
1. 新增 IR 模型与校验。
2. 新增 MinerUAdapter 与 OCRAdapter（OCR升格为解析源）。
3. 新增 IRMerger（统一合并所有 Adapter 输出）。
4. 改 generator/render 全链路只消费 merged IR。
5. 更新测试与回归 demo。

已确认约束（保持不变）：
- `order` 兜底固定为“先 y 后 x”。
- `group_id` 允许 Adapter 生成 + merge 阶段补写。
- `style` 最小字段：`bold` / `font_size` / `align`。
- 第二解析源（如 PP-Structure）不纳入第一期。
- 第一期开关与 CLI/GUI 用户行为保持兼容。

## 2. File Impact Analysis

- **Created:**
  - `converter/ir.py`（IR模型、校验器、排序兜底）
  - `converter/adapters/mineru_adapter.py`（MinerU -> IR）
  - `converter/adapters/ocr_adapter.py`（OCR -> IR）
  - `converter/ir_merge.py`（多Adapter IR统一合并）
  - `tests/unit/test_ir.py`
  - `tests/unit/test_mineru_adapter.py`
  - `tests/unit/test_ocr_adapter.py`
  - `tests/unit/test_ir_merge.py`

- **Modified:**
  - `converter/generator.py`
    - 删除对 MinerU 原始结构直接依赖（现状 `838-903`）
    - `process_page` 输入改为 merged IR（仅 text/image）
    - OCR接入改为通过 OCRAdapter，而非专用 merge 路径（现状 `790-810`）
  - `converter/ocr_merge.py`
    - 保留 OCR 引擎初始化、OCR bbox refine 等 OCR 专属能力
    - 移除/下沉 MinerU 结构耦合 merge（现状 `313-425`）
  - `main.py`（参数保持兼容，内部调用切到 IR 流程）
  - `gui.py`（保持 UI 行为，内部调用切到 IR 流程）
  - `tests/unit/test_ocr_merge.py`（按拆分后职责重写/精简）
  - `tests/integration/test_generator_ocr_merge.py`（改为多Adapter IR merge链路验证）
  - `tests/integration/test_cli_ocr_option.py`（保持参数兼容断言）

- **Deleted:**
  - 暂不删除外部入口 API；迁移完成后清理旧的 MinerU 结构分支与死代码。

## 3. Task Breakdown by User Story

### US-001: 多源解析统一接入
**Business Acceptance Criteria:**
- 系统存在明确 IR 结构定义与字段约束。
- 下游模块不再读取 MinerU 原始结构字段。
- MinerU 输出可稳定映射为 IR 并驱动完整流程。

**Technical Tasks:**
- [ ] **T-001.1 (IR Core)**: 在 `converter/ir.py` 定义 `DocumentIR/PageIR/ElementIR`（仅 `text|image`）。
- [ ] **T-001.2 (MinerU Adapter)**: 实现 MinerU JSON -> IR，处理 `discarded`、`group_id`、`order`、`style`。
- [ ] **T-001.3 (OCR Adapter)**: 实现 OCR结果 -> IR（包含 `source=ocr` 的 provenance 与 style 推导）。
- [ ] **T-001.4 (Validation/Normalization)**: 统一坐标系、bbox 合法性校验、默认排序字段补全。

### US-002: 下游逻辑简化为双通道渲染
**Business Acceptance Criteria:**
- 渲染入口仅按 `type in {text, image}` 分流。
- `table/title/list` 不作为独立渲染类型。
- `style` 字段可用于文本样式控制。

**Technical Tasks:**
- [ ] **T-002.1 (Generator API)**: 改 `converter/generator.py` 页面流程为 IR 输入。
- [ ] **T-002.2 (Render Branch)**: 移除 `list/title/table/...` 分流，统一 text/image 渲染通道。
- [ ] **T-002.3 (Legacy Removal)**: 下线 `_process_list` 与 image nested block 的 MinerU 专用路径。
- [ ] **T-002.4 (Style Wiring)**: 渲染优先读取 IR style（bold/font_size/align），OCR推导逻辑作为兜底。

### US-003: 迁移期稳定可回归
**Business Acceptance Criteria:**
- CLI 参数与主流程兼容。
- GUI 无结构性改版。
- 既有测试通过，新增 IR 相关测试通过。

**Technical Tasks:**
- [ ] **T-003.1 (IR Merger Core)**: 新增 `converter/ir_merge.py`，实现“多Adapter输出统一合并”。
- [ ] **T-003.2 (Merge Rules)**: 统一规则：`group_id` 优先，几何重叠 + `order` 兜底；不依赖单一来源结构。
- [ ] **T-003.3 (Entrypoint Compatibility)**: `main.py` 保持参数兼容；内部使用 adapters + IR merge。
- [ ] **T-003.4 (GUI Compatibility)**: `gui.py` 单任务/批量路径保持行为，复用共享 OCR 引擎。
- [ ] **T-003.5 (Regression Pack)**: 跑 unit/integration + demo case1/2/3 产物可打开。

## 4. Test Plan

### Testing for US-001
- **Unit Tests:**
  - [ ] `tests/unit/test_ir.py`：IR schema/字段约束校验（合法与失败用例）。
  - [ ] `tests/unit/test_mineru_adapter.py`：MinerU -> IR 映射正确性。
  - [ ] `tests/unit/test_ocr_adapter.py`：OCR -> IR 映射正确性（bbox/内容/style/provenance）。
- **Integration Tests:**
  - [ ] 新增最小链路：MinerUAdapter + OCRAdapter 输出可被统一 merge 并进入 generator。

### Testing for US-002
- **Unit Tests:**
  - [ ] `tests/unit/test_ir_merge.py`：多来源 IR 合并（重叠、非重叠、group_id、order 兜底）。
- **Integration Tests:**
  - [ ] 更新 `tests/integration/test_generator_ocr_merge.py`：断言 generator 只消费 merged IR，渲染双通道正确。
  - [ ] 更新 case2 列表场景断言：从“list结构保留”改为“IR 合并输出与文本结果正确”。

### Testing for US-003
- **Integration Tests:**
  - [ ] `tests/integration/test_cli_ocr_option.py`：CLI 参数兼容与转发。
  - [ ] GUI 最小回归：单任务 + 批量任务（mock OCR 引擎）。
- **Functional / E2E (项目内 smoke):**
  - [ ] `demo/case1`, `demo/case2`, `demo/case3` 转换成功并可打开 PPT。

## 5. Technical Considerations & Risks

- OCR 升格为解析源后，需明确职责边界：
  - OCRAdapter 负责“解析与IR映射”；
  - IRMerger 负责“跨源冲突解决”；
  - Renderer 仅负责“text/image渲染”。
- `group_id` 仅为弱提示，不能成为合并正确性的唯一依据。
- `order` 缺失统一按“先 y 后 x”，避免渲染顺序抖动。
- 迁移初期需兼容旧入口命名，降低 CLI/GUI 与测试改动面。
- 高风险点在 merge 重构：当前 `converter/ocr_merge.py:313-425` 逻辑耦合 MinerU 结构，迁移必须以测试驱动分步替换。
