# 中文提示词实现方案

## 概述

本文档描述如何为 Graphiti 添加中文提示词支持。

## 当前状态

- 所有提示词目前都是英文
- 系统已支持多语言输出（通过 `get_extraction_language_instruction`）
- 提示词通过 `prompt_library` 统一管理

## 实现方案

### 方案 1: 语言配置参数（推荐）

**优点**:
- 向后兼容
- 用户可以选择语言
- 不影响现有功能

**实现步骤**:

1. **在 Graphiti 初始化时添加语言参数**

```python
# graphiti_core/graphiti.py
class Graphiti:
    def __init__(
        self,
        ...,
        prompt_language: str = 'en',  # 新增参数
    ):
        self.prompt_language = prompt_language
```

2. **创建中文提示词文件**

在 `graphiti_core/prompts/` 目录下创建：
- `extract_nodes_zh.py`
- `extract_edges_zh.py`
- `dedupe_nodes_zh.py`
- `dedupe_edges_zh.py`
- `dedupe_edges_zh.py`
- `summarize_nodes_zh.py`
- `extract_edge_dates_zh.py`
- `invalidate_edges_zh.py`
- `eval_zh.py`

3. **修改 lib.py 支持语言选择**

```python
# graphiti_core/prompts/lib.py
def create_prompt_library(language: str = 'en') -> PromptLibrary:
    if language == 'zh':
        from .extract_nodes_zh import versions as extract_nodes_versions_zh
        from .extract_edges_zh import versions as extract_edges_versions_zh
        # ... 导入其他中文版本
        PROMPT_LIBRARY_IMPL = {
            'extract_nodes': extract_nodes_versions_zh,
            'extract_edges': extract_edges_versions_zh,
            # ...
        }
    else:
        # 使用默认英文版本
        PROMPT_LIBRARY_IMPL = {
            'extract_nodes': extract_nodes_versions,
            'extract_edges': extract_edges_versions,
            # ...
        }
    return PromptLibraryWrapper(PROMPT_LIBRARY_IMPL)
```

### 方案 2: 环境变量配置

通过环境变量控制提示词语言：

```bash
export GRAPHITI_PROMPT_LANGUAGE=zh
```

### 方案 3: 配置文件

在配置文件中添加语言设置：

```yaml
# config.yaml
prompts:
  language: zh  # 或 en
```

## 实施建议

### 阶段 1: 讨论和设计（当前阶段）

1. ✅ 创建 GitHub Issue 描述功能需求
2. ✅ 讨论实现方案
3. ✅ 获得维护者批准

### 阶段 2: 实现核心功能

1. 创建中文提示词文件（参考 `extract_nodes_zh.py.example`）
2. 实现语言选择机制
3. 添加单元测试

### 阶段 3: 测试和验证

1. 编写集成测试
2. 验证中文提示词效果
3. 性能测试

### 阶段 4: 文档和发布

1. 更新文档
2. 添加使用示例
3. 提交 PR

## 注意事项

### 1. 提示词翻译质量

- 确保中文提示词准确传达原意
- 保持技术术语的一致性
- 考虑中文 LLM 模型的特点

### 2. 测试覆盖

- 为中文提示词添加测试
- 确保输出格式一致
- 验证多语言场景

### 3. 向后兼容

- 默认使用英文（保持现有行为）
- 不影响现有用户
- 提供清晰的迁移指南

### 4. 维护成本

- 两套提示词需要同步维护
- 考虑自动化测试确保一致性

## 贡献步骤

### 1. Fork 和设置

```bash
# Fork 仓库
git clone https://github.com/YOUR_USERNAME/graphiti.git
cd graphiti

# 创建功能分支
git checkout -b feature/chinese-prompts

# 安装依赖
make install
```

### 2. 创建中文提示词

参考 `extract_nodes_zh.py.example`，创建所有提示词的中文版本。

### 3. 实现语言选择

修改 `lib.py` 和相关文件，添加语言选择逻辑。

### 4. 添加测试

```bash
# 创建测试文件
tests/prompts/test_chinese_prompts.py

# 运行测试
make test
```

### 5. 提交 PR

```bash
# 格式化代码
make format

# 运行检查
make check

# 提交
git commit -m "feat: 添加中文提示词支持"
git push origin feature/chinese-prompts
```

## 示例：中文提示词格式

```python
def extract_message(context: dict[str, Any]) -> list[Message]:
    """
    从对话消息中提取实体节点（中文版）
    """
    sys_prompt = """你是一个 AI 助手，负责从对话消息中提取实体节点。
    你的主要任务是从对话中提取并分类说话者和其他重要的实体。"""

    user_prompt = f"""
<实体类型>
{context['entity_types']}
</实体类型>

<历史消息>
{to_prompt_json([ep for ep in context['previous_episodes']])}
</历史消息>

<当前消息>
{context['episode_content']}
</当前消息>

指令：

你被提供了一个对话上下文和一条当前消息。你的任务是从当前消息中提取**显式或隐式**提到的**实体节点**。
...
"""
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]
```

## 下一步

1. **创建 GitHub Issue**: 描述你的实现方案
2. **等待反馈**: 与维护者讨论最佳方案
3. **开始实现**: 获得批准后开始编码
4. **提交 PR**: 完成实现后提交 Pull Request

## 相关资源

- [贡献指南](../CONTRIBUTING.md)
- [中文贡献指南](./CONTRIBUTING_CN.md)
- [提示词索引](./PROMPTS_INDEX.md)
- [Discord 社区](https://discord.com/invite/W8Kw6bsgXQ)

