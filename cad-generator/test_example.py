"""
cad-generator 测试示例
用法：python test_example.py

验证 skill 能否正常生成 DXF 图纸：
  1. 法兰盘 — 同心圆 + 圆周均布螺栓孔
  2. 验证 DXF 文件完整性
"""
import ezdxf
import math
import os


# ==================== 法兰盘 ====================

def draw_flange(filename="test_flange.dxf"):
    """绘制法兰盘：外径200、内径100、6×φ20螺栓孔、分度圆φ160"""
    doc = ezdxf.new(setup=True)
    doc.units = ezdxf.units.MM
    msp = doc.modelspace()

    # 图层
    doc.layers.new("轮廓线", dxfattribs={"color": 7, "lineweight": 30})
    doc.layers.new("中心线", dxfattribs={"color": 1, "linetype": "CENTER"})
    doc.layers.new("尺寸线", dxfattribs={"color": 3, "lineweight": 13})

    # 中心线
    msp.add_line((-130, 0), (130, 0), dxfattribs={"layer": "中心线"})
    msp.add_line((0, -130), (0, 130), dxfattribs={"layer": "中心线"})

    # 外圆 R100
    msp.add_circle((0, 0), 100, dxfattribs={"layer": "轮廓线"})
    # 内圆 R50
    msp.add_circle((0, 0), 50, dxfattribs={"layer": "轮廓线"})

    # 6个螺栓孔，分度圆半径80
    for i in range(6):
        angle = 2 * math.pi * i / 6
        bx = 80 * math.cos(angle)
        by = 80 * math.sin(angle)
        msp.add_circle((bx, by), 10, dxfattribs={"layer": "轮廓线"})

    # 尺寸标注
    dim = msp.add_aligned_dim(p1=(-100, 0), p2=(100, 0), distance=-40)
    dim.render()

    doc.saveas(filename)
    return filename


# ==================== 验证 ====================

def validate(filename):
    """验证 DXF 文件完整性"""
    doc = ezdxf.readfile(filename)
    msp = doc.modelspace()
    count = len(list(msp))
    layers = [l.dxf.name for l in doc.layers]

    print(f"📄 {filename}")
    print(f"  图元数: {count}")
    print(f"  图层:   {layers}")

    assert count > 0, "❌ 模型空间为空"
    assert "轮廓线" in layers, "❌ 缺少轮廓线图层"
    assert "中心线" in layers, "❌ 缺少中心线图层"
    print("  ✅ 验证通过")


# ==================== 主流程 ====================

def main():
    print("=" * 40)
    print("cad-generator 测试示例")
    print("=" * 40)

    # 生成法兰盘
    print("\n1️⃣  生成法兰盘 DXF...")
    f = draw_flange()
    assert os.path.exists(f), f"❌ 文件 {f} 未生成"
    print(f"   ✅ 已生成: {f}")

    # 验证
    print("\n2️⃣  验证 DXF 文件...")
    validate(f)

    # 清理
    os.remove(f)
    print(f"\n3️⃣  清理: {f} 已删除")
    print("\n✅ 全部测试通过")


if __name__ == "__main__":
    main()