# metrics/delay.py
from config.DefaultConfig import CONFIG
import numpy as np


class DelayCalculator:
    def __init__(self, transmission_time):
        self.transmission_time = np.array(transmission_time)

    def calculate_average_delay(self):
        delay_list = CONFIG.scheduler.delay * self.transmission_time  # ʱ�ӵĵ�λ����ʱ�ӳ��Դ������
        return np.mean(delay_list)  # ͳһƽ��ʱ��
