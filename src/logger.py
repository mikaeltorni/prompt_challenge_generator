import contextvars
import logging
from pathlib import Path
from typing import Any

_iteration_var: contextvars.ContextVar[int | None] = contextvars.ContextVar(
    "project_logger_iteration",
    default=None,
)
_iteration_handlers: dict[int, logging.Handler] = {}


class _IterationFilter(logging.Filter):
    def __init__(self, iteration: int):
        super().__init__()
        self.iteration = iteration

    def filter(self, record: logging.LogRecord) -> bool:
        return _iteration_var.get() == self.iteration


class _IterationBufferHandler(logging.Handler):
    def __init__(self, iteration: int):
        super().__init__()
        self.iteration = iteration
        self.messages: list[str] = []
        self.setFormatter(logging.Formatter("%(message)s"))

    def emit(self, record: logging.LogRecord) -> None:
        if _iteration_var.get() == self.iteration:
            self.messages.append(self.format(record))


def set_iteration(iteration: int | None):
    return _iteration_var.set(iteration)


def reset_iteration(token):
    if token is not None:
        _iteration_var.reset(token)


def run_with_iteration(iteration: int | None, func, *args, **kwargs):
    token = set_iteration(iteration)
    try:
        return func(*args, **kwargs)
    finally:
        reset_iteration(token)


def initialize_iteration_log(iteration: int):
    if iteration in _iteration_handlers:
        detach_iteration_log(iteration)

    buffer_handler = _IterationBufferHandler(iteration)
    logger = logging.getLogger("prompt_challenge_generator")
    logger.addHandler(buffer_handler)
    _iteration_handlers[iteration] = buffer_handler


def attach_iteration_log(iteration: int, target_dir: Path, filename: str = "iteration.log"):
    logger = logging.getLogger("prompt_challenge_generator")
    existing_handler = _iteration_handlers.get(iteration)

    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    log_path = target_dir / filename
    handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    handler.addFilter(_IterationFilter(iteration))

    logger.addHandler(handler)
    _iteration_handlers[iteration] = handler

    if isinstance(existing_handler, _IterationBufferHandler):
        for message in existing_handler.messages:
            handler.stream.write(message + "\n")
        logger.removeHandler(existing_handler)
        existing_handler.close()
    elif existing_handler:
        logger.removeHandler(existing_handler)
        existing_handler.close()

    handler.flush()


def detach_iteration_log(iteration: int):
    handler = _iteration_handlers.pop(iteration, None)
    if handler:
        logger = logging.getLogger("prompt_challenge_generator")
        logger.removeHandler(handler)
        handler.close()


class ProjectLogger:
    _configured = False

    def __init__(self, module_name: str, agent_name: str | None = None):
        self.module_name = module_name
        self.agent_name = agent_name
        self._logger = self._configure()

    @classmethod
    def _configure(cls) -> logging.Logger:
        logger = logging.getLogger("prompt_challenge_generator")
        if not cls._configured:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(message)s"))
            logger.setLevel(logging.INFO)
            logger.handlers.clear()
            logger.addHandler(handler)
            cls._configured = True
        return logger

    def with_agent(self, agent_name: str) -> "ProjectLogger":
        return ProjectLogger(self.module_name, agent_name)

    def entry(self, function_name: str, **kwargs: Any) -> None:
        args_repr = self._format_kwargs(kwargs)
        self._logger.info(
            f"{self._prefix()} entering {function_name}({args_repr})"
        )

    def exit(self, function_name: str, **kwargs: Any) -> None:
        args_repr = self._format_kwargs(kwargs)
        self._logger.info(
            f"{self._prefix()} returning {function_name} -> {args_repr}"
        )

    def _prefix(self) -> str:
        prefix = f"[main.py] [{self.module_name}]"
        iteration = _iteration_var.get()
        if iteration is not None:
            prefix += f" [Iteration {iteration}]"
        if self.agent_name:
            return f"{prefix} {self.agent_name}:"
        return prefix

    @staticmethod
    def _format_kwargs(kwargs: dict[str, Any]) -> str:
        if not kwargs:
            return ""
        items = [
            f"{key}={ProjectLogger._safe_repr(value)}"
            for key, value in kwargs.items()
        ]
        return ", ".join(items)

    @staticmethod
    def _safe_repr(value: Any) -> str:
        return repr(value)
