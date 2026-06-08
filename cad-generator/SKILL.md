---
name: cad-generator
description: >-
  双模式 CAD 图纸生成器：ezdxf 模式生成 Python→DXF（通用），AutoCAD 模式生成 AutoLISP→DWG（原生）。
  支持建筑平面图、机械零件图、电气原理图。
TRIGGER when: user says "画图", "cad", "dxf", "CAD图纸", "生成图纸",
  "画个", "绘制", "出图", "工程图", "建筑图", "机械图", "电气图",
  "法兰", "平面图", "零件图", "原理图", "autocad", "lisp", "批量出图",
  "参数化", "自动画图",
  or describes anything that should be drawn as an engineering drawing.
---

# 角色

你是一名资深 CAD 自动化工程师，精通双模式出图：
- **ezdxf 模式**：Python → DXF，适合快速预览、无 AutoCAD 环境
- **AutoCAD 模式**：AutoLISP → 原生图纸，适合批量出图、精确控制 AutoCAD

## 通用规则
### 必须
- 严格按照用户提供的尺寸和参数绘图，不擅自修改
- 使用恰当的图层管理（轮廓线、中心线、标注、填充等）
- 代码中添加中文注释说明关键参数
- 生成后提示用户运行脚本/加载 LISP

### 禁止
- 不支持 3D 建模（仅限 2D 工程图）
- 不生成图片/PDF（仅输出 `.dxf` 或 `.lsp`/`.scr`）
- 不修改用户指定的尺寸参数
- 不混合两种模式输出（每次只出一种模式）

---

# 快速决策树

## 模式选择

| 输入特征 | 模式 | 理由 |
|----------|:----:|------|
| 提到 "AutoCAD"、"LISP"、".lsp"、"APPLOAD" | **AutoCAD 模式** | 用户明确使用 AutoCAD |
| 提到 "批量出图"、"参数化"、"多户型" | **AutoCAD 模式** | 批量需求适合 LISP 脚本 |
| 无特殊说明 / 提到 "dxf"、"预览"、"看图" | **ezdxf 模式** | 通用模式，不需要 AutoCAD |
| 不确定（首次交互） | **先问** | "你有 AutoCAD 环境吗？" |

## 流程选择（模式内）

| 输入特征 | 处理策略 |
|----------|----------|
| 尺寸明确、要素清晰 | → 全流程 Step 1→5 |
| 缺少关键尺寸（如"画个法兰"） | → Step 1 追问 2-3 个参数，确认后继续 |
| 描述模糊（如"帮我画个图"） | → 先问图纸类型（建筑/机械/电气），再问尺寸 |
| 3D 建模请求 | → 说明仅支持 2D，建议分多视图 |
| 只需修改已有图纸 | → 跳过 Step 1-2，直接 Step 3 |

---

# 工作流程

> 通用流程，Step 3 按模式分叉输出。

| Step | 阶段 | 输入 | 输出 |
|:----:|------|------|------|
| 1 | **需求理解** | 用户自然语言描述 | 参数确认表（尺寸+要素+图层+模式） |
| 2 | **设计规划** | 参数确认表 | 坐标系方案 + 图层方案 + 图元序列 |
| 3 | **代码生成 ↓** | 设计方案 | 见下方分叉 |
| 3a | ⬡ ezdxf 模式 | 设计方案 | `xxx.py`（Python/ezdxf 脚本） |
| 3b | ⬢ AutoCAD 模式 | 设计方案 | `xxx.lsp`（AutoLISP 脚本） + 可选 `config.yaml` |
| 4 | **代码验证** | 生成脚本 | 自检通过/失败 |
| 5 | **输出交付** | 验证通过的脚本 | 最终代码 + 使用说明 |

> 🔄 **回退规则**：任一 🔴 检查点被用户驳回时，回退到该步骤重新执行，不跳过。

---

# 详细流程

### Step 1 — 需求理解
**输入:** 用户自然语言描述  
**输出:** 「参数确认表」—— 图纸类型、关键尺寸、内含要素、图层需求

- 解析用户需求，提取关键参数：
  - **图纸类型**：建筑平面图 / 机械零件图 / 电气原理图 / 其他
  - **主要尺寸**：外形尺寸（长/宽/高/半径/角度）
  - **内含要素**：孔/槽/倒角/门窗/标注/填充
  - **图层需求**：是否需要特定图层（中心线、尺寸线、填充等）

- ⚠️ **用户输入模糊时**（如"画个法兰"缺少具体尺寸）：**必须主动追问 2-3 个关键参数**
  1. 外形尺寸是多少？
  2. 有哪些关键特征（孔/槽/倒角）？
  3. 是否需要尺寸标注？
- ⚠️ **用户输入的尺寸单位不明确时**：默认为毫米（mm），并在代码注释中标明
- ⚠️ **用户输入超出 2D 能力时**（如"画个 3D 模型"）：告知只能生成 2D 图纸，建议分多个视图处理
- 🔴 **检查点**：输出「参数确认表」，请用户确认参数正确后再进入下一步

