from datetime import date, datetime
import json
import os
from pydantic import ValidationError
import pytest

from medsearch_api.app.dailymed_response.models import (
    SPLListItemResponse,
    SPLListMetadata,
    SPLListResponse,
)


@pytest.fixture
def mock_spl_list_response():
    file_path = os.path.join(
        os.path.dirname(__file__), "fixtures", "mock_spl_list_response.json"
    )
    with open(file_path, "r") as file:
        return json.load(file)


@pytest.fixture
def spl_list_item_data(mock_spl_list_response):
    return mock_spl_list_response["data"]


@pytest.fixture
def spl_list_metadata_data(mock_spl_list_response):
    return mock_spl_list_response["metadata"]


class TestSPLListItemResponse:
    def test_valid_data_should_deserialize_correctly(self, spl_list_item_data):

        assert len(spl_list_item_data) == 3

        # First item
        item_data = spl_list_item_data[0]
        item = SPLListItemResponse(**item_data)

        assert item.spl_version == 13
        assert item.published_date == date(2024, 8, 23)
        assert item.title == "FIBRYGA (FIBRINOGEN (HUMAN)) KIT [OCTAPHARMA USA INC]"
        assert item.set_id == "007a93f4-d84b-1fa9-51ed-32f6140bf423"

        # Second item
        item_data = spl_list_item_data[1]
        item = SPLListItemResponse(**item_data)
        assert item.spl_version == 3
        assert item.published_date == date(2024, 8, 23)
        assert (
            item.title
            == "NATURIUM DEW-GLOW MOISTURIZER SPF 50 CREAM [MANA PRODUCTS, INC]"
        )
        assert item.set_id == "00c93b11-754e-701c-e063-6294a90a3b1d"

        # Third item
        item_data = spl_list_item_data[2]
        item = SPLListItemResponse(**item_data)
        assert item.spl_version == 107
        assert item.published_date == date(2024, 8, 23)
        assert (
            item.title == "GUANFACINE TABLET, EXTENDED RELEASE [BRYANT RANCH PREPACK]"
        )
        assert item.set_id == "00f244f8-353d-4674-b479-26aad6b1619a"

    def test_missing_field_should_raise_validation_error(self, spl_list_item_data):
        incomplete_data = spl_list_item_data[0].copy()
        incomplete_data.pop("setid")  # Remove a required field

        with pytest.raises(ValidationError) as e:
            SPLListItemResponse(**incomplete_data)

        error = e.value.errors()[0]
        assert error["type"] == "missing"
        assert error["loc"] == ("setid",)
        assert error["msg"] == "Field required"

    def test_empty_string_for_set_id_should_be_converted_to_none_and_raise(
        self, spl_list_item_data
    ):
        invalid_data = spl_list_item_data[0].copy()
        invalid_data["setid"] = ""

        with pytest.raises(ValidationError) as e:
            SPLListItemResponse(**invalid_data)
        error = e.value.errors()[0]
        assert error["type"] == "string_type"
        assert error["loc"] == ("setid",)
        assert error["msg"] == "Input should be a valid string"

    def test_invalid_spl_version_should_raise_validation_error(
        self, spl_list_item_data
    ):
        invalid_data = spl_list_item_data[0].copy()
        invalid_data["spl_version"] = "invalid"

        with pytest.raises(ValidationError) as e:
            SPLListItemResponse(**invalid_data)

        # Access and inspect the captured exception
        error = e.value.errors()[0]
        assert error["loc"] == ("spl_version",)
        assert (
            error["msg"]
            == "Input should be a valid integer, unable to parse string as an integer"
        )
        assert error["type"] == "int_parsing"

    def test_published_date_string_should_be_parsed_correctly(self, spl_list_item_data):
        date_data = spl_list_item_data[0].copy()
        date_data["published_date"] = "Aug 23, 2024"

        item = SPLListItemResponse(**date_data)
        assert item.published_date == date(2024, 8, 23)


