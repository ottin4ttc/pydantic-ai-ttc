import pytest
from ttc_agent.tests.ui.conftest import RUN_DIR, LOGGER, REPORT_GENERATOR
from ttc_agent.tests.ui.test_utils import UITestResult

# Import the test functions directly
from ttc_agent.tests.ui.test_send_message import test_send_message
from ttc_agent.tests.ui.test_create_conversation import test_create_conversation
from ttc_agent.tests.ui.test_conversation_switching import test_conversation_switching

# Define wrapper functions that will be discovered by pytest
def test_send_message_wrapper(conversation_page):
    """Wrapper for test_send_message"""
    LOGGER.info("Starting test_send_message_wrapper")
    return test_send_message(conversation_page)

def test_create_conversation_wrapper(conversation_page):
    """Wrapper for test_create_conversation"""
    LOGGER.info("Starting test_create_conversation_wrapper")
    return test_create_conversation(conversation_page)

def test_conversation_switching_wrapper(conversation_page):
    """Wrapper for test_conversation_switching"""
    LOGGER.info("Starting test_conversation_switching_wrapper")
    return test_conversation_switching(conversation_page)