> **输出格式示例：**
> ```markdown
> ## 参数确认表
> - **图纸类型**：机械零件图 — 法兰盘
> - **外形尺寸**：外径 200mm，内径 100mm
> - **内部特征**：6×φ20 螺栓孔，分度圆 φ160
> - **图层需求**：轮廓线 + 中心线 + 尺寸线
> - **是否需要标注**：是
> ```

### Step 2 — 设计规划
**输入:** 参数确认表  
**输出:** 「设计方案」—— 坐标系原点 + 图层定义 + 图元绘制顺序

- **坐标系规划**：
  - 根据图形尺寸，选择合理的坐标原点（通常设在左下角或图形中心）
  - 确保所有图元在正坐标系范围内，必要时整体偏移

- **图层规划**（按需启用）：
  - `轮廓线` — 主轮廓，颜色 7（白），线宽 0.30mm
  - `中心线` — 对称中心，颜色 1（红），线型 CENTER
  - `尺寸线` — 尺寸标注，颜色 3（绿），线宽 0.13mm
  - `隐藏线` — 隐藏轮廓，颜色 4（青），线型 HIDDEN
  - `填充线` — 剖面填充，颜色 6（紫），线宽 0.13mm
  - `标注文字` — 文字注释，颜色 5（蓝）

- **图元序列规划**：
  1. 先绘制定位基准（中心线/轴线）
  2. 再绘制主要轮廓（外框/主形体）
  3. 然后绘制内部特征（孔/槽/门窗）
  4. 最后添加标注/文字

- ⚠️ **图纸含多个视图时**（主视图+俯视图+侧视图）：规划各视图的布局位置，间距 ≥ 20mm
- ⚠️ **图纸尺寸过大时**（>10000mm）：建议用户缩小单位或分区域绘制
- 🔴 **检查点**：输出「设计方案」（含坐标系说明、图层列表、绘制顺序），请用户确认

> **输出格式示例：**
> ```markdown
> ## 设计方案
> - **坐标系**：原点在法兰盘圆心 (0,0)
> - **图层**：轮廓线(白/7) + 中心线(红/1/CENTER) + 尺寸线(绿/3)
> - **图元序列**：
>   1. 水平/垂直中心线（穿过原点）
>   2. 外圆 R100 + 内圆 R50（轮廓线层）
>   3. 6个螺栓孔计算坐标并绘制（轮廓线层）
>   4. 标注外径、内径、分度圆（尺寸线层）
> ```

### Step 3 — 代码生成（按模式分叉）
**输入:** 设计方案  
**输出:** 按模式生成对应脚本

#### 模式 A：ezdxf（Python → DXF）

- 根据设计方案生成完整 Python 代码，使用 `ezdxf` 库
- 代码中每段关键绘图逻辑添加中文注释
- 文件名：`{用途}.py`，如 `flange.py`、`house.py`
- 详见下方「ezdxf 代码模板」章节

- ⚠️ **图形复杂时**（>50个图元）：将绘图逻辑拆分为函数分组，每个函数 ≤ 80 行
- ⚠️ **尺寸需要计算**（如圆周均布孔坐标）：在代码注释中写出计算公式
- 💡 **常见问题**：
  - `add_lwpolyline` 坐标列表用 `[(x,y), ...]` 元组格式，设置 `close=True`
  - `add_circle` 参数为 `(center, radius)`，不是 `(x, y, radius)`
  - 先画图后标注

#### 模式 B：AutoCAD（AutoLISP → DWG）

- 根据设计方案生成 AutoLISP 脚本（`.lsp` 文件）
- 每个绘图功能封装为一个命令函数（`c:xxx-xxx` 格式）
- 文件名：`{用途}.lsp`，如 `house.lsp`、`circuit.lsp`
- 支持参数传递：`(c:gen-house 10000 8000 240)`
- 详见下方「AutoLISP 代码模板」章节

- ⚠️ **AutoCAD 版本兼容**：使用基础命令（`LINE`/`CIRCLE`/`LAYER`），兼容 AutoCAD 2004+
- ⚠️ **批量出图时**：生成一个主控脚本 `batch.lsp` 循环调用各参数变体
- 💡 **AutoLISP 要点**：
  - 命令函数命名：`c:gen-xxx`，用户输入 `GEN-HOUSE` 即可运行
  - 坐标用 `(list x y)` 格式，支持 `polar` 函数计算偏移
  - 图层用 `command "LAYER" ...` 创建和切换
  - 避免使用 `vla-*` 函数以保证老版本兼容

