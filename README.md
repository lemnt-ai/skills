# Skill 工具集

面向企业级 Java / Spring Boot / DDD 项目的 AI 驱动研发自动化 + 小说创作工具集，基于 Claude Code Skill 机制。

**研发链路：** 需求分析 → 设计文档 → 代码生成 → 代码审查  
**创作链路：** 灵感设定 → 大纲规划 → 逐章写作 → 自动校验

---

## 项目结构

```
ai/skills/
├── code-design/                    # 需求设计文档生成
│   ├── SKILL.md                    # skill 定义 + 工作流程
│   └── code_design_template.md     # 15 章标准化设计模板
├── code-generate/                  # 代码生成
│   └── SKILL.md                    # skill 定义 + 9 步生成流程
├── code-review/                    # 代码审查
│   └── SKILL.md                    # skill 定义 + 7 维审查维度
└── novel-studio/                   # 小说创作插件
    ├── .claude-plugin/
    │   └── plugin.json             # 插件身份证（名称/版本/18 个子 skill 注册表）
    ├── skills/                     # 核心：18 个子 skill
    │   ├── planning/               # 规划阶段（4 skill）
    │   │   ├── create_world/
    │   │   ├── create_character/
    │   │   ├── create_faction/
    │   │   └── generate_main_plot/
    │   ├── writing/                # 写作阶段（4 skill）
    │   │   ├── write_scene/
    │   │   ├── write_dialogue/
    │   │   ├── write_combat/
    │   │   └── write_emotional_scene/
    │   ├── analysis/               # 分析阶段（4 skill）
    │   │   ├── analyze_character_arc/
    │   │   ├── analyze_relationship/
    │   │   ├── detect_plot_holes/
    │   │   └── analyze_pacing/
    │   ├── validation/             # 校验阶段（3 skill）
    │   │   ├── validate_timeline/
    │   │   ├── validate_character_consistency/
    │   │   └── validate_power_scaling/
    │   └── memory/                 # 记忆阶段（3 skill）
    │       ├── summarize_chapter/
    │       ├── update_character_memory/
    │       └── update_timeline_memory/
    ├── agents/                     # 可选：子代理专用提示模板
    │   ├── world-architect.md
    │   ├── character-designer.md
    │   ├── scene-writer.md
    │   └── plot-hole-detector.md
    └── hooks/                      # 可选：生命周期钩子
        ├── hooks.json
        └── session-start
---

## Skill 介绍

### 1. code-design — 需求设计文档生成

从原始需求出发，输出标准化的 15 章设计文档和可执行的实现计划。

**触发方式：** 用户在 Claude Code 中输入 `生成设计文档`、`技术方案`、`系统设计` 等关键词。

**工作流程：**

```
原始需求 → 需求理解 → 源码分析 → 章节规划 → 逐章生成 → 自检 → 实现计划
```

**输出文档结构：**

| 分组 | 章节 |
|------|------|
| 核心设计 | ①工作流 ②需求背景 ③需求范围 ④需求分析 ⑤架构设计 |
| 接口数据 | ⑥API设计 ⑦数据库设计 ⑧枚举常量 |
| 集成设计 | ⑨缓存设计 ⑩MQ设计 ⑪安全设计 ⑫日志监控 |
| 质量保障 | ⑬测试方案 ⑭验收标准 ⑮输出要求 |

**内置决策树：**

| 需求类型 | 策略 |
|----------|------|
| 模糊需求 | → 追问 3 个关键问题 |
| 新功能（涉及 DB） | → 全 15 章 |
| 增量修改 | → 仅输出变更章节 |
| 重构/优化 | → 聚焦架构、安全、监控 |
| Bug 修复 | → 最小化，聚焦分析和验收 |

> **输出 → 直接作为 code-generate 的输入**

---

### 2. code-generate — 代码生成

根据设计文档自动生成可运行的企业级代码，风格严格对齐目标项目。

**触发方式：** 用户在 Claude Code 中输入 `生成代码`、`CRUD`、`按设计文档开发` 等关键词。

**工作流程：**

```
设计文档 → 项目结构分析 → 代码风格识别 → 逐层生成 → 自检 → 测试 → 配置 → 写入
```

**生成顺序：**

```
BO → VO → DO → Mapper → Converter → Service → ServiceImpl → Controller
```

**生成原则：**

- **设计文档优先** — API、字段、流程以文档为准，不擅自增减
- **项目风格优先** — 生成前先读目标项目已有文件，对齐命名/注解/结构
- **逐层自检** — 每完成一层，对照已有文件检查风格一致性

**测试覆盖：** 自动为 Service / Controller / Mapper 生成单元测试。

---

### 3. code-review — 代码审查

对企业级 Java 代码进行 7 维审查，输出可落地的问题清单和修复建议。

**触发方式：** 用户在 Claude Code 中输入 `审查代码`、`code review`、`帮我 review` 等关键词。

**审查维度：**

| 维度 | 检查重点 | 严重等级 |
|------|----------|:--------:|
| 设计一致性 | API/DB/流程与设计文档冲突 | MEDIUM |
| 代码正确性 | 边界条件、异常、事务、并发、幂等 | CRITICAL/HIGH |
| 安全性 | 权限、SQL注入、XSS、日志泄漏 | CRITICAL/HIGH |
| 代码质量 | 方法长度、重复代码、命名 | MEDIUM/LOW |
| 性能 | N+1、循环查库、索引缺失 | HIGH |
| 可维护性 | 注释、可测试性 | LOW |

**审查结论：**

| 结论 | 条件 |
| ---- | ---- |
| ✅ 通过 | 无 CRITICAL / HIGH |
| ⚠️ 有条件通过 | 存在 HIGH，修复后合并 |
| ❌ 拒绝 | 存在 CRITICAL 或 ≥3 项 HIGH |

---

### 4. novel-studio — 小说创作插件

`novel-studio/` 是一个符合插件规范的**小说创作辅助插件**，由 `.claude-plugin/plugin.json`（注册中心）+ 18 个子 skill（skills/）+ 子代理模板（agents/）+ 生命周期钩子（hooks/）组成。

#### 插件架构

```
novel-studio/
├── .claude-plugin/
│   └── plugin.json             # ◀── 插件身份证（名称/版本/18 子 skill 注册表/流水线定义）
├── skills/                     # 核心：18 个子 skill
│   ├── planning/               # 规划阶段（4 skill）
│   ├── writing/                # 写作阶段（4 skill）
│   ├── analysis/               # 分析阶段（4 skill）
│   ├── validation/             # 校验阶段（3 skill）
│   └── memory/                 # 记忆阶段（3 skill）
├── agents/                     # 子代理专用提示模板
│   ├── world-architect.md
│   ├── character-designer.md
│   ├── scene-writer.md
│   └── plot-hole-detector.md
└── hooks/                      # 生命周期钩子
    ├── hooks.json
    └── session-start
