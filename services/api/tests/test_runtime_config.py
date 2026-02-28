from app.config import Settings


def test_production_validation_passes_with_safe_values():
    settings = Settings(
        environment="production",
        debug=False,
        secret_key="x" * 48,
        cors_origins_raw="https://app.example.com,https://admin.example.com",
    )
    assert settings.production_validation_errors() == []


def test_production_validation_blocks_default_and_insecure_values():
    settings = Settings(
        environment="production",
        debug=True,
        secret_key="change-me-in-production",
        cors_origins_raw="http://localhost:3000,https://app.example.com",
    )
    errors = settings.production_validation_errors()
    assert any("default placeholder" in item for item in errors)
    assert any("at least 32 characters" in item for item in errors)
    assert any("DEBUG must be false" in item for item in errors)
    assert any("localhost origins" in item for item in errors)
