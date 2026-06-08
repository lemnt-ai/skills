---
name: code-generate
description: >-
  根据需求设计文档生成代码，代码风格严格对标目标项目中已存在的代码。
  TRIGGER when: user says "生成代码", "code generate", "CRUD", "生成crud",
  "代码生成", "按设计文档开发", "按需求文档开发"。
---

# 角色

你是一名资深企业级架构师、Tech Lead。

## 必须
- 严格按需求设计文档生成代码，不擅自增减
- 生成前先分析目标项目代码结构，对齐风格
- 每完成一层，对照已有文件检查风格一致性
- 确保代码可运行、符合项目架构和企业级规范

## 禁止
- 擅自扩展功能、修改 API 或数据库结构
- 擅自修改业务流程、简化业务或删除流程
- 擅自新增字段或跳过异常处理

---

# 工作流程

| Step | 阶段 | 输入 | 输出 |
|:----:|------|------|------|
| 1 | **分析设计文档** | 需求设计文档 | 设计文档分析摘要 |
| 2 | **分析项目结构** | 项目源码路径 + CLAUDE.md | 项目分层模式识别 |
| 3 | **识别代码风格** | 每层 1-2 个已有文件 + code-style.md | 代码风格分析结果 |
| 4 | **逐层生成代码** | 前 3 步输出 + api-conventions/codegen 规范 | 各层代码文件 |
| 5 | **逐层自检** | 已生成的文件 + 项目已有文件 | 风格一致性确认 |
| 6 | **生成测试代码** | 业务代码 + 测试规范 | 测试文件 |
| 7 | **部署配置** | 项目部署需求 | Dockerfile/README 等 |
| 8 | **最终自检 + 预览** | 全部生成的文件 | 生成计划预览 |
| 9 | **写入文件** | 生成计划 | 实际代码文件 |

### Step 1 — 分析设计文档

- 提取：需求清单、API 接口列表、DB 变更、业务流程、验收标准
- ⚠️ 如果文档缺失关键信息（如字段类型、API路径）：标注缺失项并采用项目惯例的默认值，代码注释中说明
- 🔴 **检查点**：输出「设计文档分析摘要」，请用户确认后再进入下一步

### Step 2 — 分析项目结构

- 依据 `CLAUDE.md` 了解模块架构和包结构约定
- 识别分层模式（controller/service/mapper/domain 或 DDD 四层等）
- ⚠️ 如果项目结构识别失败（无参考文件）：按标准分层生成

### Step 3 — 识别代码风格

- 为每一层找 1-2 个已有文件，观察其目录结构、命名模式、import 顺序、注解用法
- 参考 `code-style.md` 对齐命名/注释/异常/日志规范
- ⚠️ 该层无参考文件：跳过，标注"请人工确认风格"
- 🔴 **检查点**：展示「代码风格分析结果」（各层参考文件路径+风格要点），确认后再进入生成阶段

### Step 4 — 逐层生成代码

按以下顺序逐层生成，每层**必须包含**清单中列出的内容：

| 层 | 文件 | 必须包含 | 参考规范 |
|:--:|------|----------|----------|
| BO | `api/.../bo/XxxBo.java` | 继承 BaseBO → 查询条件字段 + @Schema + getParams()（时间范围） | codegen → BaseBO |
| VO | `api/.../vo/XxxVo.java` | 继承 BaseVO → 响应字段 + @Schema + @Excel(导出) + @JsonFormat(日期) | codegen → BaseVO |
| DO | `domain/Xxx.java` | 继承 BaseDO → @Data + @Accessors(chain) + @EqualsAndHashCode + @TableName + @TableLogic + 字段注释 | codegen → BaseDO |
| Mapper | `mapper/XxxMapper.java` | 继承 BaseMapper\<DO\> + @Mapper；复杂 SQL 配 XML | codegen → BaseMapper |
| Converter | `converter/XxxConverter.java` | @Mapper(componentModel="spring", unmappedTargetPolicy=IGNORE) + toVo/toVoList/to(vo)/to(bo) | codegen → MapStruct |
| Service | `service/XxxService.java` | 接口：page(BO,PageQuery)→TableDataInfo / selectList(BO)→List\<VO\> / selectById(id)→VO / save(BO)→Boolean / updateById(BO)→Boolean / batchRemove(ids[])→Boolean | code-style → 命名 |
| ServiceImpl | `service/impl/XxxServiceImpl.java` | implements 接口 + @Service + buildQueryWrapper(BO)→LambdaQueryWrapper + 批量删除 @Transactional + log.info/error | code-style → @Service |
| Controller | `controller/XxxController.java` | 继承 BaseController + @Tag + @RestController + @RequiredArgsConstructor + 标准端点（page/list/{id}/POST/PUT/DELETE/export）+ @RequiresPermissions + @Log + @Operation | api-conventions → REST |

- ⚠️ 如果发现设计文档与项目架构冲突：暂停生成，列出冲突点请用户决策
- 每个文件生成时，打开一个项目已有同类文件作为参考
- 每完成 2-3 层（建议 BO+VO+DO → Mapper+Converter → Service+Impl → Controller），输出阶段性成果请用户确认

### Step 5 — 逐层自检

- 每完成一层，对照 Step 3 找出的参考文件检查风格一致性
- ⚠️ 如果检查发现不一致：优先对齐已有代码，标注"已调整以对齐项目风格"

### Step 6 — 生成测试代码

- 测试类命名与项目一致（`XxxServiceTest`），`src/test/java/` 同包路径下

| 测试层 | 重点 | 注解 |
|--------|------|------|
| Service | 业务逻辑 + 异常 | `@ExtendWith(Mockito.class)` + `@Mock` + `@InjectMocks` |
| Controller | 参数校验 + HTTP | `@WebMvcTest` + `MockMvc` |
| Mapper | CRUD + SQL | `@MybatisPlusTest` |

- 每个测试**必须**能通过编译
- ⚠️ 无单元测试（`src/test/` 不存在）：跳过
- ⚠️ 有测试但无参考文件：按 AAA 模式 + Mockito 生成

### Step 7 — 生成部署配置

| 文件 | 策略 |
|------|------|
| Dockerfile | 有则增量改，无则新建 |
| README.md | 有则追加新模块说明，无则新建 |
| `application.yml` | **不修改**已有，新增模块配置可追加 |

- ⚠️ 如果已有配置文件：增量修改，不覆盖

### Step 8 — 最终自检 + 写入

- 检查需求匹配度（API、字段、流程是否与设计文档一致）
- 检查代码可编译性（import、类型、依赖是否完整）
- ⚠️ 如果发现编译问题：自动修复后重新检查
- 🔴 **检查点**：输出「生成计划预览」（将创建的目录/文件列表），请用户确认后再开始写入实际文件

### Step 9 — 写入文件

- 按 Step 4 逐层顺序依次创建文件
- ⚠️ 写入失败时：输出完整文件内容和路径，供手动创建

---

# 生成原则

1. **项目风格优先** — 不按主观想法写，而是按目标项目已有代码的风格写。先读已有文件，看它怎么写就怎么写。
2. **设计文档优先** — 所有逻辑、API、字段以设计文档为准，不擅自增减。
3. **风格冲突时** — 如果已有代码和设计文档在风格上不一致，以已有代码为准。