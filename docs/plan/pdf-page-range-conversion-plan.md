# Technical Blueprint: PDF 页码范围转换

**Functional Spec:** `docs/interview/spec-pdf-page-range-conversion.md`

## 1. Technical Approach Overview

在 CLI、GUI、核心转换链路统一增加可选参数 `page_range`，并在 PDF 输入场景执行严格解析与校验。

- 输入语法支持：`N`、`N-M`、逗号组合（如 `1,3,5-8`）
- 页码规则：1-based 严格校验（非法格式、越界、反向区间均报错）
- 非 PDF 输入：忽略 `page_range`，保持现有流程

实现落点：
- `main.py`：新增 `--page-range` 参数并透传
- `gui.py`：单任务与批任务新增页码范围输入并透传
- `converter/generator.py`：新增解析器与 PDF 页过滤逻辑

## 2. File Impact Analysis

- **Created:**
  - （可选）`tests/unit/test_generator_page_range.py`（页码解析与边界校验）
- **Modified:**
  - `converter/generator.py`
  - `main.py`
  - `gui.py`
  - `tests/integration/test_cli_ocr_option.py`
  - `tests/integration/test_generator_ocr_merge.py`
- **Deleted:**
  - 无

## 3. Task Breakdown by User Story

### US-001: 仅转换 PDF 的指定页面
**Business Acceptance Criteria:**
- [ ] 输入 `1,3,5-8` 时，只输出对应页内容到 PPT。
- [ ] 未提供页码范围时，行为与当前版本一致。
- [ ] 输出页顺序与 PDF 原始页顺序一致。

**Technical Tasks:**
- [ ] **T-001.1 (Core)**: 在 `converter/generator.py` 实现页码范围解析函数。
- [ ] **T-001.2 (Core)**: 在 `convert_mineru_to_ppt` 中增加 `page_range` 参数并在 PDF 分支过滤页处理。
- [ ] **T-001.3 (CLI)**: `main.py` 新增 `--page-range` 参数并透传。
- [ ] **T-001.4 (GUI Single/Batch)**: `gui.py` 与 `AddTaskDialog` 增加页码范围输入并透传。

### US-002: 非法页码输入可被明确拦截
**Business Acceptance Criteria:**
- [ ] 非法格式报错并给出可理解提示。
- [ ] 越界页码报错并停止任务。
- [ ] 反向区间报错并停止任务。

**Technical Tasks:**
- [ ] **T-002.1 (Core Validation)**: 解析器对非法 token/区间/越界抛出 `ValueError`。
- [ ] **T-002.2 (Error Wiring)**: 复用现有 CLI/GUI 错误展示链路，不吞错。

### US-003: 非 PDF 输入兼容现有流程
**Business Acceptance Criteria:**
- [ ] 输入为非 PDF 时，页码范围参数被忽略。
- [ ] 任务正常完成，不报错。

**Technical Tasks:**
- [ ] **T-003.1 (Core)**: 非 PDF 分支直接忽略 `page_range`。
- [ ] **T-003.2 (Regression)**: 增加覆盖该行为的集成测试。

## 4. Test Plan

- **Unit Tests:**
  - [ ] 页码解析：合法输入（`1`、`1,3,5-8`、含空格）
  - [ ] 页码解析：非法输入（`1--3`、`a,b`、`8-5`、越界）
- **Integration Tests:**
  - [ ] CLI 透传 `--page-range` 到 `convert_mineru_to_ppt`
  - [ ] PDF 场景仅处理选中页（验证输出页数）
  - [ ] 非 PDF + `page_range` 不报错且可完成
- **Manual GUI Checks:**
  - [ ] 单任务：PDF 生效，图片忽略
  - [ ] 批任务：每任务页码范围独立生效

## 5. Technical Considerations & Risks

- `convert_mineru_to_ppt` 当前以 `i == 0` 设置首张 slide 尺寸，需要改为“首个实际处理页”以兼容选择非第一页场景。
- GUI 需同步中英文 i18n key，避免新增字段导致 KeyError。
- 批任务任务对象新增 `page_range` 字段时需兼容默认值，避免旧逻辑读取失败。
