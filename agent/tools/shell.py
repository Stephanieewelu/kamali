from agent.core.executor import ToolExecutor, ToolPermission


def build_shell_executor(permission: ToolPermission = ToolPermission.READ_ONLY) -> ToolExecutor:
    return ToolExecutor(permission)
