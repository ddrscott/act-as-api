"""
Responsibly for parsing bot data out of YAML files from a certain directory.
The directory is configured by BOTS_PATH setting.
Bots are individual YAML files in the directory.
An example of a bot YAML file:
    messages:
      - role: system
        content: Hello, I am a bot!
      - role: ai
        content: How can I help you?
      - role: human
        content: |
            Can you summarize the following text:
            #body
"""
import logging
import os
import re
import yaml
from functools import lru_cache
from typing import AsyncIterable, Awaitable

import asyncio
import click
import jinja2
from pydantic import BaseModel

from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.schema import SystemMessage, HumanMessage, AIMessage, FunctionMessage, BaseMessage

from . import env

ROLE_TO_CLASS = {
    'system': SystemMessage,
    'human': HumanMessage,
    'function': FunctionMessage,
    'ai': AIMessage
}


class Bot(BaseModel):
    name: str
    messages: list[dict[str, str]]
    temperature: float = 0.5

    def one_shot(self, **params) -> str:
        """
        Predict the response of a bot to a list of messages.
        """
        messages = build_messages(self.messages, **params)
        return predict(messages, temperature=self.temperature)

    def async_one_shot(self, **params) -> AsyncIterable[str]:
        messages = build_messages(self.messages, **params)
        return async_predict(messages)

@lru_cache
def fetch_all():
    return [Bot(**bot) for bot in parse_bot_data()]

def fetch(name):
    """
    Fetch a bot by name.
    """
    for bot in fetch_all():
        if bot.name == name:
            return bot
    raise Exception(f'Bot {name} not found')

def build_messages(bot_messages, **params):
    """
    Build a list of messages from a new message and a list of bot messages.
    """
    has_message = False
    messages =  messages_from_dict(bot_messages)
    for m in messages:
        if has_message_template(m):
            has_message = True
        process_jinja(m, **params)
    if not has_message:
        messages.append(HumanMessage(content=params.get('message', '')))
    return messages


def has_message_template(message: BaseMessage) -> bool:
    return re.search(r'{{\s*message\s*}}', message.content) is not None

def parse_bot_data():
    bots = []
    for bot_file in os.listdir(env.BOTS_PATH):
        if re.match(r".*\.y[a]?ml$", bot_file):
            with open(os.path.join(env.BOTS_PATH, bot_file), "r") as f:
                data = yaml.safe_load(f.read())
                # get name from files base name
                name = os.path.splitext(bot_file)[0]
                data['name'] = name
                bots.append(data)
    return bots

def process_jinja(base_message: BaseMessage, **params):
    """
    Process jinja templates in the message content.
    """
    template = jinja2.Template(base_message.content, undefined=jinja2.StrictUndefined)
    try:
        base_message.content = template.render(**params)
    except jinja2.exceptions.UndefinedError as e:
        msg = str(e).replace('undefined', 'required!')
        raise ValueError(msg)


class CustomHandler(StreamingStdOutCallbackHandler):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def on_llm_start(self, serialized, prompts, **_) -> None:
        self.logger.info(f"prompts: {prompts}")
        click.echo("\033[33m", nl=False)
        pass

    def on_llm_new_token(self, token: str, **_) -> None:
        click.echo(token, nl=False)

    def on_llm_end(self, response, **kwargs) -> None:
        click.echo("\033[0m")
        self.logger.info(f"response: {response}")

def convert_messages_if_needed(messages) -> list[BaseMessage]:
    if messages is None:
        return []

    if not isinstance(messages, list):
        messages = [messages]

    if messages and isinstance(messages[0], dict):
        return messages_from_dict(messages)

    return messages

def predict(messages, model:str=env.DEFAULT_LLM_MODEL, max_retries=5, temperature=0.5) -> str:
    """
    Wrapper around ChatOpenAI.predict_messages that allows for custom callbacks.
    """
    llm = ChatOpenAI(
        model=model,
        client=None,
        streaming=True,
        temperature=temperature,
        verbose=True,
        max_retries=max_retries,
        callbacks=[CustomHandler()],
    )
    messages = convert_messages_if_needed(messages)
    response = llm.predict_messages(messages)
    return response.content

async def async_predict(messages, model:str=env.DEFAULT_LLM_MODEL) -> AsyncIterable[str]:
    """
    Allows for tokens to be yielded as they are generated.

    Thanks: https://gist.github.com/ninely/88485b2e265d852d3feb8bd115065b1a
    """
    async_callback = AsyncIteratorCallbackHandler()
    llm = ChatOpenAI(
        client=None,
        model=model,
        streaming=True,
        verbose=True,
        callbacks=[async_callback, CustomHandler()],
    )

    async def wrap_done(fn: Awaitable, event: asyncio.Event):
        logger = logging.getLogger(__name__)
        try:
            await fn
        except Exception as e:
            logger.exception(e)
        finally:
            event.set()

    messages = convert_messages_if_needed(messages)

    task = asyncio.create_task(wrap_done(
        llm.agenerate(messages=[messages]),
        async_callback.done),
    )

    async for token in async_callback.aiter():
        yield token

    await task

def messages_from_dict(messages:list[dict]):
    return [ROLE_TO_CLASS[m['role']](content=m['content']) for m in messages]
