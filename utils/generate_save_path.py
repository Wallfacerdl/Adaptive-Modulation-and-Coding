def generate_save_path():
    from config.DefaultConfig import CONFIG
    import os
    from datetime import datetime

    # 先创建results文件夹
    if not os.path.exists("results"):
        os.makedirs("results")
    # 再在子目录下创建当前时间子文件夹
    timestamp = datetime.now().strftime("%Y%m%d_%H")
    results_dir = os.path.join("results", timestamp)
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    # 使用绝对路径
    results_path = os.path.abspath(results_dir)
    return results_path
