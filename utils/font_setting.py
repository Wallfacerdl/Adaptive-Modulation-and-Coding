# 小符同学
# python YYDS
# 开发时间： 2025/2/20 上午10:16

def font_setting():
    import matplotlib
    import os
    import platform

    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm

    # 查找支持中文的字体
    if platform.system() == 'Darwin':  # macOS 示例
        zh_font = fm.FontProperties(fname='/System/Library/Fonts/Supplemental/Songti.ttc')
    elif platform.system() == 'Windows':  # Windows 示例
        zh_font = fm.FontProperties(fname='C:/Windows/Fonts/msyh.ttc')
    else:  # Linux / 其他系统
        linux_font_candidates = [
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        ]
        font_path = next((p for p in linux_font_candidates if os.path.exists(p)), None)
        zh_font = fm.FontProperties(fname=font_path) if font_path else None

    # 设置全局字体
    if zh_font:
        plt.rcParams['font.family'] = zh_font.get_name()
    else:
        plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.unicode_minus'] = False
