# 小符同学
# python YYDS
# 开发时间： 2025/2/20 上午10:16

def font_setting():
    import matplotlib
    import platform

    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm

    # 查找支持中文的字体
    if platform.system() == 'Darwin':  # macOS 示例
        zh_font = fm.FontProperties(fname = '/System/Library/Fonts/Supplemental/Songti.ttc')  # macOS 示例
    elif platform.system() == 'Windows':  # Windows 示例
        zh_font = fm.FontProperties(fname = 'C:/Windows/Fonts/msyh.ttc')  # Windows 示例
    else:  # 抛出异常
        raise Exception("未知操作系统")

    # 设置全局字体
    plt.rcParams['font.family'] = zh_font.get_name()
    plt.rcParams['axes.unicode_minus'] = False
