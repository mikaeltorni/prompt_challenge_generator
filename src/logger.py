import logging
from typing import Any


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
