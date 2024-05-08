import pytest
from unittest.mock import Mock, patch
from openseneca.models.llama2 import LLama27BChatModel

def test_llama2_chat_model_initialization():
    provider_mock = Mock()
    model = LLama27BChatModel(provider=provider_mock)
    assert model.provider == provider_mock

def test_llama2_chat_model_request():
    provider_mock = Mock()
    provider_mock.request.return_value = "Test response"
    model = LLama27BChatModel(provider=provider_mock)

    response = model.request("Test prompt")
    assert response == "Test response"
    provider_mock.request.assert_called_once()

@patch('openseneca.models.llama2.LLama27BChatModel.request')
def test_llama2_chat_model_request_with_instructions(mock_request):
    mock_request.return_value = "Test response"
    model = LLama27BChatModel(provider=Mock())
    response = model.request("Test prompt", instructions="Test instructions")
    assert response == "Test response"
    mock_request.assert_called_once()

@patch('openseneca.models.llama2.LLama27BChatModel.request')
def test_llama2_chat_model_request_with_past_messages(mock_request):
    mock_request.return_value = "Test response"
    model = LLama27BChatModel(provider=Mock())
    response = model.request("Test prompt", past_messages=["Past message"])
    assert response == "Test response"
    mock_request.assert_called_once()

@patch('openseneca.models.llama2.LLama27BChatModel.request')
def test_llama2_chat_model_request_with_settings(mock_request):
    mock_request.return_value = "Test response"
    model = LLama27BChatModel(provider=Mock())
    response = model.request("Test prompt", settings={"setting": "value"})
    assert response == "Test response"
    mock_request.assert_called_once()