"""content_events 单元测试包。

允许 `python -m unittest content_events.tests -v` 直接加载并运行全部用例。
unittest 默认 loader 不会递归 __init__ 导入的子模块，这里用 load_tests 协议显式聚合。
"""
import unittest

from . import (
    test_content_events,
    test_publishers,
    test_orchestrator,
    test_cli,
    test_feedback_opt,
    test_idempotency,
    test_event_log,
    test_serve,
)


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    for mod in (
        test_content_events,
        test_publishers,
        test_orchestrator,
        test_cli,
        test_feedback_opt,
        test_idempotency,
        test_event_log,
        test_serve,
    ):
        suite.addTests(loader.loadTestsFromModule(mod))
    return suite
