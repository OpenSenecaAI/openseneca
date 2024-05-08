import pytest
from unittest.mock import Mock, patch
from openseneca.models.mistral import MistralLargeChatModel

def test_mistral_large_chat_model_initialization():
    provider_mock = Mock()
    model = MistralLargeChatModel(provider=provider_mock)
    assert model.provider == provider_mock

def test_mistral_large_chat_model_request():
    provider_mock = Mock()
    provider_mock.request.return_value = "Test response"
    model = MistralLargeChatModel(provider=provider_mock)

    response = model.request("Test prompt")
    assert response == "Test response"
    provider_mock.request.assert_called_once()

@patch('openseneca.models.mistral.MistralLargeChatModel.request')
def test_mistral_large_chat_model_request_with_instructions(mock_request):
    mock_request.return_value = "Test response"
    model = MistralLargeChatModel(provider=Mock())
    response = model.request("Test prompt", instructions="Test instructions")
    assert response == "Test response"
    mock_request.assert_called_once()

@patch('openseneca.models.mistral.MistralLargeChatModel.request')
def test_mistral_large_chat_model_request_with_past_messages(mock_request):
    mock_request.return_value = "Test response"
    model = MistralLargeChatModel(provider=Mock())
    response = model.request("Test prompt", past_messages=["Past message"])
    assert response == "Test response"
    mock_request.assert_called_once()

@patch('openseneca.models.mistral.MistralLargeChatModel.request')
def test_mistral_large_chat_model_request_with_settings(mock_request):
    mock_request.return_value = "Test response"
    model = MistralLargeChatModel(provider=Mock())
    response = model.request("Test prompt", settings={"setting": "value"})
    assert response == "Test response"
    mock_request.assert_called_once()