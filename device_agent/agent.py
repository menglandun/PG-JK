# -*- coding: utf-8 -*-
"""
Google ADK + DeepSeek 设备控制智能体（最小可运行示例）
目录名 device_agent 必须与 App / 会话里的 app_name 一致。
运行（在项目根目录）：
    adk run device_agent                      # 本地交互（ADK 2.x 无 adk web）
    adk eval device_agent device_agent/eval.test.json --print_detailed_results
"""
import os
from dotenv import load_dotenv

load_dotenv()  # 从同项目根目录 .env 读取 DEEPSEEK_API_KEY 等环境变量

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# ---------------------------------------------------------------------------
# 1) 模拟的设备台账（真实项目换成数据库 / MQTT / 智能家居 API）
# ---------------------------------------------------------------------------
_devices = {
    ("Bedroom", "device_2"): {"name": "卧室台灯", "status": "ON"},
    ("Living", "device_1"): {"name": "客厅空调", "status": "ON"},
}


# ---------------------------------------------------------------------------
# 2) 给智能体注册的函数工具（普通 Python 函数即可，ADK 自动转成 FunctionTool）
#    这类工具会出现在执行轨迹里，可用 tool_trajectory_avg_score 校验。
# ---------------------------------------------------------------------------
def set_device_info(location: str, device_id: str, status: str) -> dict:
    """打开或关闭指定房间的某台设备。

    Args:
        location: 房间，如 Bedroom / Living（英文归一化）。
        device_id: 设备编号，如 device_2。
        status: 目标状态，只能是 ON 或 OFF。
    """
    key = (location, device_id)
    if key not in _devices:
        return {"ok": False, "error": f"未找到设备 {location}/{device_id}"}
    _devices[key]["status"] = status
    return {"ok": True, "location": location, "device_id": device_id,
            "device": _devices[key]["name"], "status": status}


def get_temperature(location: str) -> dict:
    """查询某个房间当前温度。"""
    # 真实项目接入温湿度传感器
    return {"location": location, "celsius": 24.5, "humidity": 48}


# ---------------------------------------------------------------------------
# 3) 用 LiteLlm 适配器把 DeepSeek（OpenAI 兼容）接到 ADK
#    LiteLLM 内置识别 deepseek/ 前缀；api_base 显式写出更稳。
# ---------------------------------------------------------------------------
_model = LiteLlm(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek/deepseek-chat"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    api_base=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
)

root_agent = LlmAgent(
    model=_model,
    name="device_agent",
    instruction=(
        "你是智能家居客服助手。流程：先判断用户意图，"
        "需要操作设备时再调用工具，参数必须从用户原话中提取并归一化"
        "（房间转英文 Bedroom/Living，状态转 ON/OFF）；"
        "回答简洁，按工具返回结果复述操作结果，不要编造设备或温度。"
    ),
    tools=[set_device_info, get_temperature],
)
