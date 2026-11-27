import pytest
from wfx.components.input_output import TextOutputComponent

from tests.base import ComponentTestBaseWithoutClient


class TestTextOutputComponent(ComponentTestBaseWithoutClient):
    @pytest.fixture
    def component_class(self):
        return TextOutputComponent

    @pytest.fixture
    def default_kwargs(self):
        return {
            "input_value": "Hello, world!",
        }

    @pytest.fixture
    def file_names_mapping(self):
        return []
