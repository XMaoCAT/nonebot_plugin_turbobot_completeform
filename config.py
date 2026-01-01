from pathlib import Path
from typing import List
import os

# 获取插件目录的绝对路径
_PLUGIN_DIR = Path(os.path.dirname(os.path.abspath(__file__)))


class Config:
    data_file: str = str(_PLUGIN_DIR / "XM-Turbo.json")
    api_base_url: str = "https://api.sys-allnet.com"
    bot_name: str = "XMaoBot-Turbo"
    allowed_groups: List[int] = []  # 授权群组，空列表允许所有群
    session_expire_timeout: int = 60  # 会话超时时间（秒）
