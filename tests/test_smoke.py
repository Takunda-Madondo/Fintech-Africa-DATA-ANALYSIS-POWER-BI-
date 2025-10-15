import importlib
import app


def test_load_data():
    df = app.load_data('datasets/fintech_usage_africa.csv')
    assert df is not None
    assert len(df) > 0
