# Product Requirements Document: OCR BBox XY联合精修（在Y流程中补充X）

## 0. Document Control
- Version: v0.1
- Status: Approved
- Source: requirements interview conversation
- Last Updated: 2026-03-14

## 1. Decision Summary

### 1.1 Confirmed Decisions
- D1: 在现有 OCR bbox 的 Y 方向精修流程中，补充 X 方向精修逻辑，形成同一流程内的 XY 联合处理。
- D2: 处理对象为 OCR 结果全链路：element bbox、line bbox、span bbox 全部同步更新。
- D3: 采用对称策略：复用现有“像素命中”思路，新增列方向 flags，执行 left/right 的 trim + extend 两阶段逻辑。
- D4: 验收接受新增单测覆盖 X 收缩与 X 恢复，并保持现有 Y 能力不退化。

### 1.2 Out of Scope / Non-Goals
- 不改 OCR 检测模型与推理参数。
- 不引入新的外部依赖。
- 不重构 OCR-MinerU 合并策略，仅修改 bbox refine 阶段。

## 2. Scope & Boundaries

### 2.1 In Scope
- 修改 OCR refine 核心逻辑，使其在现有 Y 处理路径中加入 X 处理。
- 同步更新 element/line/span 的 bbox。
- 保持并复用当前调试字段输出能力（original/pad/refined）。
- 增加对应单元测试。

### 2.2 Constraints & Dependencies
- 需兼容当前调用链 `refine_ocr_text_elements`（`converter/ocr_merge.py`）。
- 需保持现有 `_expand_bbox_with_pad`、颜色提取链路与 bbox 坐标转换行为一致。
- 现有调试字段使用点不得破坏。

## 3. Final-State Process Flow

### 3.1 End-to-End Happy Path
1. OCR 结果进入 `refine_ocr_text_elements`。
2. 对 element bbox 执行“Y流程内补充X”的联合 refine：在同一次 refine 过程中计算 row/col flags，完成 top/bottom/left/right 的 trim+extend。
3. 对每个 line bbox 执行同样联合 refine。
4. 用 refine 后的 line bbox 同步回写 spans 的 x/y 边界。
5. 由 line bbox union 得到 element 最终 bbox。
6. 输出 refined elements，并保留调试字段。

### 3.2 Key Exception Flows
- EX-1: ROI 无有效像素命中 -> 保持原 bbox，不做破坏性调整。
- EX-2: refine 后框无效（x2<=x1 或 y2<=y1）-> 回退原 bbox。
- EX-3: 输入缺失 bbox/lines/spans -> 按现有容错路径保持行为稳定。

## 4. Functional Requirements

### FR-001 在Y精修流程中补充X精修
- Description: 在当前 Y refine 逻辑内加入 X refine，形成单流程联合处理。
- Trigger/Input: OCR element/line 的 bbox 与 page_image。
- Processing rules:
  - 复用现有像素匹配思路；
  - 新增列方向 flags；
  - 执行 left/right trim + extend，规则与 top/bottom 对称；
  - 与 pad 区域结合进行边界恢复与对齐。
- Output/Result: 产出同时完成 X/Y 调整的 bbox。
- Error/Failure behavior: 无法判定时返回原 bbox。
- Priority: Must

### FR-002 全链路 bbox 同步更新
- Description: 将 XY refine 结果同步到 element、line、span。
- Trigger/Input: refine 后 line bbox。
- Processing rules:
  - line.bbox 使用 refine 结果；
  - span.bbox 的 x1/x2/y1/y2 与 line 对齐（覆盖原仅Y同步行为）；
  - element.bbox 由 refined lines union 生成。
- Output/Result: 三层 bbox 坐标一致。
- Error/Failure behavior: 缺失 spans 时保持最小合法结构。
- Priority: Must

### FR-003 调试字段兼容
- Description: 保持调试字段存在并语义稳定。
- Trigger/Input: refine 输出阶段。
- Processing rules: 继续输出 `ocr_bbox_original`、`ocr_bbox_pad`、`ocr_bbox_refined`。
- Output/Result: 调试链路可继续使用。
- Error/Failure behavior: 若无可 refine bbox，字段遵循现有降级策略。
- Priority: Must

### FR-004 测试覆盖X方向行为
- Description: 为 X 方向 refine 增加测试并保证 Y 不回归。
- Trigger/Input: 单元测试执行。
- Processing rules:
  - 新增“左右去空白”用例；
  - 新增“左右恢复扩展”用例；
  - 保留现有 Y refine 与 debug 字段断言。
- Output/Result: 测试可验证 XY 联合 refine。
- Error/Failure behavior: 任一断言失败视为需求未达标。
- Priority: Must

## 5. Acceptance Criteria (Release Gate)
- AG-001 (FR-001): 在过宽 OCR 框样本中，refined 后至少一侧 x 边界向内收缩，且 bbox 合法。
- AG-002 (FR-001): 在过窄 OCR 框样本中，refined 后至少一侧 x 边界可向外恢复。
- AG-003 (FR-002): 输出中 element/line/span 的 bbox 在 x/y 坐标层面保持同步一致。
- AG-004 (FR-003): `ocr_bbox_original`、`ocr_bbox_pad`、`ocr_bbox_refined` 仍存在。
- AG-005 (FR-004): 现有 `test_ocr_bbox_refine` 的 Y 相关测试保持通过，新增 X 测试通过。

## 6. Verification Plan
- Unit tests required:
  - 扩展 `tests/unit/test_ocr_bbox_refine.py`，新增 X trim 与 X extend 用例。
- Integration tests required:
  - 非必须新增；现有 OCR 集成测试需全绿以防回归。
- Functional/smoke tests required:
  - 运行现有 OCR merge/refine 相关测试集，确认 bbox 输出稳定。
- Evidence needed for sign-off:
  - 相关单测通过记录；
  - 关键用例 refined 前后 bbox 对比结果。

## 7. Open Questions
- Q1: 列方向命中阈值是否完全复用行方向参数，还是单独引入列阈值常量（默认建议先复用，避免参数膨胀）。
- Q2: X/Y 执行顺序采用“同阶段联合计算”还是“固定顺序串行（先Y后X或先X后Y）”；建议在实现中固定一种并保持测试锁定。
