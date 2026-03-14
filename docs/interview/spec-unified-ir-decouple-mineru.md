# Feature Brief: 统一IR解耦MinerU（Text/Image双类型）

## 1. Overview
当前转换链路以 MinerU 原始格式为主，导致解析源耦合高、后续接入其他分块来源成本高。该功能通过引入统一中间结构（IR），将上游解析（如 MinerU）与下游处理（merge/refine/render）解耦。第一期仅保留 `text` 与 `image` 两类元素，并保留必要样式字段与分组字段（`group_id`），实现“多源可接入、下游单逻辑消费”。

## 2. Goals
- 建立统一 IR 数据模型与输入校验机制，作为下游唯一输入。
- 完成 MinerU -> IR 适配器，屏蔽 MinerU 原始字段对下游的直接影响。
- 完成全链路迁移：generator / merge / render 仅消费 IR。
- 保持现有 CLI/GUI 用户行为不变（不做 GUI 大改）。
- 在不引入训练与性能专项优化的前提下，保证回归通过。

## 3. User Stories

- **US-001: 多源解析统一接入**
  - **As a** 开发者, **I want to** 将不同解析源转换为统一 IR, **so that I can** 不改渲染主链路即可替换上游解析器。
  - **Acceptance Criteria:**
    - [ ] 系统存在明确的 IR 结构定义与字段约束。
    - [ ] 下游模块不再读取 MinerU 原始结构字段。
    - [ ] MinerU 输出可稳定映射为 IR 并驱动完整转换流程。

- **US-002: 下游逻辑简化为双通道渲染**
  - **As a** 维护者, **I want to** 只保留 text/image 两种渲染逻辑, **so that I can** 降低复杂度并减少嵌套结构处理负担。
  - **Acceptance Criteria:**
    - [ ] 渲染入口仅按 `type in {text, image}` 分流。
    - [ ] `table/title/list` 不作为独立渲染类型；按映射策略归并到 text/image。
    - [ ] `style` 字段可用于文本样式控制（如加粗）。

- **US-003: 迁移期稳定可回归**
  - **As a** 使用者, **I want to** 在迁移后继续使用现有命令与GUI流程, **so that I can** 无感升级。
  - **Acceptance Criteria:**
    - [ ] 现有 CLI 参数与主流程保持兼容。
    - [ ] GUI 无结构性改版，仅最小接线调整。
    - [ ] 既有单元/集成测试通过，且新增 IR 相关测试通过。

## 4. Functional Requirements

- **FR-1** 系统必须定义统一 IR，元素类型仅允许 `text` 与 `image`。
- **FR-2** IR 元素必须包含最小公共字段：`id`, `page_index`, `type`, `bbox`, `order`（可空）, `group_id`（可空）, `tags`（可空）, `provenance`。
- **FR-3** `text` 元素必须支持 `text` 内容与 `style`（可空）；`image` 元素必须支持图像引用字段（路径或内存句柄）。
- **FR-4** 必须提供 IR 校验机制，在边界处进行字段合法性校验并失败快返（非法类型、非法 bbox、页索引错误等）。
- **FR-5** 必须实现 MinerU 适配器，将 MinerU 输出转换为 IR，不允许在适配器之外直接依赖 MinerU 原始字段。
- **FR-6** 现有 generator/merge/render 必须迁移为仅消费 IR。
- **FR-7** `group_id` 作为可选弱提示字段，可用于文本块合并（尤其列表场景），但系统不能强依赖其存在。
- **FR-8** 阅读顺序必须可由 `order` 驱动；当 `order` 缺失时，必须有统一兜底排序策略（如按几何位置）。
- **FR-9** 系统必须支持通过新增适配器接入其他解析源，而无需改动渲染主链路。
- **FR-10** 第一期开关与行为必须与现有 CLI/GUI 兼容，不引入用户可见破坏性变更。

## 5. Non-Goals (Out of Scope)
- 不做模型训练或数据标注流程建设。
- 不做 GUI 大改（仅必要接线与参数透传调整）。
- 不做 table 可编辑化（表格先按 image 渲染）。
- 不做性能专项优化（并发、缓存、启动耗时优化不在本期）。

## 6. Success Metrics
- 代码中除适配器层外，`0` 处直接读取 MinerU 原始结构字段。
- 既有单元/集成测试通过率 `100%`（以当前仓库测试集为准）。
- 新增 IR 相关测试至少覆盖：
  - [ ] IR 校验（合法/非法输入）
  - [ ] MinerU -> IR 映射正确性
  - [ ] 渲染双通道分流正确性
- demo 样例（case1/case2/case3）均可完成转换并生成可打开的 PPT 文件。

## 7. Open Questions
1. `order` 的最终兜底排序规则是否固定为“先 y 后 x”，还是需要可配置策略？
2. `group_id` 的生成与继承规则是否只由适配器提供，还是允许 merge 阶段补写？
3. `style` 最小字段集合是否仅包含 `bold/font_size/align`，还是需要预留更多属性（如颜色/行高）？
4. 第二解析源（如 PP-Structure）是否在第一期作为“可选验证项”接入，还是严格推迟到下一期？
