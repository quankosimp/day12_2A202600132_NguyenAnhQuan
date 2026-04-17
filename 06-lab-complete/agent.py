import logging
import os
import uuid
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import tools_condition
from typing_extensions import TypedDict

from tools import calculate_budget, search_flights, search_hotels

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
SYSTEM_PROMPT_PATH = BASE_DIR / "system_prompt.txt"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE_PATH = LOG_DIR / "agent.log"
DEFAULT_MODEL = "gpt-4o-mini"
SYSTEM_ERROR_MESSAGE = "Hệ thống đang bị lỗi..."
MAX_TOOL_RETRIES = 3


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("travelbuddy.agent")
    if logger.handlers:
        return logger

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger


logger = setup_logger()


def load_system_prompt() -> str:
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()


def create_llm() -> ChatOpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "Thiếu API key. Hãy đặt OPENAI_API_KEY trong biến môi trường."
        )

    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)

    return ChatOpenAI(
        model=model,
        api_key=api_key,
    )


SYSTEM_PROMPT = load_system_prompt()


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    trace_id: str


def get_tools_list():
    return [search_flights, search_hotels, calculate_budget]


@lru_cache(maxsize=1)
def get_tools_map():
    return {tool.name: tool for tool in get_tools_list()}


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    return create_llm()


@lru_cache(maxsize=1)
def get_llm_with_tools():
    return get_llm().bind_tools(get_tools_list())


def agent_node(state: AgentState):
    messages = list(state["messages"])
    trace_id = state.get("trace_id", "-")
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    if _has_recent_tool_failure(messages):
        logger.error("[%s] Tool lỗi sau 3 lần thử, trả fallback", trace_id)
        return {"messages": [AIMessage(content=SYSTEM_ERROR_MESSAGE)]}

    logger.info("[%s] Agent node start | messages=%s", trace_id, len(messages))
    try:
        response = get_llm_with_tools().invoke(messages)
    except Exception as exc:
        logger.exception("[%s] LLM invoke failed | error=%s", trace_id, exc)
        raise

    if response.tool_calls:
        for tc in response.tool_calls:
            logger.info(
                "[%s] Tool planned | name=%s | args=%s",
                trace_id,
                tc["name"],
                tc["args"],
            )
    else:
        logger.info("[%s] Direct response", trace_id)

    return {"messages": [response]}


def _has_recent_tool_failure(messages: list) -> bool:
    return bool(
        messages
        and isinstance(messages[-1], ToolMessage)
        and str(messages[-1].content).strip() == SYSTEM_ERROR_MESSAGE
    )


def tools_node(state: AgentState):
    messages = list(state["messages"])
    trace_id = state.get("trace_id", "-")
    last_message = messages[-1]
    tool_messages = []

    for tool_call in getattr(last_message, "tool_calls", []):
        tool_name = tool_call["name"]
        tool = get_tools_map().get(tool_name)
        args = tool_call.get("args", {})

        if tool is None:
            logger.error("[%s] Tool not found | name=%s", trace_id, tool_name)
            content = SYSTEM_ERROR_MESSAGE
        else:
            content = _invoke_tool_with_retry(trace_id, tool_name, tool, args)

        tool_messages.append(
            ToolMessage(
                content=content,
                tool_call_id=tool_call["id"],
                name=tool_name,
            )
        )

    return {"messages": tool_messages}


def _invoke_tool_with_retry(trace_id: str, tool_name: str, tool, args: dict) -> str:
    last_error = None

    for attempt in range(1, MAX_TOOL_RETRIES + 1):
        try:
            logger.info(
                "[%s] Tool invoke | name=%s | attempt=%s | args=%s",
                trace_id,
                tool_name,
                attempt,
                args,
            )
            result = str(tool.invoke(args))
            logger.info(
                "[%s] Tool success | name=%s | attempt=%s",
                trace_id,
                tool_name,
                attempt,
            )
            return result
        except Exception as exc:
            last_error = exc
            logger.warning(
                "[%s] Tool failed | name=%s | attempt=%s | error=%s",
                trace_id,
                tool_name,
                attempt,
                exc,
            )

    logger.error(
        "[%s] Tool exhausted retries | name=%s | retries=%s | last_error=%s",
        trace_id,
        tool_name,
        MAX_TOOL_RETRIES,
        last_error,
    )
    return SYSTEM_ERROR_MESSAGE


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("agent", agent_node)

    builder.add_node("tools", tools_node)

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")

    return builder.compile()


@lru_cache(maxsize=1)
def get_graph():
    return build_graph()


def run_agent(user_input: str):
    trace_id = uuid.uuid4().hex[:12]
    logger.info("[%s] Run start | input=%s", trace_id, user_input)
    result = get_graph().invoke(
        {
            "messages": [("human", user_input)],
            "trace_id": trace_id,
        }
    )
    final_message = result["messages"][-1].content if result.get("messages") else ""
    logger.info("[%s] Run end | final=%s", trace_id, final_message)
    result["trace_id"] = trace_id
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("TravelBuddy — Trợ lý Du lịch Thông minh")
    print("Gõ 'quit' để thoát")
    print("=" * 60)

    while True:
        user_input = input("\nBạn: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break

        print("\nTravelBuddy đang suy nghĩ...")
        result = run_agent(user_input)
        final = result["messages"][-1]
        trace_id = result.get("trace_id", "-")

        print(f"\nTravelBuddy [{trace_id}]: {final.content}")
