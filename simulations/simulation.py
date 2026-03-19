import os
import sys


# 允许直接运行本文件时正确导入项目内模块
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from simulations.facade import SimulationFacade


def run_simulation():
    SimulationFacade().run()
