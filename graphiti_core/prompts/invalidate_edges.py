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


class InvalidatedEdges(BaseModel):
    contradicted_facts: list[int] = Field(
        ...,
        description='List of ids of facts that should be invalidated. If no facts should be invalidated, the list should be empty.',
    )


class Prompt(Protocol):
    v1: PromptVersion
    v2: PromptVersion


class Versions(TypedDict):
    v1: PromptFunction
    v2: PromptFunction


def v1(context: dict[str, Any]) -> list[Message]:
    """
    基于新边判断哪些现有边应该失效（基于时间戳）
    
    用途: 根据新边和现有边的时间戳，判断哪些现有关系应该被标记为失效
    输入:
        context['previous_episodes']: 历史消息列表
        context['current_episode']: 当前消息
        context['existing_edges']: 现有边列表（按时间戳排序，最新的在前）
        context['new_edges']: 新提取的边列表
    输出: Message 列表，包含系统提示和用户提示
    使用场景: 关系失效检测（基于时间戳和矛盾关系）
    """
    return [
        Message(
            role='system',
            content='You are an AI assistant that helps determine which relationships in a knowledge graph should be invalidated based solely on explicit contradictions in newer information.',
        ),
        Message(
            role='user',
            content=f"""
               Based on the provided existing edges and new edges with their timestamps, determine which relationships, if any, should be marked as expired due to contradictions or updates in the newer edges.
               Use the start and end dates of the edges to determine which edges are to be marked expired.
                Only mark a relationship as invalid if there is clear evidence from other edges that the relationship is no longer true.
                Do not invalidate relationships merely because they weren't mentioned in the episodes. You may use the current episode and previous episodes as well as the facts of each edge to understand the context of the relationships.

                Previous Episodes:
                {context['previous_episodes']}

                Current Episode:
                {context['current_episode']}

                Existing Edges (sorted by timestamp, newest first):
                {context['existing_edges']}

                New Edges:
                {context['new_edges']}

                Each edge is formatted as: "UUID | SOURCE_NODE - EDGE_NAME - TARGET_NODE (fact: EDGE_FACT), START_DATE (END_DATE, optional))"
            """,
        ),
    ]


def v2(context: dict[str, Any]) -> list[Message]:
    """
    基于新事实判断哪些现有事实被矛盾（基于矛盾检测）
    
    用途: 根据新事实判断哪些现有事实被矛盾，需要被标记为失效
    输入:
        context['existing_edges']: 现有事实列表
        context['new_edge']: 新提取的事实
    输出: Message 列表，包含系统提示和用户提示
    使用场景: 关系失效检测（基于矛盾关系）
    """
    return [
        Message(
            role='system',
            content='You are an AI assistant that determines which facts contradict each other.',
        ),
        Message(
            role='user',
            content=f"""
               Based on the provided EXISTING FACTS and a NEW FACT, determine which existing facts the new fact contradicts.
               Return a list containing all ids of the facts that are contradicted by the NEW FACT.
               If there are no contradicted facts, return an empty list.

                <EXISTING FACTS>
                {context['existing_edges']}
                </EXISTING FACTS>

                <NEW FACT>
                {context['new_edge']}
                </NEW FACT>
            """,
        ),
    ]


versions: Versions = {'v1': v1, 'v2': v2}
