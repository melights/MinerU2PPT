# Technical Blueprint: OCR调试框分阶段输出与PageContext统一IR存储

**Functional Spec:** 会话推导需求（用户明确约束）

## 1. Technical Approach Overview

本方案采用“**PageContext作为页面级中间态中心（IR + Debug）**”的实现方式，满足以下约束：

- `PageContext` 不仅保存渲染用元素，还保存**各阶段产出的 `PageIR`**。
- 使用字典结构按阶段名存储：`stage_page_irs: dict[str, PageIR]`，便于统一调试与后续扩展。
- 中间处理阶段不直接写文件，只把阶段结果注册到 `PageContext`。
- 统一在 `PageContext.generate_debug_images(...)` 中输出调试图。
- 除框对比图外，额外输出每页原始 PNG（无框）以支持 case 产出。

阶段定义（首期）：

1. `mineru_original`：MinerU Adapter 输出的原始 IR
2. `ocr_before_refined_elements`：OCR refine 前对应 IR
3. `ocr_after_refined_elements`：OCR refine 后对应 IR
4. `merged_final`：IR merge 之后用于渲染的最终 IR

现有代码锚点：

- `PageContext`：`converter/generator.py:20`
- 页面主流程：`convert_mineru_to_ppt` in `converter/generator.py:406`
- OCR refine 前后：`converter/ocr_merge.py:304-305`
- `PageIR` 构建：`build_page_ir` in `converter/ir.py:445`

## 2. File Impact Analysis

- **Created:**
  - 无

- **Modified:**
  - `converter/generator.py`
    - 扩展 `PageContext`：新增 `stage_page_irs`、阶段注册方法、统一debug输出
    - `convert_mineru_to_ppt`：创建并贯穿传递 `PageContext`，在关键阶段注册 `PageIR`
    - `process_page`：兼容接收外部创建的 `PageContext` 或至少消费 `merged_final` 阶段IR
  - `converter/adapters/ocr_adapter.py`
    - `extract_page_elements` 支持接收 `page_context`（可选）
    - 将 OCR pre/post refine 结果映射为 IR，并注册到 `PageContext`
  - `converter/ocr_merge.py`
    - `extract_text_elements` 支持输出 refine 前后结构给上层（避免仅依赖隐式状态）
  - `converter/adapters/mineru_adapter.py`
    - 保持 adapter 纯映射；在 generator 层将其输出构建为 `PageIR` 并注册

- **Deleted:**
  - 无

## 3. Task Breakdown by User Story

### US-DBG-001: 作为开发者，我希望每页保存分阶段IR并统一输出对比图，便于定位OCR与Merge差异
**Business Acceptance Criteria:**
- `PageContext` 可按阶段保存 `PageIR`。
- 每页输出 OCR refine 前框、OCR refine 后框、MinerU 原始框对比图。
- 每页额外输出原始 PNG（无框）。
- 中间阶段不分散写图，统一由 `PageContext` 输出。

**Technical Tasks:**
- [ ] **T-DBG-001.1 (PageContext Core)**: 在 `PageContext` 中新增 `stage_page_irs: dict[str, PageIR]` 与 `register_stage_page_ir(stage, page_ir)`。
- [ ] **T-DBG-001.2 (MinerU Stage Capture)**: 在 `convert_mineru_to_ppt` 中将 MinerU adapter 输出构建为 `PageIR` 并注册为 `mineru_original`。
- [ ] **T-DBG-001.3 (OCR Stage Capture)**: 打通 OCR refine 前后结果到 adapter/generator，分别构建 `PageIR` 并注册为 `ocr_before_refined_elements` 与 `ocr_after_refined_elements`。
- [ ] **T-DBG-001.4 (Merged Stage Capture)**: `merge_ir_elements` 产出后构建 `PageIR` 并注册为 `merged_final`。
- [ ] **T-DBG-001.5 (Unified Debug Output)**: 在 `PageContext.generate_debug_images` 内统一输出各阶段框图 + 原始PNG。
- [ ] **T-DBG-001.6 (Naming Convention)**: 统一文件命名，便于自动脚本收集与对比。

## 4. Test Plan

### Testing for US-DBG-001
- **Unit Tests:**
  - [ ] `PageContext` 阶段注册行为测试：
    - 阶段可新增/覆盖
    - 非法阶段输入处理
    - `stage_page_irs` 存储为 `PageIR`
  - [ ] OCR阶段采集测试：确保 pre/post refine 都能被转换为有效IR元素并可构建 `PageIR`。

- **Integration Tests:**
  - [ ] `debug_images=True` 时，每页输出：
    - `tmp/page_<index>_original.png`
    - `tmp/page_<index>_mineru_original_boxes.png`
    - `tmp/page_<index>_ocr_before_refined_elements.png`
    - `tmp/page_<index>_ocr_after_refined_elements.png`
    - `tmp/page_<index>_merged_final_boxes.png`
  - [ ] 多页输入时页码与输出文件一一对应。
  - [ ] 关闭 debug 时不生成上述调试文件。

- **E2E / Smoke:**
  - [ ] 以 `demo/case1`、`demo/case3` 进行人工对比，确认三类框图差异与预期一致。

## 5. Technical Considerations & Risks

- `PageContext` 与 Adapter 之间需避免循环依赖：
  - Adapter 接收 `page_context` 的 duck-typed 接口，不直接 import `PageContext` 类型。
- “OCR 未 refined_elements”语义首期定义为 refine 输入集合（当前流程中的 `merged_line_elements`，见 `converter/ocr_merge.py:304`），保持与现有pipeline一致。
- 阶段 `PageIR` 建议统一通过 `build_page_ir` 构建（`converter/ir.py:445`），确保元素规范化与排序一致。
- 原始图输出应基于页面 `original_image`（无框、无inpaint），避免与渲染背景混淆。
- 该功能为 debug 能力增强，不应改变 `merged_final` 渲染结果与PPT输出语义。
