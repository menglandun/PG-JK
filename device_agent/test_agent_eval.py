# -*- coding: utf-8 -*-
import os, sys, asyncio, importlib
from google.adk.evaluation.agent_evaluator import AgentEvaluator

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
MODULE = "device_agent.agent"

def test_agent_eval():
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    importlib.import_module(MODULE)
    eval_file = os.path.join(HERE, "eval.test.json")
    asyncio.run(AgentEvaluator.evaluate(
        agent_module=MODULE,
        eval_dataset_file_path_or_dir=eval_file,
        num_runs=1,
        print_detailed_results=True,
    ))
