from dataclasses import dataclass

"""创建一个结构体便于分类"""


@dataclass
class SimulationConfig:
    num_users: int
    duration: int
    tti_duration: float
    tti_length: int
    save_training_results: bool
    save_info: bool


@dataclass
class PhyLayerConfig:
    fft_size: int
    cp_length: int
    bandwidth: float
    num_symbols: int  #
    rb_bandwidth: float


@dataclass
class ChannelConfig:
    type: str
    snr: dict
    ar_model: dict


@dataclass
class LinkAdaptationConfig:
    strategy: str
    bler_target: float


@dataclass
class SchedulerConfig:
    type: str
    qos_requirements: dict
    delay: float


@dataclass
class AdvancedConfig:
    enable_visualization: bool
    log_level: str


@dataclass
class ShowConfig:
    plot_hist_snr: bool
    plot_throughput_distribution: bool
    plot_cqi_distribution: bool
    show_bler_analysis: bool
    print_summary_stats: bool
    plot_mcs_distribution: bool
    show_snr_mcsindex: bool
    show_delay_distribution: bool
    show_user_HistoryData: bool


@dataclass
class UserConfig:
    iot_params: dict
    citycar_params: dict


@dataclass
class GlobalConfig:
    simulation: SimulationConfig
    phy_layer: PhyLayerConfig
    channel: ChannelConfig
    link_adaptation: LinkAdaptationConfig
    scheduler: SchedulerConfig
    advanced: AdvancedConfig
    show: ShowConfig
    user: UserConfig


CONFIG = GlobalConfig(
    simulation = SimulationConfig(
        num_users = 1000,
        duration = 60,
        tti_duration = 1e-3,
        tti_length = 1000,
        save_training_results = False,
        save_info = True
        ),
    phy_layer = PhyLayerConfig(
        fft_size = 64,
        cp_length = 16,  # 循环前缀
        bandwidth = 10e9,  # 带宽设置为10GHZ
        num_symbols = 14,
        rb_bandwidth = 180e3,  # 一个资源块的带宽
        ),

    channel = ChannelConfig(
        type = "Rayleigh",
        snr = {
            "init_range": (0, 25),  # SNR范围(dB)
            "dynamic":    True,
            "medium":     16,  # 阴影衰落中值
            "sigma":      4,  # 阴影衰落标准差
            },
        ar_model = {
            "alpha":    0.9,
            "sigma_ar": 0.1  # 自相关系数
            }
        ),
    link_adaptation = LinkAdaptationConfig(
        strategy = "查表",  # DNN或查表
        bler_target = 0.1
        ),
    scheduler = SchedulerConfig(
        type = "round_robin",
        qos_requirements = {
            "video": {"max_delay": 50e-3, "min_rate": 1e6},
            "iot":   {"max_delay": 1.0, "min_rate": 10e3}
            },
        delay = 1e-3  # 1ms
        ),
    advanced = AdvancedConfig(
        enable_visualization = True,
        log_level = "INFO"
        ),

    # show = ShowConfig(
    #     plot_hist_snr = False,
    #     plot_throughput_distribution = False,
    #     plot_cqi_distribution = False,
    #     show_bler_analysis = False,
    #     print_summary_stats = True,
    #     plot_mcs_distribution = False,
    #     show_snr_mcsindex = False,
    #     show_delay_distribution = False,
    #     show_user_HistoryData = False
    #     ),
    show = ShowConfig(
        plot_hist_snr = True,
        plot_throughput_distribution = True,
        plot_cqi_distribution = True,
        show_bler_analysis = True,
        print_summary_stats = True,
        plot_mcs_distribution = True,
        show_snr_mcsindex = True,
        show_delay_distribution = True,
        show_user_HistoryData = True
        ),
    user = UserConfig(
        iot_params = {
            "speed":       0.5,  # 低速移动
            "filter_taps": 10,  # 低速场景无需过高阶数
            "fc":          2.4e9,  # 2.4GHz(载波频率/工作频率）
            # "Ts":          10e-3,  # 10ms
            "fd":          10  # 多普勒频移-步行用户为5-20HZ
            },
        citycar_params = {
            "speed":       15,  # 低速移动
            "filter_taps": 20,  # 3e8/(15*3.5e9*1e-3) ≈ 18.3 → 取20
            "fc":          3.5e9,  # 5G主流频段
            # "Ts":          1e-3,  # 1ms
            "fd":          100  # 多普勒频移-车载用户为50-300HZ
            },
        )
    )

# 测试调用
# print(CONFIG.simulation.num_users)
