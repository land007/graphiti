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

from collections.abc import Callable
from typing import Any, Protocol

from pydantic import BaseModel


class Message(BaseModel):
    """
    提示词消息的基础模型
    
    用途: 表示 LLM 提示词中的一条消息
    字段:
        role: 消息角色（'system' 或 'user'）
        content: 消息内容
    """
    role: str
    content: str


class PromptVersion(Protocol):
    """
    提示词版本的协议定义
    
    用途: 定义提示词函数的标准接口
    签名: (context: dict[str, Any]) -> list[Message]
    """
    def __call__(self, context: dict[str, Any]) -> list[Message]: ...


# 提示词函数的类型别名
# 用途: 表示一个接受上下文字典并返回消息列表的函数
PromptFunction = Callable[[dict[str, Any]], list[Message]]
