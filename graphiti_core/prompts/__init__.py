"""
Graphiti 提示词模块

本模块包含所有用于知识图谱构建的 LLM 提示词。

主要导出:
    prompt_library: 提示词库统一入口，包含所有提示词类型
    Message: 提示词消息的基础模型

使用示例:
    from graphiti_core.prompts import prompt_library, Message
    
    # 使用节点提取提示词
    messages = prompt_library.extract_nodes.extract_message(context)
    
    # 使用边提取提示词
    messages = prompt_library.extract_edges.edge(context)
"""

from .lib import prompt_library
from .models import Message

__all__ = ['prompt_library', 'Message']
