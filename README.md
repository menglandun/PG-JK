# Google ADK + DeepSeek 智能体评估监控最小项目

用 Google ADK 框架接 DeepSeek（OpenAI 兼容），并落地第 19 章讲的
**测试文件（单元测试）+ test_config 阈值 + pytest/CI** 评估闭环。

## 目录结构

```
adk-deepseek-eval/
├── .env.example              # 环境变量模板（复制为 .env）
├── requirements.txt
└── device_agent/             # 目录名 = app_name，必须一致
    ├── agent.py              # LlmAgent + 工具 + LiteLlm(DeepSeek)
    ├── eval.test.json        # 单元测试文件：预期工具轨迹 + 标准答案
    ├── test_config.json      # 指标与通过阈值
    └── test_agent_eval.py    # pytest/CI 桥接，调用 AgentEvaluator
```

## 一、安装与配置

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # 填入 DEEPSEEK_API_KEY
```

## 二、本地交互调试（ADK 2.x 已无 adk web）

```bash
# 终端交互式对话
adk run device_agent
# 单轮直接提问：adk run device_agent "关闭卧室中的设备2"
# 起 API 服务供 ADK Studio 前端连接：adk api_server device_agent --port 8000
```

## 三、跑评估（CLI）

```bash
# test_config.json 放在测试文件同目录会被自动识别，--config_file_path 可省略
adk eval device_agent device_agent/eval.test.json \
  --config_file_path=device_agent/test_config.json \
  --print_detailed_results
```

输出 `tool_trajectory_avg_score`（轨迹是否按序调对工具）与
`response_match_score`（答复是否达标）。本项目阈值分别为 `1.0` 和 `0.3`，
低于阈值判 FAIL。

## 四、pytest 接入 CI/CD

```bash
# 直接跑测试文件（AgentEvaluator 自动加载同目录 test_config.json）
pytest device_agent/test_agent_eval.py -v
# 或用 ADK 内置命令扫描目录里的 *.test.json
adk test device_agent
```

## 五、指标速查

| 指标 | 评什么 | 适用 |
|---|---|---|
| `tool_trajectory_avg_score` | 是否按顺序调对工具、参数是否正确 | 自定义函数工具（本项目） |
| `response_match_score` | ROUGE 词重叠，确定性快但怕换说法 | 简单标准答案 |
| `final_response_match_v2` | LLM 语义判断答复是否一致 | 措辞自由的答复 |
| `hallucinations_v1` | 答复是否有工具输出支撑，防编造 | 接地类智能体 |
| `rubric_based_final_response_quality_v1` | 自定义规则评分（礼貌/安全/确认） | 主观质量 |

## 说明

- DeepSeek 通过 LiteLLM 的 `deepseek/` 前缀接入，`api_base` 指向
  `https://api.deepseek.com`；换模型只改 `.env` 的 `DEEPSEEK_MODEL`。
- 自定义 Python 函数会进入轨迹，可用轨迹匹配；模型内置检索类工具
  不进轨迹，需改用 rubric 语义评分。
