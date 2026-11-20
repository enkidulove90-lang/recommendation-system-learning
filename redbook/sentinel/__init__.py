"""Sentinel: dependency probe sweep + 11:00 paper retrieval + delivery pool.

Low-ops contract: no resident service. ``python -m redbook.cli sentinel run-once``
is invoked by Windows Task Scheduler; the same command is idempotent per day
for retrieval and rate-limited for probes, so over-triggering is harmless.
"""
