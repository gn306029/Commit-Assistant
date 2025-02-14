import os
import shutil
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from commit_assistant.enums.config_key import ConfigKey
from commit_assistant.utils.console_utils import console


def _load_config_from_config_file(config: dict[str, Any], repo_root: str) -> None:
    """
    從專案配置文件載入配置

    Args:
        config (dict[str, Any]): 設定
        repo_root (str): 專案根目錄路徑
    """
    repo_root_path = Path(repo_root)
    config_file = repo_root_path / ".commit-assistant-config"

    if not config_file.exists():
        return

    with open(config_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # '#' 開頭的行為註解，忽略
            # 其餘的設定進行寫入
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()


def load_config(repo_root: str = ".") -> None:
    """
    載入配置文件

    優先順序:
    1. 專案配置文件 (.commit-assistant-config)
    2. 環境變數 (.env)
    3. 默認值

    Args:
        repo_root (str, optional): 專案根目錄路徑. Defaults to ".".
    """
    # 定義默認配置
    config: dict[str, Any] = {
        ConfigKey.ENABLE_COMMIT_ASSISTANT.value: True,
        ConfigKey.USE_MODEL.value: "gemini-2.0-flash-exp",
        ConfigKey.GEMINI_API_KEY.value: None,
        ConfigKey.COMMIT_STYLE.value: "custom",
    }

    # 從 .env 載入，覆蓋默認配置
    package_path = Path(__file__).parent.parent
    dotenv_path = package_path / ".env"
    load_dotenv(dotenv_path)
    for key in config:
        env_value = os.getenv(key)
        if env_value is not None:
            config[key] = env_value

    # 從專案配置文件載入
    try:
        _load_config_from_config_file(config, repo_root)
    except Exception as e:
        console.print(f"[yellow]載入commit-assistant config 失敗: {e}[/yellow]")

    # 將 config 設定進環境變數
    for key, value in config.items():
        if value is not None:
            os.environ[key] = str(value)


def install_config(repo_root: str) -> None:
    """
    安裝配置文件到專案根目錄
    """
    config_file = Path(repo_root) / ".commit-assistant-config"

    if config_file.exists():
        return

    try:
        # 複製默認的配置文件到專案根目錄
        package_dir = Path(__file__).parent.parent
        default_config_file = package_dir / "resources" / "config" / ".commit-assistant-config"

        shutil.copy(default_config_file, config_file)
    except Exception as e:
        console.print(f"[red]安裝配置文件失敗: {e}[/red]")
        return