class TestSPLListMetadata:
    def test_valid_data_should_deserialize_correctly(self, spl_list_metadata_data):
        metadata = SPLListMetadata(**spl_list_metadata_data)

        assert metadata.db_published_date == datetime(2024, 8, 23, 20, 39, 50)
        assert metadata.elements_per_page == 3
        assert (
            metadata.next_page_url
            == "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?published_date=2024-08-17&published_date_comparison=gt&page=2&pagesize=3"
        )
        assert metadata.total_pages == 429
        assert metadata.total_elements == 1287
        assert (
            metadata.current_url
            == "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?published_date=2024-08-17&published_date_comparison=gt&page=1&pagesize=3"
        )
        assert metadata.next_page == 2
        assert metadata.previous_page is None
        assert metadata.previous_page_url is None
        assert metadata.current_page == 1

    def test_missing_required_fields_should_raise_validation_error(
        self, spl_list_metadata_data
    ):
        incomplete_data = spl_list_metadata_data.copy()
        incomplete_data.pop("db_published_date")

        with pytest.raises(ValidationError) as e:
            SPLListMetadata(**incomplete_data)

        error = e.value.errors()[0]
        assert error["type"] == "missing"
        assert error["loc"] == ("db_published_date",)
        assert error["msg"] == "Field required"

    def test_invalid_elements_per_page_should_raise_validation_error(
        self, spl_list_metadata_data
    ):
        invalid_data = spl_list_metadata_data.copy()
        invalid_data["elements_per_page"] = "invalid"

        with pytest.raises(ValidationError) as e:
            SPLListMetadata(**invalid_data)

        error = e.value.errors()[0]
        assert error["loc"] == ("elements_per_page",)
        assert (
            error["msg"]
            == "Input should be a valid integer, unable to parse string as an integer"
        )
        assert error["type"] == "int_parsing"

    def test_db_published_date_string_should_be_parsed_correctly(
        self, spl_list_metadata_data
    ):
        date_data = spl_list_metadata_data.copy()
        date_data["db_published_date"] = "Aug 23, 2024, 20:39:50"

        metadata = SPLListMetadata(**date_data)
        assert metadata.db_published_date == datetime(2024, 8, 23, 20, 39, 50)

    def test_null_string_should_be_converted_to_none_for_optional_fields(
        self, spl_list_metadata_data
    ):
        null_data = spl_list_metadata_data.copy()
        null_data["next_page_url"] = "null"
        null_data["previous_page"] = "null"

        metadata = SPLListMetadata(**null_data)
        assert metadata.next_page_url is None
        assert metadata.previous_page is None

    def test_null_string_should_be_converted_to_none_for_required_fields(
        self, spl_list_metadata_data
    ):
        null_data = spl_list_metadata_data.copy()
        null_data["current_url"] = "null"

        with pytest.raises(ValidationError) as e:
            SPLListMetadata(**null_data)

        error = e.value.errors()[0]
        assert error["loc"] == ("current_url",)
        assert error["msg"] == "Input should be a valid string"
        assert error["type"] == "string_type"

    def test_empty_string_for_optional_fields_should_not_raise_error(
        self, spl_list_metadata_data
    ):
        empty_string_data = spl_list_metadata_data.copy()
        empty_string_data["next_page_url"] = ""

        metadata = SPLListMetadata(**empty_string_data)
        assert metadata.next_page_url == ""

    def test_invalid_date_format_should_raise_validation_error(
        self, spl_list_metadata_data
    ):
        invalid_date_data = spl_list_metadata_data.copy()
        invalid_date_data["db_published_date"] = (
            "2024-23-08 20:39:50"  # Invalid date format
        )

        with pytest.raises(ValidationError) as e:
            SPLListMetadata(**invalid_date_data)

        error = e.value.errors()[0]
        assert error["loc"] == ("db_published_date",)
        assert "Value error, month must be in" in error["msg"]

    def test_non_integer_for_page_fields_should_raise_validation_error(
        self, spl_list_metadata_data
    ):
        invalid_page_data = spl_list_metadata_data.copy()
        invalid_page_data["total_pages"] = "ten"  # Invalid type

        with pytest.raises(ValidationError) as e:
            SPLListMetadata(**invalid_page_data)

        error = e.value.errors()[0]
        assert error["loc"] == ("total_pages",)
        assert (
            error["msg"]
            == "Input should be a valid integer, unable to parse string as an integer"
        )
        assert error["type"] == "int_parsing"

    def test_empty_string_optional_fields_should_default_to_none(
        self, spl_list_metadata_data
    ):
        incomplete_data = spl_list_metadata_data.copy()
        incomplete_data["next_page_url"] = ""

        metadata = SPLListMetadata(**incomplete_data)
        assert metadata.next_page_url is None


class TestSPLListResponse:

    def test_has_more_pages_should_return_true_when_more_pages_exist(
        self, mock_spl_list_response
    ):
        response_data = mock_spl_list_response
        response = SPLListResponse(**response_data)

        assert response.has_more_pages is True

    def test_has_more_pages_should_return_false_when_no_more_pages_exist(
        self, mock_spl_list_response
    ):
        response_data = mock_spl_list_response.copy()
        response_data["metadata"]["current_page"] = response_data["metadata"][
            "total_pages"
        ]

        response = SPLListResponse(**response_data)
        assert response.has_more_pages is False
