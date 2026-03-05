import pytest


@pytest.mark.skip(reason="Requires docker stack with Postgres + MinIO + Playwright")
def test_full_api_flow_placeholder() -> None:
    # Placeholder for local integration:
    # create carousel -> run generation -> edit slide/design -> export -> download zip.
    assert True

