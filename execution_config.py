"""
MAiKO Execution Configuration
Sandbox and execution parameters for code execution
"""
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
import os
from config import config


class ExecutionEnvironment(Enum):
    """Execution environment types"""
    LOCAL = "local"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    SERVERLESS = "serverless"


@dataclass
class SandboxConfig:
    """Sandbox configuration parameters"""
    # Resource limits
    timeout_ms: int = 5000
    max_memory_mb: int = 512
    max_cpu_percent: int = 100
    max_output_size: int = 10 * 1024 * 1024  # 10MB

    # Code restrictions
    blocked_patterns: List[str] = None
    allowed_imports: List[str] = None
    max_code_size: int = 10 * 1024  # 10KB

    # Environment
    environment: ExecutionEnvironment = ExecutionEnvironment.LOCAL
    environment_vars: dict = None
    read_only_filesystem: bool = True

    def __post_init__(self):
        if self.blocked_patterns is None:
            self.blocked_patterns = [
                r"rm\s+-rf",
                r"sudo",
                r"eval",
                r"exec\s*\(",
                r"__import__",
                r"subprocess",
            ]

        if self.allowed_imports is None:
            self.allowed_imports = [
                "json", "math", "datetime", "random",
                "re", "itertools", "collections"
            ]

        if self.environment_vars is None:
            self.environment_vars = {}

    def to_dict(self):
        """Convert config to dictionary"""
        return {
            "timeout_ms": self.timeout_ms,
            "max_memory_mb": self.max_memory_mb,
            "max_cpu_percent": self.max_cpu_percent,
            "max_output_size": self.max_output_size,
            "blocked_patterns": self.blocked_patterns,
            "allowed_imports": self.allowed_imports,
            "max_code_size": self.max_code_size,
            "environment": self.environment.value,
            "read_only_filesystem": self.read_only_filesystem,
        }

    @classmethod
    def from_env(cls) -> "SandboxConfig":
        """Create config from environment variables"""
        return cls(
            timeout_ms=int(os.getenv("EXECUTION_TIMEOUT", "5000")),
            max_memory_mb=int(os.getenv("MAX_MEMORY_MB", "512")),
            max_cpu_percent=int(os.getenv("MAX_CPU_PERCENT", "100")),
            max_output_size=int(os.getenv("MAX_OUTPUT_SIZE", str(10 * 1024 * 1024))),
            max_code_size=int(os.getenv("MAX_CODE_SIZE", "10240")),
            environment=ExecutionEnvironment(os.getenv("EXECUTION_ENV", "local")),
            read_only_filesystem=os.getenv("READ_ONLY_FS", "true").lower() == "true",
        )


@dataclass
class ExecutionPolicy:
    """Policy for code execution control"""
    # Rate limiting
    max_executions_per_minute: int = 60
    max_executions_per_hour: int = 1000

    # Resource quotas
    daily_execution_quota_mb: int = 1000  # 1GB total execution
    monthly_execution_quota_mb: int = 10000  # 10GB total execution

    # Execution logging
    log_all_executions: bool = True
    log_failed_only: bool = False
    log_execution_time: bool = True
    log_memory_usage: bool = True

    # Security
    require_approval_for: List[str] = None
    enable_audit_trail: bool = True
    track_user_attribution: bool = True

    def __post_init__(self):
        if self.require_approval_for is None:
            self.require_approval_for = [
                "system_calls",
                "file_operations",
                "network_requests"
            ]

    def to_dict(self):
        """Convert policy to dictionary"""
        return {
            "max_executions_per_minute": self.max_executions_per_minute,
            "max_executions_per_hour": self.max_executions_per_hour,
            "daily_quota_mb": self.daily_execution_quota_mb,
            "monthly_quota_mb": self.monthly_execution_quota_mb,
            "log_all_executions": self.log_all_executions,
            "log_failed_only": self.log_failed_only,
            "log_execution_time": self.log_execution_time,
            "log_memory_usage": self.log_memory_usage,
            "require_approval_for": self.require_approval_for,
            "enable_audit_trail": self.enable_audit_trail,
        }

    @classmethod
    def from_env(cls) -> "ExecutionPolicy":
        """Create policy from environment variables"""
        return cls(
            max_executions_per_minute=int(os.getenv("MAX_EXEC_PER_MIN", "60")),
            max_executions_per_hour=int(os.getenv("MAX_EXEC_PER_HOUR", "1000")),
            daily_execution_quota_mb=int(os.getenv("DAILY_QUOTA_MB", "1000")),
            monthly_execution_quota_mb=int(os.getenv("MONTHLY_QUOTA_MB", "10000")),
            log_all_executions=os.getenv("LOG_ALL_EXEC", "true").lower() == "true",
            log_failed_only=os.getenv("LOG_FAILED_ONLY", "false").lower() == "true",
            enable_audit_trail=os.getenv("AUDIT_TRAIL", "true").lower() == "true",
        )


# Default sandbox and policy configurations
DEFAULT_SANDBOX = SandboxConfig.from_env()
DEFAULT_POLICY = ExecutionPolicy.from_env()