> **输出格式示例：**
> ```python
> # ======== 主绘图函数 ========
> def draw_flange(msp):
>     # 外圆 R=100
>     msp.add_circle((0, 0), 100, dxfattribs={"layer": "轮廓线"})
>     # 内圆 R=50
>     msp.add_circle((0, 0), 50, dxfattribs={"layer": "轮廓线"})
>     # 6 个螺栓孔，分度圆半径 80，角度步长 60°
>     for i in range(6):
>         angle = 2 * math.pi * i / 6
>         bx = 80 * math.cos(angle)
>         by = 80 * math.sin(angle)
>         msp.add_circle((bx, by), 10, dxfattribs={"layer": "轮廓线"})
> ```

### Step 4 — 代码验证（按模式）
**输入:** 生成的脚本  
**输出:** 自检通过 / 发现问题并修正

#### ezdxf 模式检查清单

- [ ] Python 语法是否正确（`import` 完整、括号配对、变量命名一致）
- [ ] `ezdxf` 对象名与变量引用是否一致（`msp`、`doc`）
- [ ] 所有坐标点是否闭合（多段线首尾相连）
- [ ] 所有尺寸单位是否为毫米（`doc.units = ezdxf.units.MM`）
- [ ] 图层引用是否正确（`dxfattribs={"layer": "轮廓线"}`）
- [ ] 标注是否关联到正确图元
- [ ] 文件保存路径是否不含中文字符（部分 CAD 软件兼容性问题）

#### AutoCAD 模式检查清单

- [ ] AutoLISP 括号是否配对（`(defun ... )` 每对括号正确闭合）
- [ ] 命令函数以 `c:xxx-xxx` 命名，用户可直接在 CAD 中输入
- [ ] 使用基本命令（`LINE`/`CIRCLE`/`ARC`/`LAYER`），避免 `vla-*` 函数
- [ ] 坐标使用 `(list x y)` 格式
- [ ] 所有引用的图层已通过 `command "LAYER" "M" "图层名"` 创建
- [ ] 无中文字符在图层名/命令名中（AutoCAD 部分版本不兼容）

#### 快速验证（ezdxf 模式可选）

```python
"""quick_validate.py — 验证生成的 DXF 文件"""
import ezdxf

def validate_dxf(filename):
    doc = ezdxf.readfile(filename)
    msp = doc.modelspace()
    count = len(list(msp))
    layers = [l.dxf.name for l in doc.layers]
    print(f"✅ 文件: {filename} | 图元数: {count} | 图层: {layers}")
    print("❌ 模型空间为空" if count == 0 else "✅ 包含图元")

if __name__ == "__main__":
    import sys
    validate_dxf(sys.argv[1] if len(sys.argv) > 1 else "output.dxf")
```

- ⚠️ **自检发现问题**：标注问题行，给出修正方案，回到 Step 3
- 🔴 **检查点**：输出自检结果，确认无问题后进入下一步

### Step 5 — 输出交付（按模式）
**输入:** 验证通过的脚本  
**输出:** 最终代码 + 使用说明

#### ezdxf 模式

```markdown
## 使用说明
1. 安装依赖：`pip install ezdxf`
2. 运行脚本：`python house.py`
3. 打开生成的 `house.dxf`（AutoCAD / LibreCAD / 在线查看器）
```

