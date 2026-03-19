def generate_save_path():
    from config.DefaultConfig import CONFIG
    from config.paths import RESULTS_ROOT
    from config.strategy import normalize_strategy
    from datetime import datetime

    RESULTS_ROOT.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H-%M")

    strategy = normalize_strategy(CONFIG.link_adaptation.strategy)
    dir = timestamp + "_" + strategy.value + "_" + CONFIG.ai.data_mode

    results_dir = RESULTS_ROOT / dir
    results_dir.mkdir(parents=True, exist_ok=True)
    return str(results_dir)
