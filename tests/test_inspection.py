import pytest
import os
from openseneca.utils.inspection import get_model_builder, get_LLMs, ModelBuilderNotFound
from openseneca.interfaces.models import ModelBuilder

def test_get_model_builder():
    class DummyModel:
        NAME = 'Dummy'
    class DummyBuilder(ModelBuilder):
        pass
    # Add DummyModel and DummyBuilder to the module
    import openseneca.models
    openseneca.models.DummyModel = DummyModel
    openseneca.models.DummyBuilder = DummyBuilder
    # Test get_model_builder
    assert get_model_builder('Dummy') == DummyBuilder
    # Test ModelBuilderNotFound exception
    with pytest.raises(ModelBuilderNotFound):
        get_model_builder('NonExistent')

def test_get_LLMs():
    # Set up environment variables
    os.environ['oS__TEST1_ENDPOINT'] = 'test1_endpoint'
    os.environ['oS__TEST1_AUTH'] = 'test1_auth'
    os.environ['oS__TEST2_ENDPOINT'] = 'test2_endpoint'
    os.environ['oS__TEST2_AUTH'] = 'test2_auth'
    # All test LLMs (TEST1, TEST2) should be in the get_LLMs() list.
    assert all(element in get_LLMs() for element in ['TEST1', 'TEST2'])
    # Clean up environment variables
    del os.environ['oS__TEST1_ENDPOINT']
    del os.environ['oS__TEST1_AUTH']
    del os.environ['oS__TEST2_ENDPOINT']
    del os.environ['oS__TEST2_AUTH']

def test_from_all_llms():
    llms = get_LLMs()
    for llm in llms:
        assert get_model_builder(llm) is not None
