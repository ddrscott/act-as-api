import pytest
from act_as_api import bots
from langchain.schema import HumanMessage, SystemMessage
from langchain.schema.messages import messages_from_dict

def test_fetch_bots():
    found = bots.parse_bot_data()
    assert len(found) > 0


def test_fetch_all():
    found = bots.fetch_all()
    assert len(found) > 0
    assert found[0].messages[0]['role'] == 'system'

def test_predict():
    messages = [
        SystemMessage(content="Act as a calculator. You respond with only the answer. No need to say 'the answer is'."),
        HumanMessage(content="1 + 1"),
    ]

    response = bots.predict(messages)
    assert response == '2'

def test_predict_dict():
    messages = [
        {'role': 'system', 'content': "Act as a calculator and only respond the answer. No need to say 'the answer is'."},
        {'role': 'human', 'content': "1 + 1"},
    ]

    response = bots.predict(messages)
    assert response == '2'

def test_process_jinja():
    message = HumanMessage(content="Hello {{ name }}")
    bots.process_jinja(message, name="World")
    assert message.content == "Hello World"

def test_build_message_with_update():
    messages = [
        m.content
        for m in bots.build_messages(message="World", bot_messages=[{'role': 'system', 'content': "Hello {{ message }}"}])
    ]
    assert '\n'.join(messages) == "Hello World"

def test_build_message_with_append():
    messages = [
        m.content
        for m in bots.build_messages(message="Bob", bot_messages=[{'role': 'system', 'content': "Who are you?"}])
    ]
    assert '\n'.join(messages) == "Who are you?\nBob"

def test_calculator():
    bot =bots.fetch('calculator')
    assert bot.one_shot(message="3 + 2") == "5"

def test_translate():
    bot =bots.fetch('translate')
    assert bot.one_shot(message="Hello", to='French') == "Bonjour"

def test_undefined_param():
    bot =bots.fetch('translate')
    with pytest.raises(ValueError) as exc_info:
        bot.one_shot(typo_message="Hello", to='French')
        assert str(exc_info.value) == "'message' is required!"
