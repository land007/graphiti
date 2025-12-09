# Graphiti 提示词索引

本文档列出了 Graphiti 项目中所有提示词（Prompts）的位置和用途。

## 提示词目录结构

所有提示词位于 `graphiti_core/prompts/` 目录下：

```
graphiti_core/prompts/
├── __init__.py              # 导出 prompt_library 和 Message
├── models.py                # 提示词基础模型定义
├── lib.py                   # 提示词库统一管理
├── prompt_helpers.py        # 提示词辅助函数
├── snippets.py              # 共享的提示词片段
├── extract_nodes.py         # 节点提取提示词
├── extract_edges.py         # 边/关系提取提示词
├── dedupe_nodes.py          # 节点去重提示词
├── dedupe_edges.py          # 边去重提示词
├── summarize_nodes.py       # 节点摘要提示词
├── extract_edge_dates.py    # 边日期提取提示词
├── invalidate_edges.py      # 边失效提示词
└── eval.py                  # 评估相关提示词
```

## 提示词分类清单

### 1. 节点提取 (extract_nodes.py)

**文件路径**: `graphiti_core/prompts/extract_nodes.py`

#### 1.1 extract_message
- **用途**: 从对话消息中提取实体节点
- **输入**: 对话消息、实体类型、历史消息
- **输出**: 提取的实体列表
- **使用场景**: 处理对话格式的输入

#### 1.2 extract_json
- **用途**: 从 JSON 数据中提取实体节点
- **输入**: JSON 数据、实体类型、源描述
- **输出**: 提取的实体列表
- **使用场景**: 处理结构化 JSON 数据

#### 1.3 extract_text
- **用途**: 从纯文本中提取实体节点
- **输入**: 文本内容、实体类型
- **输出**: 提取的实体列表
- **使用场景**: 处理普通文本输入

#### 1.4 reflexion
- **用途**: 检查是否有遗漏的实体未提取
- **输入**: 历史消息、当前消息、已提取实体
- **输出**: 遗漏的实体列表
- **使用场景**: 实体提取质量检查

#### 1.5 classify_nodes
- **用途**: 对提取的实体进行分类
- **输入**: 消息、提取的实体、实体类型定义
- **输出**: 分类后的实体
- **使用场景**: 实体类型分类

#### 1.6 extract_attributes
- **用途**: 从消息中提取实体属性
- **输入**: 消息、实体信息
- **输出**: 实体属性值
- **使用场景**: 实体属性填充

#### 1.7 extract_summary
- **用途**: 生成实体摘要
- **输入**: 消息、实体信息
- **输出**: 实体摘要（< 250 字符）
- **使用场景**: 实体摘要生成

---

### 2. 边/关系提取 (extract_edges.py)

**文件路径**: `graphiti_core/prompts/extract_edges.py`

#### 2.1 edge
- **用途**: 从消息中提取实体间的关系（边）
- **输入**: 消息、实体列表、关系类型、参考时间
- **输出**: 提取的关系列表（包含 valid_at, invalid_at）
- **使用场景**: 关系提取，支持时间信息

#### 2.2 reflexion
- **用途**: 检查是否有遗漏的关系未提取
- **输入**: 历史消息、当前消息、已提取实体、已提取关系
- **输出**: 遗漏的关系列表
- **使用场景**: 关系提取质量检查

#### 2.3 extract_attributes
- **用途**: 从消息中提取关系的属性
- **输入**: 消息、关系信息、参考时间
- **输出**: 关系属性值
- **使用场景**: 关系属性填充

---

### 3. 节点去重 (dedupe_nodes.py)

**文件路径**: `graphiti_core/prompts/dedupe_nodes.py`

#### 3.1 node
- **用途**: 判断单个新实体是否为现有实体的重复
- **输入**: 新实体、现有实体列表、消息上下文
- **输出**: 重复判断结果（duplicate_idx, duplicates）
- **使用场景**: 单个实体去重

#### 3.2 nodes
- **用途**: 批量判断多个实体是否为现有实体的重复
- **输入**: 新实体列表、现有实体列表、消息上下文
- **输出**: 每个实体的重复判断结果
- **使用场景**: 批量实体去重