```

#### 核心机制

**`plugin.json`（插件注册中心）**：
- 声明插件的名称、版本、作者
- 注册全部 18 个子 skill 的路径、触发词、输入/输出规格
- 定义内置流水线（全流程创作、仅规划等）

**路由逻辑**（skill 触发时自动执行）：
- **意图分类** — 识别用户需求属于哪一类（规划/写作/分析/校验/记忆/全流程）
- **路由分发** — 匹配 `plugin.json` 中的 `triggers` 字段，路由到对应子 skill
- **流水线编排** — 全流程创作自动按 `planning → writing → memory → analysis/validation` 推进
- **上下文传递** — 上游子 skill 的输出自动作为下游的输入

**子 skill**：每个独立存在，保留独立触发能力，插件在路由层做编排。

#### 触发方式

| 场景 | 示例输入 |
|------|----------|
| 全流程创作 | "写一本玄幻小说"（自动执行全流水线） |
| 单 skill 调用 | "设计一个穿越到魔法世界的世界观"（自动路由到 create_world） |
| 指定阶段 | "帮我规划一下剧情，后续再写"（只执行 planning 阶段） |
| 分析检查 | "检查已写的前5章有没有剧情漏洞"（自动路由到 detect_plot_holes） |

> **每个子 skill 仍可独立触发**（如直接说"写一场战斗"触发 write_combat），但通过插件可获得编排和上下文传递能力。

#### 子 skill 注册表

注册在 `plugin.json` 中，共 18 个子 skill，按阶段分组：

**planning — 规划阶段**

| skill | 功能 | 触发词 |
|-------|------|--------|
| `create_world` | 世界观设定（时代/地理/力量体系/核心冲突） | 世界观, world building |
| `create_character` | 人物设定（性格/动机/语言风格/关系网） | 人物设定, character |
| `create_faction` | 势力设定（组织/阵营/势力关系） | 势力, faction |
| `generate_main_plot` | 主线剧情 + 分章大纲（章节规划/伏笔） | 剧情, 大纲, plot |

**writing — 写作阶段**

| skill | 功能 | 触发词 |
|-------|------|--------|
| `write_scene` | 场景构建（节奏/感官/转场） | 场景写作, scene |
| `write_dialogue` | 对话写作（语言风格/潜台词） | 对话, dialogue |
| `write_combat` | 战斗场景（力量体系/动作节奏） | 战斗, combat |
| `write_emotional_scene` | 情感场景（克制/留白/情绪曲线） | 情感戏, emotional |

**analysis — 分析阶段**

| skill | 功能 | 触发词 |
|-------|------|--------|
| `analyze_character_arc` | 角色弧光完整性分析 | 弧光, character arc |
| `analyze_relationship` | 人物关系合理性分析 | 关系分析, relationship |
| `detect_plot_holes` | 剧情漏洞/逻辑矛盾检测 | 漏洞, plot hole |
| `analyze_pacing` | 叙事节奏/高潮分布分析 | 节奏, pacing |

**validation — 校验阶段**

| skill | 功能 | 触发词 |
|-------|------|--------|
| `validate_timeline` | 时间线一致性校验 | 时间线, timeline |
| `validate_character_consistency` | 角色行为/性格一致性校验 | 角色一致性, 人设漂移 |
| `validate_power_scaling` | 战力/力量体系一致性校验 | 战力, power scaling |

**memory — 记忆阶段**

| skill | 功能 | 触发词 |
|-------|------|--------|
| `summarize_chapter` | 章节摘要记录 | 摘要, summarize |
| `update_character_memory` | 角色状态/位置/目标追踪 | 角色记忆, 角色状态 |
| `update_timeline_memory` | 故事时间线坐标记录 | 时间线更新 |

---

## 完整研发链路

```
┌──────────┐    ┌──────────────────┐    ┌──────────────┐    ┌──────────────┐
│  需求输入  │ → │  code-design     │ → │ code-generate │ → │ code-review   │
│           │    │  设计文档 + 实现计划 │    │  生成代码      │    │  审查代码      │
└──────────┘    └──────────────────┘    └──────────────┘    └──────────────┘
```

链路中的每个环节都是 **可选** 的：
- 直接生成代码（已有设计文档）
- 直接审查代码（无需重新设计）
- 先设计再生成再审查（全流程）

---

## 配套规范体系

本工具集参考以下企业级规范：

| 规范文件 | 内容 |
|----------|------|
| `CLAUDE.md` | 编码原则（思考先行、简洁优先、精准改动、目标驱动） |
| `code-style.md` | 代码规范（命名、DDD、注释、日志、AI Agent） |
| `api-conventions.md` | API 规范（RESTful、错误码、幂等、可观测性） |
| `testing.md` | 测试规范（分层、Mock、覆盖率、CI/CD） |

---

## 使用前提

- **Claude Code** 已安装并配置
- 目标项目为 **Java 17+ / Spring Boot 3**（或其他企业级 Java 项目）（研发方向）
- 项目目录中包含 `CLAUDE.md` 用于 code-generate 识别项目结构

---

## 快速开始

```bash
# 研发方向：在 Claude Code 中描述原始需求
# 1. 触发 code-design 生成设计文档
# 2. 确认设计文档后触发 code-generate 生成代码
# 3. （可选）触发 code-review 审查生成的代码

# 创作方向：直接说需求，插件自动路由
#   "写一本玄幻小说"              → 匹配 plugin.json → 全流水线编排
#   "设计一个穿越到魔法世界的世界观"  → 匹配 create_world 触发词 → 路由到该 skill
#   "写一场主角vs反派的战斗"      → 匹配 write_combat 触发词 → 路由到该 skill
#   "检查已写的前5章有没有剧情漏洞" → 匹配 detect_plot_holes 触发词 → 路由到该 skill
#   "总结第5章"                  → 匹配 summarize_chapter 触发词 → 路由到该 skill
```

---

## 许可证

MIT
