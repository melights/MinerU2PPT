# Technical Blueprint: Unified IR Cleanup Order and Dict-Free IR Pipeline

**Functional Spec:** `docs/interview/spec-unified-ir-cleanup-dict-free-pipeline.md`

## 1. Technical Approach Overview

### A. 统一 IR 类型边界（normalize 后禁用 dict）
现状是 `normalize_element_ir` 仍返回 dict（`converter/ir.py:307`, `converter/ir.py:357`, `converter/ir.py:395`），且 `PageIR.elements` / `ImageIR.text_elements` 也仍是 dict 容器（`converter/ir.py:47`, `converter/ir.py:40`）。
方案：

1. 将 `normalize_element_ir` 改为返回 `TextIR | ImageIR`。
2. `normalize_elements / validate_ir_elements / materialize_text_runs_for_elements / sort_elements / build_page_ir` 全链路改为强类型 IR，不再使用 dict `.get(...)` 访问。
3. `MinerUAdapter`、`OCRAdapter` 输出统一改为强类型 IR（当前调用点：`converter/adapters/mineru_adapter.py:107`, `converter/adapters/mineru_adapter.py:154`, `converter/adapters/ocr_adapter.py:173`）。
4. `ir_merge.py` 从 dict 算法迁移到类型化算法（当前大量 `elem.get`，如 `converter/ir_merge.py:27`, `converter/ir_merge.py:132`, `converter/ir_merge.py:324`）。

### B. cleanup 顺序重排并集中
现状 cleanup 分散且有重复：
- 全元素背景 cleanup 预处理（`converter/generator.py:421-425`）
- `_process_text` 再 cleanup（`converter/generator.py:284-293`）
- `_process_image` 再 cleanup（`converter/generator.py:387-389`）
- image crop 内又有 text cleanup（`converter/generator.py:367-380`）

方案改成单一阶段顺序：

1. **text → background**
2. **text → image**（在 ImageIR 裁剪像素副本上）
3. **image → background**

并将上述逻辑收敛到统一 cleanup orchestrator，避免散落在 `_process_text/_process_image/_add_picture_from_bbox` 多点重复。

### C. ImageIR 保存裁剪像素副本
在页面上下文可得 `page_image` 后，为每个 `ImageIR` 生成 `crop_pixels`（copy），用于 text→image cleanup。渲染阶段直接使用该副本，不再临时在 `_add_picture_from_bbox` 里即取即改。

### D. 双门禁（类型 + 测试）
- **类型门禁**：在代码层与测试层阻止 normalize 后 dict IR 回流。
- **测试门禁**：新增/改造单测与集成测试覆盖 cleanup 顺序、ImageIR 像素副本路径、dict IR 禁止规则。

## 2. File Impact Analysis

- **Created:**
  - `converter/cleanup_pipeline.py`（集中实现 cleanup 三阶段编排）
  - `tests/unit/test_cleanup_pipeline_order.py`（顺序与阶段行为）
  - `tests/unit/test_ir_no_dict_post_normalize.py`（类型门禁）
  - `tests/integration/test_generator_cleanup_pipeline.py`（真实流程回归）

- **Modified:**
  - `converter/ir.py`（核心：normalize/validate/materialize/sort/build 全类型化）
  - `converter/adapters/mineru_adapter.py`（输出强类型 IR）
  - `converter/adapters/ocr_adapter.py`（输出强类型 IR）
  - `converter/ir_merge.py`（合并逻辑由 dict 改为类型对象）
  - `converter/generator.py`（cleanup 调度重构，删除重复 cleanup 路径）
  - `tests/unit/test_ir.py`（断言从 dict key 迁移到属性访问）
  - `tests/unit/test_ir_merge.py`（fixture 与断言迁移）
  - `tests/integration/test_generator_ocr_merge.py`（按新 pipeline 调整断言）

- **Deleted:**
  - 无强制删除文件；但会删除旧的重复 cleanup 分支代码段（函数内逻辑删除）。

## 3. Task Breakdown by User Story

### US-001: 统一 clean up 顺序
**Business Acceptance Criteria:** text→background/image，再 image→background；逻辑集中。

**Technical Tasks:**
- [ ] **T-001.1 (Generator/Cleanup)**: 新建 cleanup orchestrator，定义三阶段执行序。
- [ ] **T-001.2 (Generator)**: 删除 `process_page` 的全量预清理分支（`converter/generator.py:421-425`）与重复路径，改为单入口调用。
- [ ] **T-001.3 (Render)**: `_add_picture_from_bbox` 不再做临时 text overlap cleanup（`converter/generator.py:367-380`），改读已清理的 ImageIR 像素副本。

