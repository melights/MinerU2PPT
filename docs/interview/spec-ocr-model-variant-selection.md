# Product Requirements Document: OCR Model Variant Selection

## 0. Document Control
- Version: v0.1
- Status: Draft
- Source: requirements interview conversation
- Last Updated: 2026-03-15

## 1. Decision Summary

### 1.1 Confirmed Decisions
- D1: GPU 可用时默认使用 server 模型；GPU 不可用时默认使用 lite 模型。
- D2: 轻量模型使用 PP-OCRv5_lite_det/rec。
- D3: 提供 CLI/GUI 参数 `--ocr-model-variant [auto|lite|server]` 覆盖默认策略。
- D4: 当设置 `--ocr-model-root` / `MINERU_OCR_MODEL_ROOT` 时，仍依据 lite/server 选择其子目录版本。
- D5: 模型缺失或下载失败直接报错，不做自动回退。

### 1.2 Out of Scope / Non-Goals
- 不引入新的 OCR 引擎或替代 PaddleOCR。
- 不改变 OCR 结果合并与渲染逻辑。
- 不新增在线模型下载策略。

## 2. Scope & Boundaries

### 2.1 In Scope
- 新增 OCR 模型变体选择策略（auto/lite/server）。
- CLI 与 GUI 的模型变体配置与传递。
- 运行时日志明确输出所选模型变体与来源。

### 2.2 Constraints & Dependencies
- 依赖 PaddleOCR/PaddleX 的模型命名与加载机制。
- 现有 `ocr_device_policy` 仍保留，模型变体选择独立于设备选择。
- 本地模型根目录布局需包含 lite/server 对应子目录（由实现定义）。

## 3. Final-State Process Flow

### 3.1 End-to-End Happy Path
1. 用户在 CLI/GUI 中未指定 `ocr-model-variant`。
2. 系统检测 GPU 可用性。
3. GPU 可用 -> 选用 server 模型；否则选用 lite 模型。
4. 初始化 OCR 引擎并记录日志（包含变体与来源）。
5. 正常完成 OCR 与转换流程。

### 3.2 Key Exception Flows
- EX-1: 选择的模型文件缺失 -> 抛出错误并终止。
- EX-2: PaddleOCR 初始化失败 -> 抛出错误并终止。

## 4. Functional Requirements

### FR-001 OCR 模型变体选择
- Description: 支持 auto/lite/server 三种变体策略。
- Trigger/Input: CLI/GUI 参数 `--ocr-model-variant` 或默认 auto。
- Processing rules:
  - auto: GPU 可用 -> server；GPU 不可用 -> lite。
  - lite/server: 强制对应模型。
- Output/Result: 选定模型变体用于 OCR 初始化。
- Error/Failure behavior: 变体非法时抛错并终止。
- Priority: Must

### FR-002 本地模型根目录适配
- Description: 当使用本地模型根目录时，仍按 lite/server 选择对应子目录。
- Trigger/Input: `--ocr-model-root` 或 `MINERU_OCR_MODEL_ROOT`。
- Processing rules: 从 root 下解析 lite/server 对应子目录并加载。
- Output/Result: 使用本地模型完成初始化。
- Error/Failure behavior: 子目录或模型文件缺失时报错。
- Priority: Must

### FR-003 CLI 参数支持
- Description: CLI 增加 `--ocr-model-variant` 参数。
- Trigger/Input: 用户执行 CLI 命令。
- Processing rules: 参数透传到 OCR 初始化逻辑。
- Output/Result: CLI 可覆盖默认策略。
- Error/Failure behavior: 参数非法时报错。
- Priority: Must

### FR-004 GUI 参数支持
- Description: GUI 提供与 CLI 等价的模型变体选择。
- Trigger/Input: 用户在 GUI 中选择变体。
- Processing rules: GUI 选项透传到 OCR 初始化逻辑。
- Output/Result: GUI 可覆盖默认策略。
- Error/Failure behavior: 初始化失败在 GUI 日志中提示并终止。
- Priority: Must

### FR-005 日志输出
- Description: 运行时日志输出模型变体与来源（auto/explicit）。
- Trigger/Input: OCR 初始化时。
- Processing rules: 记录变体、是否因 GPU 不可用而切换。
- Output/Result: 用户可在日志中确认模型选择。
- Error/Failure behavior: 无。
- Priority: Should

## 5. Acceptance Criteria (Release Gate)
- AG-001: GPU 不可用且未指定变体时，日志显示使用 lite 模型且转换成功（FR-001, FR-005）。
- AG-002: GPU 可用且未指定变体时，日志显示使用 server 模型（FR-001, FR-005）。
- AG-003: CLI 指定 `--ocr-model-variant lite` 时，强制使用 lite（FR-003）。
- AG-004: GUI 选择 server 时，强制使用 server（FR-004）。
- AG-005: 指定本地模型根目录时，按 lite/server 子目录加载；缺失时报错（FR-002）。

## 6. Verification Plan
- Unit tests required:
  - 变体选择逻辑（auto/lite/server）
  - 本地模型 root 路径解析与缺失报错
- Integration tests required:
  - CLI 参数透传并生效
  - GPU 不可用时默认切换 lite
- Functional/smoke tests required:
  - GUI 变体切换路径可用
- Evidence needed for sign-off:
  - 测试通过日志 + 关键日志截图/输出

## 7. Open Questions
- 无
