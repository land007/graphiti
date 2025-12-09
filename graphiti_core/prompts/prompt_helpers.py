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

import json
from typing import Any

# 系统提示词中的指令，要求不转义 Unicode 字符
# 用途: 自动添加到所有系统提示词，确保多语言支持
DO_NOT_ESCAPE_UNICODE = '\nDo not escape unicode characters.\n'


def to_prompt_json(data: Any, ensure_ascii: bool = False, indent: int | None = None) -> str:
    """
    将数据序列化为 JSON 格式用于提示词
    
    用途: 将 Python 对象转换为 JSON 字符串，用于构建提示词内容
    参数:
        data: 要序列化的数据（可以是字典、列表等）
        ensure_ascii: 如果为 True，转义非 ASCII 字符；如果为 False（默认），保留原始字符
        indent: 缩进空格数，默认为 None（压缩格式）
    返回:
        JSON 字符串表示
    注意:
        默认情况下（ensure_ascii=False），非 ASCII 字符（如韩语、日语、中文）
        会以原始形式保留在提示词中，使其在 LLM 日志中可读，并提高模型理解能力
    """
    return json.dumps(data, ensure_ascii=ensure_ascii, indent=indent)
