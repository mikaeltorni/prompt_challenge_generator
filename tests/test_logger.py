"""Iteration context and per-challenge log persistence tests."""

from src.logger import (
    ProjectLogger,
    attach_iteration_log,
    detach_iteration_log,
    initialize_iteration_log,
    reset_iteration,
    run_with_iteration,
    set_iteration,
)


def test_iteration_context_is_applied_and_restored():
    logger = ProjectLogger("test_logger.py")
    token = set_iteration(21)
    try:
        before = logger._prefix()
        during = run_with_iteration(34, logger._prefix)
        after = logger._prefix()
    finally:
        reset_iteration(token)

    assert "[Iteration 21]" in before
    assert "[Iteration 34]" in during
    assert "[Iteration 21]" in after


def test_run_with_iteration_restores_context_after_exception():
    logger = ProjectLogger("test_logger.py")
    token = set_iteration(21)
    try:
        try:
            run_with_iteration(34, lambda: (_ for _ in ()).throw(RuntimeError("expected")))
        except RuntimeError as exc:
            assert str(exc) == "expected"
        assert "[Iteration 21]" in logger._prefix()
    finally:
        reset_iteration(token)


def test_iteration_log_flushes_buffered_and_subsequent_records(tmp_path):
    iteration = 8091
    logger = ProjectLogger("test_logger.py")
    token = set_iteration(iteration)
    try:
        initialize_iteration_log(iteration)
        logger.entry("before_attach", sequence=1)
        attach_iteration_log(iteration, tmp_path)
        logger.exit("after_attach", sequence=2)
    finally:
        detach_iteration_log(iteration)
        reset_iteration(token)

    contents = (tmp_path / "iteration.log").read_text(encoding="utf-8")
    assert "before_attach" in contents
    assert "after_attach" in contents
    assert "[Iteration 8091]" in contents


def test_detaching_an_unknown_iteration_is_safe():
    detach_iteration_log(987654)
