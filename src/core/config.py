"""
配置加载模块
支持从 `config.yaml` 加载配置并提供默认值
"""
import os
from typing import Any, Dict, Optional

import yaml


DEFAULT_CONFIG = {
    "controller": {"type": "adb"},
    "adb": {"adb_path": "adb", "device_id": None},
    "screenshot": {"crop_ratios": [0.0, 0.2, 1.0, 0.7], "bw_threshold": 200},
    "llm": {"model": "gpt-4o", "api_key": None},
    "app": {"window_title": "BlueStacks App Player", "click_delay": 1.5, "debug_mode": False},
}


def load_config(path: Optional[str] = None) -> Dict[str, Any]:
    """加载 YAML 配置文件，返回一个配置字典

    Args:
        path: 配置文件路径，未提供时使用仓库根目录下的 `config.yaml`
    """
    if path is None:
        path = os.path.join(os.getcwd(), "config.yaml")

    config = DEFAULT_CONFIG.copy()
    try:
        with open(path, "r", encoding="utf-8") as f:
            user_cfg = yaml.safe_load(f) or {}
            # 深度合并（浅合并即可覆盖常见字段）
            for k, v in user_cfg.items():
                if isinstance(v, dict) and k in config:
                    config[k].update(v)
                else:
                    config[k] = v
    except FileNotFoundError:
        # 没有配置文件，返回默认配置
        return config
    except Exception:
        # 解析错误等，仍返回默认配置
        return config

    return config


def get(path: Optional[str] = None, key: Optional[str] = None, default: Any = None) -> Any:
    cfg = load_config(path)
    if key is None:
        return cfg
    parts = key.split(".")
    cur = cfg
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return default
    return cur
