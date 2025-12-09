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

from pydantic import BaseModel, Field

from .models import Message, PromptFunction, PromptVersion
from .prompt_helpers import to_prompt_json


class QueryExpansion(BaseModel):
    query: str = Field(..., description='query optimized for database search')


class QAResponse(BaseModel):
    ANSWER: str = Field(..., description='how Alice would answer the question')


class EvalResponse(BaseModel):
    is_correct: bool = Field(..., description='boolean if the answer is correct or incorrect')
    reasoning: str = Field(
        ..., description='why you determined the response was correct or incorrect'
    )


class EvalAddEpisodeResults(BaseModel):
    candidate_is_worse: bool = Field(
        ...,
        description='boolean if the baseline extraction is higher quality than the candidate extraction.',
    )
    reasoning: str = Field(
        ..., description='why you determined the response was correct or incorrect'
    )


class Prompt(Protocol):
    qa_prompt: PromptVersion
    eval_prompt: PromptVersion
    query_expansion: PromptVersion
    eval_add_episode_results: PromptVersion


class Versions(TypedDict):
    qa_prompt: PromptFunction
    eval_prompt: PromptFunction
    query_expansion: PromptFunction
    eval_add_episode_results: PromptFunction


def query_expansion(context: dict[str, Any]) -> list[Message]:
    """
    将问题重写为更适合数据库检索的查询
    
    用途: 将用户问题优化为更适合知识图谱检索的查询语句
    输入:
        context['query']: 原始问题
    输出: Message 列表，包含系统提示和用户提示
    使用场景: 查询优化，提高检索准确性
    """
    sys_prompt = """You are an expert at rephrasing questions into queries used in a database retrieval system"""

    user_prompt = f"""
    Bob is asking Alice a question, are you able to rephrase the question into a simpler one about Alice in the third person
    that maintains the relevant context?
    <QUESTION>
    {to_prompt_json(context['query'])}
    </QUESTION>
    """
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]


def qa_prompt(context: dict[str, Any]) -> list[Message]:
    """
    基于实体摘要和事实回答问题
    
    用途: 使用实体摘要和事实信息生成问题的答案
    输入:
        context['entity_summaries']: 实体摘要列表
        context['facts']: 事实列表
        context['query']: 问题
    输出: Message 列表，包含系统提示和用户提示
    使用场景: 问答生成，基于知识图谱的问答
    """
    sys_prompt = """You are Alice and should respond to all questions from the first person perspective of Alice"""

    user_prompt = f"""
    Your task is to briefly answer the question in the way that you think Alice would answer the question.
    You are given the following entity summaries and facts to help you determine the answer to your question.
    <ENTITY_SUMMARIES>
    {to_prompt_json(context['entity_summaries'])}
    </ENTITY_SUMMARIES>
    <FACTS>
    {to_prompt_json(context['facts'])}
    </FACTS>
    <QUESTION>
    {context['query']}
    </QUESTION>
    """
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]


def eval_prompt(context: dict[str, Any]) -> list[Message]:
    """
    评估答案是否正确
    
    用途: 判断回答是否与标准答案匹配，评估答案质量
    输入:
        context['query']: 问题
        context['answer']: 标准答案
        context['response']: 待评估的回答
    输出: Message 列表，包含系统提示和用户提示
    使用场景: 答案质量评估，用于系统测试和优化
    """
    sys_prompt = (
        """You are a judge that determines if answers to questions match a gold standard answer"""
    )

    user_prompt = f"""
    Given the QUESTION and the gold standard ANSWER determine if the RESPONSE to the question is correct or incorrect.
    Although the RESPONSE may be more verbose, mark it as correct as long as it references the same topic 
    as the gold standard ANSWER. Also include your reasoning for the grade.
    <QUESTION>
    {context['query']}
    </QUESTION>
    <ANSWER>
    {context['answer']}
    </ANSWER>
    <RESPONSE>
    {context['response']}
    </RESPONSE>
    """
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]


def eval_add_episode_results(context: dict[str, Any]) -> list[Message]:
    """
    评估基线提取和候选提取的质量
    
    用途: 比较基线提取结果和候选提取结果的质量，判断哪个更好
    输入:
        context['previous_messages']: 历史消息列表
        context['message']: 当前消息
        context['baseline']: 基线提取结果
        context['candidate']: 候选提取结果
    输出: Message 列表，包含系统提示和用户提示
    使用场景: 提取质量评估，用于提示词优化和系统改进
    """
    sys_prompt = """You are a judge that determines whether a baseline graph building result from a list of messages is better
        than a candidate graph building result based on the same messages."""

    user_prompt = f"""
    Given the following PREVIOUS MESSAGES and MESSAGE, determine if the BASELINE graph data extracted from the 
    conversation is higher quality than the CANDIDATE graph data extracted from the conversation.
    
    Return False if the BASELINE extraction is better, and True otherwise. If the CANDIDATE extraction and
    BASELINE extraction are nearly identical in quality, return True. Add your reasoning for your decision to the reasoning field
    
    <PREVIOUS MESSAGES>
    {context['previous_messages']}
    </PREVIOUS MESSAGES>
    <MESSAGE>
    {context['message']}
    </MESSAGE>
    
    <BASELINE>
    {context['baseline']}
    </BASELINE>
    
    <CANDIDATE>
    {context['candidate']}
    </CANDIDATE>
    """
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]


versions: Versions = {
    'qa_prompt': qa_prompt,
    'eval_prompt': eval_prompt,
    'query_expansion': query_expansion,
    'eval_add_episode_results': eval_add_episode_results,
}
