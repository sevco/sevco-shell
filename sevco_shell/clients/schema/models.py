from dataclasses import dataclass
from typing import Any, Dict, List

from sevco_shell.clients.models import with_dict


@dataclass
class SourceSchemaRunnerRequirements(with_dict):
    required: bool
    configurable: bool


@dataclass
class SourceSchemaInfo(with_dict):
    description: str
    runner_requirements: SourceSchemaRunnerRequirements


@dataclass
class SourceSchemas(with_dict):
    info: SourceSchemaInfo
    connect: Dict[str, Any]
    auth: Dict[str, Any]
    settings: Dict[str, Any]


@dataclass
class SourceSchemaByName(with_dict):
    info: SourceSchemaInfo
    connect: str
    auth: str
    settings: str


@dataclass
class SourceSchemaByNameArray(with_dict):
    types: List[SourceSchemaByName]