### US-002: 去除 dict IR
**Business Acceptance Criteria:** normalize 后链路不再使用 dict 表示 IR（全仓库强制）。

**Technical Tasks:**
- [ ] **T-002.1 (IR Core)**: `normalize_element_ir` 返回 `TextIR | ImageIR`；`PageIR.elements` 改为强类型列表。
- [ ] **T-002.2 (Adapters)**: MinerU/OCR adapter 返回强类型 IR。
- [ ] **T-002.3 (IR Merge)**: 将 `merge_ir_elements` 及子函数全部改为类型对象访问（去 `.get`）。
- [ ] **T-002.4 (Generator)**: 页面处理从 dict 访问改为属性访问。
- [ ] **T-002.5 (Repo-wide)**: 清理 normalize 后的 dict IR 传递路径（含测试代码）。

### US-003: ImageIR 持有像素副本
**Business Acceptance Criteria:** ImageIR 包含裁剪像素；text→image 使用该副本。

**Technical Tasks:**
- [ ] **T-003.1 (IR Model)**: 为 `ImageIR` 增加 `crop_pixels` 字段（页面阶段填充）。
- [ ] **T-003.2 (Generator)**: 在页面准备阶段创建 image crop copy 并绑定到 ImageIR。
- [ ] **T-003.3 (Cleanup)**: text→image cleanup 改为操作 `ImageIR.crop_pixels`。
- [ ] **T-003.4 (Render)**: 渲染图片直接使用清理后的 `crop_pixels`。

### US-004: 强制门禁
**Business Acceptance Criteria:** 类型门禁 + 测试门禁均可阻断违规。

**Technical Tasks:**
- [ ] **T-004.1 (Type Gate)**: 增加“normalize 后不得为 dict IR”的仓库级校验测试（含关键模块扫描与运行时断言）。
- [ ] **T-004.2 (Test Gate)**: 新增 cleanup 顺序测试与 image 副本路径测试。
- [ ] **T-004.3 (Regression)**: 更新现有 IR/merge/generator 测试，确保行为与既有 OCR 合并路径兼容。

## 4. Test Plan

### Testing for US-001
- **Unit Tests:**
  - [ ] 验证 cleanup 执行顺序严格为 text→background、text→image、image→background。
  - [ ] 验证 text cleanup margin 同时作用于 background 与 image 副本。
- **Integration Tests:**
  - [ ] 构造 text 覆盖 image 场景，验证导出结果无残影/双重擦除回归。
- **E2E Tests:**
  - [ ] 用 demo 样例跑转换，核对关键页面视觉一致性。

### Testing for US-002
- **Unit Tests:**
  - [ ] `normalize_element_ir` 返回类型对象，不再是 dict。
  - [ ] `validate_ir_elements/materialize/sort` 全链路类型对象输入输出。
- **Integration Tests:**
  - [ ] adapter→merge→generator 主链路不出现 dict IR。
- **E2E Tests:**
  - [ ] CLI/GUI 路径完成一次端到端转换并通过。

### Testing for US-003
- **Unit Tests:**
  - [ ] ImageIR 在页面阶段持有 crop copy。
  - [ ] text→image cleanup 对 crop copy 生效且不污染原图。
- **Integration Tests:**
  - [ ] 渲染阶段使用已清理 crop copy，而非临时再清理。
- **E2E Tests:**
  - [ ] 复杂图文页视觉回归检查。

### Testing for US-004
- **Unit/Guard Tests:**
  - [ ] 仓库级 guard：normalize 后流程节点禁止 dict IR。
- **CI Gate:**
  - [ ] 将 guard 测试并入默认测试入口，失败即阻断。

## 5. Technical Considerations & Risks

- **内存风险**：`ImageIR.crop_pixels` 会提升峰值内存；需定义生命周期（渲染后释放引用）。
- **迁移风险**：`ir_merge.py` 与大量测试目前是 dict 假设，迁移面广，需分阶段提交确保每步可测。
- **冻结 dataclass 与像素可变性**：若保持 `frozen=True`，需采用“copy-on-write + 生成新 IR”策略，避免隐式可变副作用。
- **门禁可靠性**：仅靠 grep 不稳，建议 guard 测试 + 运行时类型断言组合。
- **兼容边界**：允许外部输入是 dict（spec FR-10），但进入 normalize 后必须完成类型化，不得回流。
