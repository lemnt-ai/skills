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
└── novel-skills/                   # 小说创作 skill 体系（规划/写作/分析/校验/记忆）
    ├── planning/                   # 规划阶段
    │   ├── create_world/           #   世界观设定
    │   ├── create_character/       #   人物设定
    │   ├── create_faction/         #   势力设定
    │   └── generate_main_plot/     #   主线剧情
    ├── writing/                    # 写作阶段
    │   ├── write_scene/            #   场景写作
    │   ├── write_dialogue/         #   对话写作
    │   ├── write_combat/           #   战斗场景
    │   └── write_emotional_scene/  #   情感场景
    ├── analysis/                   # 分析阶段
    │   ├── analyze_character_arc/  #   角色弧光分析
    │   ├── analyze_relationship/   #   人物关系分析
    │   ├── detect_plot_holes/      #   剧情漏洞检测
    │   └── analyze_pacing/         #   叙事节奏分析
    ├── validation/                 # 验证阶段
    │   ├── validate_timeline/      #   时间线校验
    │   ├── validate_character_consistency/ # 角色一致性校验
    │   └── validate_power_scaling/ #   战力平衡校验
    └── memory/                     # 记忆阶段
        ├── summarize_chapter/      #   章节摘要
        ├── update_character_memory/#   角色记忆更新
        └── update_timeline_memory/ #   时间线记忆更新
```

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

### 4. novel-skills — 小说创作 skill 体系

`novel-skills/` 是深度专业化的小说创作 skill 集合，按创作流程分为 5 个组、19 个子 skill。每个子 skill 可独立触发，也可按 `planning → writing → memory → analysis/validation` 串联使用。

#### planning — 规划阶段

| skill | 功能 | 独立触发词 |
|-------|------|-----------|
| `create_world` | 世界观设定（时代/地理/力量体系/核心冲突） | "世界观"、"world building" |
| `create_character` | 人物设定（性格/动机/语言风格/关系网） | "人物设定"、"character" |
| `create_faction` | 势力设定（组织/阵营/势力关系） | "势力设定"、"faction" |
| `generate_main_plot` | 主线剧情 + 分章大纲（章节规划/伏笔） | "剧情"、"大纲"、"plot" |

#### writing — 写作阶段

| skill | 功能 | 独立触发词 |
|-------|------|-----------|
| `write_scene` | 场景构建（节奏/感官/转场） | "场景写作"、"scene" |
| `write_dialogue` | 对话写作（语言风格/潜台词） | "对话"、"dialogue" |
| `write_combat` | 战斗场景（力量体系/动作节奏） | "战斗"、"combat" |
| `write_emotional_scene` | 情感场景（克制/留白/情绪曲线） | "情感戏"、"emotional" |

#### analysis — 分析阶段

| skill | 功能 | 独立触发词 |
|-------|------|-----------|
| `analyze_character_arc` | 角色弧光完整性分析 | "弧光"、"character arc" |
| `analyze_relationship` | 人物关系合理性分析 | "关系分析"、"relationship" |
| `detect_plot_holes` | 剧情漏洞/逻辑矛盾检测 | "漏洞"、"plot hole" |
| `analyze_pacing` | 叙事节奏/高潮分布分析 | "节奏"、"pacing" |

#### validation — 验证阶段

| skill | 功能 | 独立触发词 |
|-------|------|-----------|
| `validate_timeline` | 时间线一致性校验 | "时间线"、"timeline" |
| `validate_character_consistency` | 角色行为/性格一致性校验 | "角色一致性" |
| `validate_power_scaling` | 战力/力量体系一致性校验 | "战力"、"power scaling" |

#### memory — 记忆阶段

| skill | 功能 | 独立触发词 |
|-------|------|-----------|
| `summarize_chapter` | 章节摘要记录 | "摘要"、"summarize" |
| `update_character_memory` | 角色状态/位置/目标追踪 | "角色记忆"、"角色状态" |
| `update_timeline_memory` | 故事时间线坐标记录 | "时间线更新" |

> **使用方式：** 每个子 skill 可独立触发调用，也可按创作流程串联使用。

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

# 创作方向：按 need 触发对应子 skill
#   "构建一个魔法世界观"          → 触发 create_world
#   "设计一个亦正亦邪的反派"      → 触发 create_character
#   "写一场主角vs反派的战斗"      → 触发 write_combat
#   "检查已写的3章有没有漏洞"     → 触发 detect_plot_holes
#   "总结第5章"                  → 触发 summarize_chapter
#   "写一本玄幻小说，从设定开始"   → 按顺序触发 planning → writing → validation
```

---

## 许可证

MIT
