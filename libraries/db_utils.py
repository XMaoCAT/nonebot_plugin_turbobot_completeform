import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from nonebot import logger

from ..config import Config

_data_file = Path(Config.data_file)
logger.info(f"Turbobot 数据文件路径: {_data_file}")


def _load_data() -> dict:
    """加载JSON数据"""
    if _data_file.exists():
        try:
            with open(_data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"users": {}}
    return {"users": {}}


def _save_data(data: dict):
    """保存JSON数据"""
    with open(_data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_already_bound(qqid: str) -> bool:
    """检查用户是否已经绑定"""
    data = _load_data()
    return qqid in data.get("users", {})


def get_bot_key(qqid: str) -> Optional[str]:
    """获取用户的bot_key"""
    data = _load_data()
    user = data.get("users", {}).get(qqid)
    return user.get("bot_key") if user else None


def bind_user(qqid: str, bot_token: str, bot_key: str):
    """绑定用户信息"""
    data = _load_data()
    if "users" not in data:
        data["users"] = {}
    data["users"][qqid] = {
        "bot_token": bot_token,
        "bot_key": bot_key,
        "bind_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    _save_data(data)


def unbind_user(qqid: str):
    """解除用户绑定"""
    data = _load_data()
    if qqid in data.get("users", {}):
        del data["users"][qqid]
        _save_data(data)
