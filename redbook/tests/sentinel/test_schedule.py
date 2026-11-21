"""Tests for redbook.sentinel.schedule (pure helpers; no OS side effects)."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from redbook.sentinel import schedule  # noqa: E402


class BuildCommandTests(unittest.TestCase):
    def test_command_wraps_cmd_with_working_directory(self):
        command = schedule.build_task_command(
            Path("C:/ProgramData/miniconda3/python.exe"),
            Path("D:/recommendation-system-learning/.worktrees/sab-anc-design"))
        self.assertIn("cd /d D:\\recommendation-system-learning\\.worktrees\\sab-anc-design", command)
        self.assertIn("C:\\ProgramData\\miniconda3\\python.exe -m redbook.sentinel run-once", command)
        self.assertTrue(command.startswith("cmd.exe /c"))

    def test_register_args_are_daily_at_configured_time(self):
        args = schedule.build_register_args(
            "RedbookSentinelDaily",
            Path("C:/p/python.exe"), Path("D:/repo"), time="11:00")
        self.assertEqual(args[0], "/Create")
        self.assertIn("/SC", args) and self.assertIn("DAILY", args)
        idx = args.index("/ST")
        self.assertEqual(args[idx + 1], "11:00")
        self.assertEqual(args[args.index("/TN") + 1], "RedbookSentinelDaily")

    def test_task_name_disambiguates_worktrees(self):
        self.assertEqual(schedule.build_task_name(), "RedbookSentinelDaily")
        self.assertEqual(schedule.build_task_name("sab"), "RedbookSentinelDaily(sab)")

    def test_run_once_entry_point_is_idempotent_mode(self):
        command = schedule.build_task_command(Path("C:/p/python.exe"), Path("D:/repo"))
        self.assertIn("run-once", command)  # never run-forever: no resident service
        self.assertNotIn("run-forever", command)


if __name__ == "__main__":
    unittest.main()
