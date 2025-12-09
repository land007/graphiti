"""
Copyright 2024, Zep Software, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import Any, Protocol, TypedDict

from .dedupe_edges import Prompt as DedupeEdgesPrompt
from .dedupe_edges import Versions as DedupeEdgesVersions
from .dedupe_edges import versions as dedupe_edges_versions
from .dedupe_nodes import Prompt as DedupeNodesPrompt
from .dedupe_nodes import Versions as DedupeNodesVersions
from .dedupe_nodes import versions as dedupe_nodes_versions
from .eval import Prompt as EvalPrompt
from .eval import Versions as EvalVersions
from .eval import versions as eval_versions
from .extract_edge_dates import Prompt as ExtractEdgeDatesPrompt
from .extract_edge_dates import Versions as ExtractEdgeDatesVersions
from .extract_edge_dates import versions as extract_edge_dates_versions
from .extract_edges import Prompt as ExtractEdgesPrompt
from .extract_edges import Versions as ExtractEdgesVersions
from .extract_edges import versions as extract_edges_versions
from .extract_nodes import Prompt as ExtractNodesPrompt
from .extract_nodes import Versions as ExtractNodesVersions
from .extract_nodes import versions as extract_nodes_versions
from .invalidate_edges import Prompt as InvalidateEdgesPrompt
from .invalidate_edges import Versions as InvalidateEdgesVersions
from .invalidate_edges import versions as invalidate_edges_versions
from .models import Message, PromptFunction
from .prompt_helpers import DO_NOT_ESCAPE_UNICODE
from .summarize_nodes import Prompt as SummarizeNodesPrompt
from .summarize_nodes import Versions as SummarizeNodesVersions
from .summarize_nodes import versions as summarize_nodes_versions


class PromptLibrary(Protocol):
    """
    提示词库的协议定义
    
    用途: 定义提示词库的标准接口，包含所有提示词类型
    包含的提示词类型:
        extract_nodes: 节点提取提示词
        dedupe_nodes: 节点去重提示词
        extract_edges: 边提取提示词
        dedupe_edges: 边去重提示词
        invalidate_edges: 边失效提示词
        extract_edge_dates: 边日期提取提示词
        summarize_nodes: 节点摘要提示词
        eval: 评估相关提示词
    """
    extract_nodes: ExtractNodesPrompt
    dedupe_nodes: DedupeNodesPrompt
    extract_edges: ExtractEdgesPrompt
    dedupe_edges: DedupeEdgesPrompt
    invalidate_edges: InvalidateEdgesPrompt
    extract_edge_dates: ExtractEdgeDatesPrompt
    summarize_nodes: SummarizeNodesPrompt
    eval: EvalPrompt


class PromptLibraryImpl(TypedDict):
    extract_nodes: ExtractNodesVersions
    dedupe_nodes: DedupeNodesVersions
    extract_edges: ExtractEdgesVersions
    dedupe_edges: DedupeEdgesVersions
    invalidate_edges: InvalidateEdgesVersions
    extract_edge_dates: ExtractEdgeDatesVersions
    summarize_nodes: SummarizeNodesVersions
    eval: EvalVersions


class VersionWrapper:
    """
    提示词版本包装器
    
    用途: 包装提示词函数，自动为系统提示词添加 Unicode 不转义指令
    """
    def __init__(self, func: PromptFunction):
        self.func = func

    def __call__(self, context: dict[str, Any]) -> list[Message]:
        messages = self.func(context)
        # 为系统提示词添加 Unicode 不转义指令
        for message in messages:
            message.content += DO_NOT_ESCAPE_UNICODE if message.role == 'system' else ''
        return messages


class PromptTypeWrapper:
    """
    提示词类型包装器
    
    用途: 包装同一类型的多个版本提示词（如 v1, v2）
    """
    def __init__(self, versions: dict[str, PromptFunction]):
        for version, func in versions.items():
            setattr(self, version, VersionWrapper(func))


class PromptLibraryWrapper:
    """
    提示词库包装器
    
    用途: 统一管理所有提示词类型，提供统一的访问接口
    使用方式:
        prompt_library.extract_nodes.extract_message(context)
        prompt_library.dedupe_nodes.node(context)
    """
    def __init__(self, library: PromptLibraryImpl):
        for prompt_type, versions in library.items():
            setattr(self, prompt_type, PromptTypeWrapper(versions))  # type: ignore[arg-type]


# 提示词库实现
# 用途: 将所有提示词类型和版本组织在一起
PROMPT_LIBRARY_IMPL: PromptLibraryImpl = {
    'extract_nodes': extract_nodes_versions,      # 节点提取提示词
    'dedupe_nodes': dedupe_nodes_versions,        # 节点去重提示词
    'extract_edges': extract_edges_versions,      # 边提取提示词
    'dedupe_edges': dedupe_edges_versions,        # 边去重提示词
    'invalidate_edges': invalidate_edges_versions,  # 边失效提示词
    'extract_edge_dates': extract_edge_dates_versions,  # 边日期提取提示词
    'summarize_nodes': summarize_nodes_versions,   # 节点摘要提示词
    'eval': eval_versions,                        # 评估相关提示词
}

# 提示词库统一入口
# 用途: 通过此对象访问所有提示词函数
# 示例: prompt_library.extract_nodes.extract_message(context)
prompt_library: PromptLibrary = PromptLibraryWrapper(PROMPT_LIBRARY_IMPL)  # type: ignore[assignment]