#### 3.3 node_list
- **用途**: 对实体列表进行去重和合并
- **输入**: 实体列表
- **输出**: 去重后的实体分组和合并摘要
- **使用场景**: 实体列表去重

---

### 4. 边去重 (dedupe_edges.py)

**文件路径**: `graphiti_core/prompts/dedupe_edges.py`

#### 4.1 edge
- **用途**: 判断新边是否为现有边的重复
- **输入**: 新边、现有边列表
- **输出**: 重复判断结果
- **使用场景**: 单个边去重

#### 4.2 edge_list
- **用途**: 对边列表进行去重
- **输入**: 边列表
- **输出**: 去重后的边列表
- **使用场景**: 边列表去重

#### 4.3 resolve_edge
- **用途**: 判断边的重复和矛盾关系
- **输入**: 新边、现有边、边失效候选、边类型
- **输出**: 重复边列表、矛盾边列表、边类型
- **使用场景**: 边去重和矛盾检测

---

### 5. 节点摘要 (summarize_nodes.py)

**文件路径**: `graphiti_core/prompts/summarize_nodes.py`

#### 5.1 summarize_pair
- **用途**: 合并两个摘要为一个
- **输入**: 两个节点摘要
- **输出**: 合并后的摘要（< 250 字符）
- **使用场景**: 摘要合并

#### 5.2 summarize_context
- **用途**: 从消息上下文中生成实体摘要和属性
- **输入**: 消息、实体名称、实体上下文、属性定义
- **输出**: 实体摘要和属性值
- **使用场景**: 实体摘要生成和属性提取

#### 5.3 summary_description
- **用途**: 生成摘要的描述
- **输入**: 摘要内容
- **输出**: 摘要的单句描述
- **使用场景**: 摘要描述生成

---

### 6. 边日期提取 (extract_edge_dates.py)

**文件路径**: `graphiti_core/prompts/extract_edge_dates.py`

#### 6.1 v1
- **用途**: 从消息中提取关系的时间信息
- **输入**: 消息、关系事实、参考时间戳
- **输出**: valid_at 和 invalid_at 时间
- **使用场景**: 关系时间信息提取

---

### 7. 边失效 (invalidate_edges.py)

**文件路径**: `graphiti_core/prompts/invalidate_edges.py`

#### 7.1 v1
- **用途**: 基于新边判断哪些现有边应该失效
- **输入**: 历史消息、当前消息、现有边、新边
- **输出**: 应该失效的边 ID 列表
- **使用场景**: 关系失效检测（基于时间戳）

#### 7.2 v2
- **用途**: 基于新事实判断哪些现有事实被矛盾
- **输入**: 现有事实、新事实
- **输出**: 被矛盾的现有事实 ID 列表
- **使用场景**: 关系失效检测（基于矛盾）

---

### 8. 评估 (eval.py)

**文件路径**: `graphiti_core/prompts/eval.py`

#### 8.1 query_expansion
- **用途**: 将问题重写为更适合数据库检索的查询
- **输入**: 原始问题
- **输出**: 优化后的查询
- **使用场景**: 查询优化

#### 8.2 qa_prompt
- **用途**: 基于实体摘要和事实回答问题
- **输入**: 问题、实体摘要、事实
- **输出**: 答案
- **使用场景**: 问答生成

#### 8.3 eval_prompt
- **用途**: 评估答案是否正确
- **输入**: 问题、标准答案、响应
- **输出**: 正确性判断和推理
- **使用场景**: 答案质量评估

#### 8.4 eval_add_episode_results
- **用途**: 评估基线提取和候选提取的质量
- **输入**: 消息、基线提取结果、候选提取结果
- **输出**: 质量比较结果
- **使用场景**: 提取质量评估

---

## 共享组件

### snippets.py

**文件路径**: `graphiti_core/prompts/snippets.py`

#### summary_instructions
- **用途**: 摘要生成的通用指导原则
- **内容**: 
  - 只输出事实内容
  - 保持简洁（< 250 字符）
  - 直接陈述事实，不解释过程
