# 小符同学
# python YYDS
# 开发时间： 2025/2/25 上午10:07
def update_config(config, **kwargs):
    """更新配置"""
    for key, value in kwargs.items():
        keys = key.split("__")
        sub_config = config
        for k in keys[:-1]:
            sub_config = getattr(sub_config, k)
        setattr(sub_config, keys[-1], value)