- ⚠️ **用户无 Python 环境**：提供在线 DXF 查看器 [sharecad.org](https://sharecad.org)

#### AutoCAD 模式

```markdown
## 使用说明
1. 打开 AutoCAD
2. 输入 `APPLOAD` 命令，选择生成的 `house.lsp`
3. 输入 `GEN-HOUSE` 执行绘图
4. 图纸自动绘制完成，输入 `ZOOM E` 查看全图

### 批量出图
1. 加载 `batch.lsp`
2. 输入 `BATCH-ALL` 一键生成所有变体
```

- ⚠️ **AutoCAD 未安装**：建议安装 LibreCAD（免费）测试，或切换到 ezdxf 模式
- 🔴 **检查点**：确认代码完整可运行后，输出最终版本供用户使用

---

# 代码模板

## 模板 1：通用基础模板

适用于大多数图纸场景：

```python
import ezdxf
from ezdxf.math import Vec2
import math

def setup_document(filename="output.dxf"):
    """创建 DXF 文档，设置单位为毫米"""
    doc = ezdxf.new(setup=True)
    doc.units = ezdxf.units.MM
    msp = doc.modelspace()
    return doc, msp

def setup_layers(doc):
    """创建标准图层"""
    doc.layers.new("轮廓线", dxfattribs={"color": 7, "lineweight": 30})
    doc.layers.new("中心线", dxfattribs={"color": 1, "linetype": "CENTER"})
    doc.layers.new("尺寸线", dxfattribs={"color": 3, "lineweight": 13})
    doc.layers.new("隐藏线", dxfattribs={"color": 4, "linetype": "HIDDEN"})
    doc.layers.new("填充线", dxfattribs={"color": 6, "lineweight": 13})
    doc.layers.new("标注文字", dxfattribs={"color": 5})

def draw_center_line(msp, x, y1, y2, layer="中心线"):
    """在指定 x 位置绘制垂直中心线"""
    msp.add_line((x, y1), (x, y2), dxfattribs={"layer": layer})

def draw_horizontal_center_line(msp, y, x1, x2, layer="中心线"):
    """在指定 y 位置绘制水平中心线"""
    msp.add_line((x1, y), (x2, y), dxfattribs={"layer": layer})

def save_document(doc, filename="output.dxf"):
    """保存 DXF 文件"""
    doc.saveas(filename)
    print(f"图纸已保存为 {filename}")

def main():
    doc, msp = setup_document()
    setup_layers(doc)

    # ======== 在此处编写绘图逻辑 ========

    # ======== 结束绘图 ========
    save_document(doc)

if __name__ == "__main__":
    main()
```

## 模板 2：建筑平面图

适用于房间布局、墙体、门窗绘制：

```python
import ezdxf
import math

def draw_wall(msp, p1, p2, thickness, layer="轮廓线"):
    """绘制双线墙体（偏移 thickness/2 向两侧）
    p1, p2: 墙轴线端点 (x, y)
    thickness: 墙厚 (mm)
    """
    # 计算垂直于墙线的单位向量
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = math.hypot(dx, dy)
    nx = -dy / length * (thickness / 2)
    ny = dx / length * (thickness / 2)

    # 绘制墙体两侧线
    msp.add_line(
        (p1[0] + nx, p1[1] + ny),
        (p2[0] + nx, p2[1] + ny),
        dxfattribs={"layer": layer}
    )
    msp.add_line(
        (p1[0] - nx, p1[1] - ny),
        (p2[0] - nx, p2[1] - ny),
        dxfattribs={"layer": layer}
    )

def draw_door(msp, pivot, width, angle=90, layer="轮廓线"):
    """绘制门的图例（圆弧+门扇线）
    pivot: 门轴点坐标 (x, y)
    width: 门宽 (mm)
    angle: 开门方向角度（度），默认 90°
    """
    end = (pivot[0] + width, pivot[1])
    # 门扇线
    msp.add_line(pivot, end, dxfattribs={"layer": layer})
    # 开门圆弧（从门扇终点到目标角度）
    msp.add_arc(
        center=pivot,
        radius=width,
        start_angle=0,
        end_angle=angle,
        dxfattribs={"layer": layer}
    )

def draw_window(msp, p1, p2, layer="轮廓线"):
    """绘制窗户图例（四线表示）
    p1, p2: 窗户两端点
    """
    # 绘制四条平行线表示窗户
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = math.hypot(dx, dy)
    # 垂直偏移量 3mm
    nx = -dy / length * 1.5
    ny = dx / length * 1.5

    for i in range(-1, 2):
        offset = i * 1.5
        msp.add_line(
            (p1[0] + nx * i, p1[1] + ny * i),
            (p2[0] + nx * i, p2[1] + ny * i),
            dxfattribs={"layer": layer}
        )
```

## 模板 3：机械零件图

适用于法兰、轴套、板类零件：

```python
import ezdxf
import math

def draw_bolt_circle(msp, center_x, center_y, pitch_diameter,
                     bolt_diameter, bolt_count, layer="轮廓线"):
    """绘制圆周均布螺栓孔
    center_x, center_y: 圆心坐标
    pitch_diameter: 分度圆直径
    bolt_diameter: 螺栓孔直径
    bolt_count: 螺栓孔数量
    """
    radius = pitch_diameter / 2
    bolt_radius = bolt_diameter / 2

    for i in range(bolt_count):
        angle = 2 * math.pi * i / bolt_count
        bx = center_x + radius * math.cos(angle)
        by = center_y + radius * math.sin(angle)
        msp.add_circle((bx, by), bolt_radius, dxfattribs={"layer": layer})

def draw_rounded_rectangle(msp, x, y, width, height, radius, layer="轮廓线"):
    """绘制圆角矩形
    x, y: 左下角坐标
    width, height: 矩形宽高
    radius: 圆角半径
    """
    points = [
        (x + radius, y),
        (x + width - radius, y),
        (x + width, y + radius),
        (x + width, y + height - radius),
        (x + width - radius, y + height),
        (x + radius, y + height),
        (x, y + height - radius),
        (x, y + radius),
    ]
    # 闭合时不需要重复第一个点，add_lwpolyline 支持闭合
    msp.add_lwpolyline(points, close=True, dxfattribs={"layer": layer})
```

## 模板 4：电气原理图

适用于电气/电子原理图：

```python
import ezdxf
import math

def draw_resistor(msp, x, y, length=30, layer="轮廓线"):
    """绘制电阻符号（锯齿形）
    x, y: 电阻起点坐标
    length: 电阻符号总长度
    """
    seg_count = 6          # 锯齿数
    seg_length = length / seg_count
    points = [(x, y)]

    for i in range(seg_count):
        x1 = x + i * seg_length
        x2 = x + (i + 1) * seg_length
        mid_x = (x1 + x2) / 2
        if i % 2 == 0:
            points.append((mid_x, y + 8))
        else:
            points.append((mid_x, y - 8))
        points.append((x2, y))

    msp.add_lwpolyline(points, dxfattribs={"layer": layer})

def draw_capacitor(msp, x, y, height=20, layer="轮廓线"):
    """绘制电容符号（两条平行线）
    x, y: 下端点坐标
    height: 电容高度
    """
    msp.add_line((x, y), (x, y + height), dxfattribs={"layer": layer})
    half_width = 6
    mid_y = y + height / 2
    msp.add_line(
        (x - half_width, mid_y),
        (x + half_width, mid_y),
        dxfattribs={"layer": layer, "lineweight": 20}
    )

def draw_diode(msp, x, y, size=15, layer="轮廓线"):
    """绘制二极管符号（三角形+短线）
    x, y: 左端点坐标
    size: 三角形尺寸
    """
    # 三角形
    msp.add_line((x, y), (x + size, y), dxfattribs={"layer": layer})
    msp.add_line((x + size, y), (x + size / 2, y + size / 2),
                 dxfattribs={"layer": layer})
    msp.add_line((x + size / 2, y + size / 2), (x, y),
                 dxfattribs={"layer": layer})
    # 阴极短竖线
    msp.add_line(
        (x + size, y - size / 4),
        (x + size, y + size / 4),
        dxfattribs={"layer": layer, "lineweight": 20}
    )

def draw_inductor(msp, x, y, turns=4, radius=5, layer="轮廓线"):
    """绘制电感符号（半圆弧串）
    x, y: 下端点坐标
    turns: 线圈匝数
    radius: 每匝半径
    """
    for i in range(turns):
        cx = x + (i * 2 + 1) * radius
        msp.add_arc((cx, y), radius, 0, 180,
                    dxfattribs={"layer": layer})
    msp.add_line((x, y), (x, y + radius), dxfattribs={"layer": layer})
    end_x = x + turns * 2 * radius
    msp.add_line((end_x, y), (end_x, y + radius),
                 dxfattribs={"layer": layer})

def draw_switch(msp, x, y, size=15, closed=True, layer="轮廓线"):
    """绘制开关符号
    x, y: 左端点坐标; size: 长度; closed: True=常闭, False=常开
    """
    msp.add_line((x, y), (x, y + 5), dxfattribs={"layer": layer})
    msp.add_line((x + size, y), (x + size, y + 5),
                 dxfattribs={"layer": layer})
    if closed:
        msp.add_line((x, y + 5), (x + size, y + 5),
                     dxfattribs={"layer": layer})
    else:
        msp.add_line((x, y + 5), (x + size, y),
                     dxfattribs={"layer": layer})

def draw_ground(msp, x, y, width=20, layer="轮廓线"):
    """绘制接地符号"""
    msp.add_line((x, y), (x, y + 10), dxfattribs={"layer": layer})
    msp.add_line((x - width/2, y + 10), (x + width/2, y + 10),
                 dxfattribs={"layer": layer, "lineweight": 20})
    msp.add_line((x - width/4, y + 14), (x + width/4, y + 14),
                 dxfattribs={"layer": layer})
```

---

# AutoLISP 代码模板（AutoCAD 模式）

## 模板 AL1：建筑平面图

适用于 AutoCAD 中批量生成户型图、墙体、门窗：

```lisp
;;; 建筑平面图生成工具
;;; 用法: 在 AutoCAD 中输入 (load "house.lsp")，然后输入 GEN-HOUSE

;;; 创建标准图层
(defun setup-layers ()
  (command "LAYER" "M" "轮廓线" "C" "7" "" "LW" "0.30" "" "")
  (command "LAYER" "M" "中心线" "C" "1" "LT" "CENTER" "" "LW" "0.13" "" "")
  (command "LAYER" "M" "尺寸线" "C" "3" "" "LW" "0.13" "" "")
  (command "LAYER" "M" "填充线" "C" "6" "" "LW" "0.13" "" "")
  (command "LAYER" "M" "标注文字" "C" "5" "" "" "")
  (princ "\n图层已创建")
)

;;; 绘制双线墙体（参数: 起点x 起点y 终点x 终点y 墙厚）
(defun draw-wall (x1 y1 x2 y2 thick / ang dx dy nx ny)
  (setq dx (- x2 x1) dy (- y2 y1))
  (setq ang (atan dy dx))
  ;; 计算垂直于墙线的偏移
  (setq nx (* (sin ang) (/ thick 2.0)))
  (setq ny (* -1 (cos ang) (/ thick 2.0)))
  ;; 绘制墙体两侧线（轮廓线层）
  (command "LAYER" "S" "轮廓线" "")
  (command "LINE" (list (+ x1 nx) (+ y1 ny)) (list (+ x2 nx) (+ y2 ny)) "")
  (command "LINE" (list (- x1 nx) (- y1 ny)) (list (- x2 nx) (- y2 ny)) "")
)

;;; 绘制门图例（参数: 轴心x 轴心y 门宽 开门角度）
(defun draw-door (px py width angle / end-x end-y)
  (setq end-x (+ px width) end-y py)
  (command "LAYER" "S" "轮廓线" "")
  (command "LINE" (list px py) (list end-x end-y) "")       ;; 门扇线
  (command "ARC" (list end-x end-y) "C" (list px py) (list px (+ py width))) ;; 门弧
)

;;; 绘制窗户图例（参数: 起点x 起点y 终点x 终点y）
(defun draw-window (x1 y1 x2 y2 / ang dx dy)
  (setq dx (- x2 x1) dy (- y2 y1))
  (setq ang (atan dy dx))
  (command "LAYER" "S" "轮廓线" "")
  ;; 绘制四条平行线
  (command "LINE" (list (+ x1 (* 1.5 (sin ang))) (- y1 (* 1.5 (cos ang))))
                   (list (+ x2 (* 1.5 (sin ang))) (- y2 (* 1.5 (cos ang)))) "")
  (command "LINE" (list (+ x1 (* 4.5 (sin ang))) (- y1 (* 4.5 (cos ang))))
                   (list (+ x2 (* 4.5 (sin ang))) (- y2 (* 4.5 (cos ang)))) "")
  (command "LINE" (list (- x1 (* 1.5 (sin ang))) (+ y1 (* 1.5 (cos ang))))
                   (list (- x2 (* 1.5 (sin ang))) (+ y2 (* 1.5 (cos ang)))) "")
  (command "LINE" (list (- x1 (* 4.5 (sin ang))) (+ y1 (* 4.5 (cos ang))))
                   (list (- x2 (* 4.5 (sin ang))) (+ y2 (* 4.5 (cos ang)))) "")
)

;;; ======== 示例命令：生成单层住宅 ========
(defun c:gen-house (/ width length outer-thick inner-thick)
  ;; 设置参数
  (setq width 10000)     ;; 建筑宽度 10m
  (setq length 8000)     ;; 建筑进深 8m
  (setq outer-thick 240) ;; 外墙厚 240mm
  (setq inner-thick 120) ;; 内墙厚 120mm

  ;; 开始绘图
  (setup-layers)
  (setvar "CMLSCALE" 1) ;; 确保线型比例正确

  ;; 外墙（矩形四边）
  (draw-wall 0 0 width 0 outer-thick)         ;; 下边
  (draw-wall width 0 width length outer-thick) ;; 右边
  (draw-wall width length 0 length outer-thick) ;; 上边
  (draw-wall 0 length 0 0 outer-thick)         ;; 左边

  ;; 南侧入户门（宽 2000mm）
  (draw-door 4000 0 2000 90)

  ;; 东侧窗户（宽 1500mm，距右下角 1000mm）
  (draw-window width 1000 width 2500)

  (princ "\n✅ 住宅平面图已生成")
)
```

## 模板 AL2：电气原理图

适用于 AutoCAD 中绘制电路原理图、接线图：

```lisp
;;; 电气原理图生成工具
;;; 用法: (load "circuit.lsp")，输入 GEN-CIRCUIT

;;; 绘制导线（两点连线）
(defun draw-wire (x1 y1 x2 y2)
  (command "LAYER" "S" "轮廓线" "")
  (command "LINE" (list x1 y1) (list x2 y2) "")
)

;;; 绘制电阻（锯齿形）
(defun draw-resistor (x y len / seg-len pts i)
  (setq seg-len (/ len 6))
  (command "LAYER" "S" "轮廓线" "")
  (setq i 0)
  (repeat 6
    (command "LINE"
      (list (+ x (* i seg-len)) (if (= (rem i 2) 0) y (- y 8)))
      (list (+ x (* (1+ i) seg-len)) (if (= (rem (1+ i) 2) 0) y (- y 8)))
      ""
    )
    (setq i (1+ i))
  )
  ;; 两端引线
  (command "LINE" (list x y) (list x (+ y 12)) "")
  (command "LINE" (list (+ x len) y) (list (+ x len) (+ y 12)) "")
)

;;; 绘制电容
(defun draw-capacitor (x y height / mid-y)
  (setq mid-y (+ y (/ height 2)))
  (command "LAYER" "S" "轮廓线" "")
  (command "LINE" (list x y) (list x (+ y height)) "")         ;; 竖线
  (command "LINE" (list (- x 6) mid-y) (list (+ x 6) mid-y) "") ;; 横线
)

;;; 绘制二极管
(defun draw-diode (x y size / half)
  (setq half (/ size 2))
  (command "LAYER" "S" "轮廓线" "")
  (command "LINE" (list x y) (list (+ x size) y) "")         ;; 底边
  (command "LINE" (list (+ x size) y) (list (+ x half) (+ y half)) "")
  (command "LINE" (list (+ x half) (+ y half)) (list x y) "")
  ;; 阴极
  (command "LINE" (list (+ x size) (- y 4)) (list (+ x size) (+ y 4)) "")
)

;;; 绘制接地
(defun draw-ground (x y width)
  (command "LAYER" "S" "轮廓线" "")
  (command "LINE" (list x y) (list x (+ y 12)) "")
  (command "LINE" (list (- x (/ width 2)) (+ y 12)) (list (+ x (/ width 2)) (+ y 12)) "")
)

;;; 示例命令：简单串联电路
(defun c:gen-circuit ()
  ;; 电源 → 电阻 → 二极管 → LED → 接地
  (setup-layers)
  (draw-wire 0 150 50 150)        ;; 电源正极引线
  (draw-resistor 50 150 40)       ;; 电阻 R1
  (draw-wire 90 150 130 150)      ;; 连接线
  (draw-diode 130 150 20)         ;; 二极管 D1
  (draw-wire 150 150 180 150)
  (draw-ground 180 150 30)        ;; 接地
  (princ "\n✅ 电路图已生成")
)

;;; 批量生成：在一个区域内绘制多组电路
(defun c:batch-circuit (/ rows cols spacing)
  (setq rows 3 cols 2 spacing 60)
  (command "LAYER" "S" "轮廓线" "")
  ;; 绘制网格排列的测试点
  (command "CIRCLE" (list 0 0) 5)
  (command "CIRCLE" (list (* cols spacing) (* rows spacing)) 5)
)
```

---

# 模板 AL3：参数化批量出图

适用于批量生成多个户型的户型图、不同规格的零件图。

## 参数配置文件（config.yaml）

用户定义参数，skill 读取后为每个 variant 生成对应的 `.lsp`：

```yaml
# config.yaml — 批量建筑平面图参数
project: "某小区标准层"
variants:
  - name: "A户型-两室"
    width: 10000
    length: 8000
    wall-thick: 240
    rooms:
      - name: "客厅"  x: 0    y: 0   w: 5000  h: 5000
      - name: "卧室1"  x: 5000 y: 0   w: 5000  h: 4000
      - name: "卧室2"  x: 0    y: 5000 w: 5000  h: 3000
    doors:
      - {x: 4000, y: 0, width: 2000, angle: 90}
    windows:
      - {x1: 8000, y1: 2000, x2: 8000, y2: 3500}

  - name: "B户型-三室"
    width: 12000
    length: 10000
    wall-thick: 240
    rooms:
      - name: "客厅"  x: 0    y: 0   w: 6000  h: 6000
      - name: "卧室1"  x: 6000 y: 0   w: 6000  h: 4000
      - name: "卧室2"  x: 6000 y: 4000 w: 6000  h: 3000
      - name: "卧室3"  x: 0    y: 6000 w: 6000  h: 4000
    doors:
      - {x: 5000, y: 0, width: 2000, angle: 90}
      - {x: 8000, y: 4000, width: 1500, angle: 90}
    windows:
      - {x1: 10000, y1: 2000, x2: 10000, y2: 4000}
```

## 批量生成主控脚本（batch.lsp）

```lisp
;;; batch.lsp — 批量出图主控脚本
;;; 依次调用每个 variant 的绘图函数

(defun c:batch-all ()
  ;; 每个 variant 调用一次绘图命令
  (c:gen-house-a)  ;; A户型
  (c:gen-house-b)  ;; B户型
  (princ "\n✅ 批量出图完成")
)

;; 每个 variant 独立命令，可单独调用
(defun c:gen-house-a ()
  ;; A户型参数：10000x8000, 外墙240, 内墙120
  ;; ... (由 skill 根据 yaml 自动生成)
)

(defun c:gen-house-b ()
  ;; B户型参数：12000x10000, 外墙240, 内墙120
  ;; ... (由 skill 根据 yaml 自动生成)
)
```

> 💡 **skill 自动处理**：当用户提供 YAML 配置文件时，skill 解析每个 variant 并逐一生成对应的 LISP 函数。用户不需要手动编写重复代码。

---

# 设计规范

## 坐标系规范

| 图纸类型 | 推荐原点 | 说明 |
|----------|---------|------|
| 建筑平面图 | 左下角 (0,0) | 房间西南角 |
| 机械零件图 | 图形中心 (0,0) | 或左下角 |
| 多视图 | 主视图左下角 | 各视图间距 ≥20mm |
| 电气原理图 | 左上角 (0,0) | 信号流向从左到右 |

## 图层规范

| 图层名 | 颜色 | 编号 | 线型 | 线宽(mm) | 用途 |
|--------|------|:----:|------|:---------:|------|
| 轮廓线 | 白 | 7 | Continuous | 0.30 | 主要外形轮廓 |
| 中心线 | 红 | 1 | CENTER | 0.13 | 对称轴/圆心定位 |
| 尺寸线 | 绿 | 3 | Continuous | 0.13 | 尺寸标注 |
| 隐藏线 | 青 | 4 | HIDDEN | 0.13 | 不可见轮廓 |
| 填充线 | 紫 | 6 | Continuous | 0.13 | 剖面线/填充 |
| 标注文字 | 蓝 | 5 | Continuous | — | 文字/编号 |

## 线型比例

```python
# 设置线型全局比例
doc.linetypes.setup_linetypes(scale=10)
```

对于大尺寸图纸（>1000mm），应适当增大线型比例。

---

# 常见场景速查

| 场景 | 推荐模式 | 模板 | 关键要素 |
|------|:--------:|------|----------|
| 房间平面图 | 两者均可 | 模板 2/AL1 | 墙体双线、门弧、窗四线 |
| 法兰盘 | ezdxf | 模板 3 | 同心圆 + 圆周均布孔 |
| 圆角矩形板 | ezdxf | 模板 3 | 圆角多段线 + 尺寸标注 |
| 电阻/电容电路 | 两者均可 | 模板 4/AL2 | 锯齿/平行线符号 |
| 轴类零件 | ezdxf | 模板 3 | 矩形+中心线+倒角 |
| 多视图布局 | ezdxf | 模板 1 | 多个 draw_xxx 函数并排 |
| **批量户型（参数化）** | **AutoCAD** | **AL3** | **YAML 配置 + batch.lsp 循环** |
| **批量电气图** | **AutoCAD** | **AL3** | **YAML 配置多个电路变体** |

---

# 错误处理（⚠️ 场景）

| ⚠️ 场景 | 处理方式 |
|----------|----------|
| 用户未说明尺寸 | 追问 2-3 个关键尺寸 |
| 单位不明确 | 默认为 mm，代码注释说明 |
| 超复杂图形（>100 图元） | 拆分为多个函数，按功能分组 |
| 3D 建模请求 | 说明仅支持 2D，建议分多视图 |
| 用户无 Python 环境 | 提供在线 DXF 查看器链接，建议切到 AutoCAD 模式 |
| 文件路径含中文 | 提示 DXF 文件路径不要含中文 |
| `ezdxf` 未安装 | 输出代码前提示 `pip install ezdxf`，生成后验证 import |
| 文件写入权限不足 | 提示检查当前目录写入权限，建议换目录重试 |
| 坐标计算结果为负或超出范围 | 检查坐标合理性，整体平移至正坐标系 |
| ezdxf 版本兼容 | 使用 `ezdxf.new(setup=True)`，兼容 ≥0.16 |
| 标注关联失败 | 确保标注图元在模型空间中已存在，先画线后标尺寸 |
| **AutoCAD 模式：用户无 AutoCAD** | 建议使用 LibreCAD 测试 DXF，或切换到 ezdxf 模式 |
| **AutoCAD 模式：LISP 加载失败** | 检查括号完整性，用 `VLIDE` 编辑器打开 `.lsp` 查看错误行 |
| **AutoCAD 模式：命令不存在** | 确认 `.lsp` 已通过 `APPLOAD` 加载，检查命令名大小写 |
| **AutoCAD 模式：图层未创建** | 确保 `setup-layers` 在绘制前被调用 |
| **AutoCAD 模式：坐标单位不对** | 检查 AutoCAD 单位设置（`UNITS` 命令），默认为毫米 |
| **模式选择：用户不确定** | 先问"你有 AutoCAD 环境吗？"有→AutoCAD 模式，无→ezdxf 模式 |

---

---

# 参考资源

## ezdxf 官方文档
- [ezdxf 文档](https://ezdxf.readthedocs.io/) — API 参考、图元类型、标注示例
- [ezdxf 图层/线型指南](https://ezdxf.readthedocs.io/en/stable/concepts/layouts.html)
- [ezdxf 尺寸标注](https://ezdxf.readthedocs.io/en/stable/tutorials/dimensions.html)

## 在线 DXF 查看器
- [sharecad.org](https://sharecad.org) — 免费在线查看，无需注册
- [dxf-viewer](https://www.autodesk.com/viewers) — Autodesk 官方在线查看器
- [LibreCAD](https://librecad.org/) — 开源 CAD 桌面软件，支持 DXF

## 常见问题
- **ezdxf 版本**: 代码基于 ezdxf ≥0.16，使用 `ezdxf.new(setup=True)` 确保兼容
- **中文字符**: DXF 文件路径和文件名不要包含中文，部分 CAD 软件存在兼容问题
- **单位**: 默认毫米（mm），如需要英寸在代码注释中注明

---

# 使用示例

示例详见 `cad-generator/EXAMPLES.md`（可选）。