- **使用场景**: 被多个摘要相关提示词引用

### prompt_helpers.py

**文件路径**: `graphiti_core/prompts/prompt_helpers.py`

#### to_prompt_json()
- **用途**: 将数据序列化为 JSON 格式用于提示词
- **参数**: 
  - `data`: 要序列化的数据
  - `ensure_ascii`: 是否转义非 ASCII 字符（默认 False）
  - `indent`: 缩进空格数（默认 None）
- **使用场景**: 所有提示词中格式化数据

#### DO_NOT_ESCAPE_UNICODE
- **用途**: 系统提示词中的指令，要求不转义 Unicode 字符
- **使用场景**: 自动添加到所有系统提示词

### models.py

**文件路径**: `graphiti_core/prompts/models.py`

#### Message
- **用途**: 提示词消息的基础模型
- **字段**:
  - `role`: 消息角色（system/user）
  - `content`: 消息内容

#### PromptVersion
- **用途**: 提示词版本的协议定义
- **签名**: `(context: dict[str, Any]) -> list[Message]`

### lib.py

**文件路径**: `graphiti_core/prompts/lib.py`

#### prompt_library
- **用途**: 统一的提示词库入口
- **结构**: 
  ```python
  prompt_library.extract_nodes.extract_message(context)
  prompt_library.dedupe_nodes.node(context)
  prompt_library.extract_edges.edge(context)
  # ... 等等
  ```

---

## 其他相关提示词

### llm_client/client.py

**文件路径**: `graphiti_core/llm_client/client.py`

#### get_extraction_language_instruction()
- **用途**: 返回多语言提取的指令
- **内容**: 要求提取的信息使用与输入相同的语言
- **使用场景**: 自动添加到提取相关的系统提示词

---

## 提示词使用流程

1. **节点提取流程**:
   - `extract_message/extract_json/extract_text` → 提取实体
   - `reflexion` → 检查遗漏
   - `classify_nodes` → 分类实体
   - `extract_attributes` → 提取属性
   - `extract_summary` → 生成摘要

2. **关系提取流程**:
   - `edge` → 提取关系
   - `reflexion` → 检查遗漏
   - `extract_edge_dates` → 提取时间信息
   - `extract_attributes` → 提取属性

3. **去重流程**:
   - `dedupe_nodes.node/nodes/node_list` → 节点去重
   - `dedupe_edges.edge/edge_list/resolve_edge` → 边去重

4. **失效检测流程**:
   - `invalidate_edges.v1/v2` → 检测失效的边

5. **摘要合并流程**:
   - `summarize_nodes.summarize_pair` → 合并摘要
   - `summarize_nodes.summarize_context` → 从上下文生成摘要

---

## 提示词版本管理

所有提示词都支持版本管理，通过 `lib.py` 中的 `PromptLibraryWrapper` 统一管理。

每个提示词类型可以有多个版本（如 `v1`, `v2`），通过以下方式访问：

```python
from graphiti_core.prompts import prompt_library

# 使用默认版本
messages = prompt_library.extract_nodes.extract_message(context)

# 使用特定版本（如果存在）
messages = prompt_library.extract_nodes.extract_message(context)  # 当前只有默认版本
```

---

## 自定义提示词

可以通过 `custom_prompt` 参数在以下提示词中添加自定义指令：

- `extract_nodes.extract_message`
- `extract_nodes.extract_json`
- `extract_nodes.extract_text`
- `extract_edges.edge`

这些自定义提示词会被追加到标准提示词的末尾。

---

## 总结

Graphiti 的提示词系统分为 8 个主要类别，共包含 **30+ 个提示词函数**，覆盖了知识图谱构建的完整流程：

1. **节点提取** (7 个提示词)
2. **关系提取** (3 个提示词)
3. **节点去重** (3 个提示词)
4. **边去重** (3 个提示词)
5. **节点摘要** (3 个提示词)
6. **边日期提取** (1 个提示词)
7. **边失效** (2 个提示词)
8. **评估** (4 个提示词)

所有提示词都通过 `prompt_library` 统一管理，支持版本控制和自定义扩展。

