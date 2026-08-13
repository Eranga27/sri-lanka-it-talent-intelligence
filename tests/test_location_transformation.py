import pytest
from pipelines.transformations.location import normalize_location

def test_structured_sri_lanka():
    c, r, ct, l, m, conf = normalize_location(raw_country="Sri Lanka", raw_city="Colombo")
    assert c == "Sri Lanka"
    assert m == "structured_country"
    assert conf == 1.0

def test_structured_lk_code():
    c, r, ct, l, m, conf = normalize_location(raw_country="LK")
    assert c == "Sri Lanka"
    assert m == "structured_country"
    assert conf == 1.0

def test_structured_other_country():
    c, r, ct, l, m, conf = normalize_location(raw_country="United Kingdom", raw_city="London")
    assert c == "United Kingdom"
    assert m == "structured_country"
    assert conf == 1.0

def test_text_fallback_sri_lanka():
    c, r, ct, l, m, conf = normalize_location(raw_location_string="Colombo, Western Province, Sri Lanka")
    assert c == "Sri Lanka"
    assert m == "text_fallback"
    assert conf == 0.7

def test_text_fallback_city_only():
    c, r, ct, l, m, conf = normalize_location(raw_location_string="Kandy")
    assert c == "Sri Lanka"
    assert m == "text_fallback"
    assert conf == 0.7

def test_text_fallback_lk_iso():
    c, r, ct, l, m, conf = normalize_location(raw_location_string="Remote, LK")
    assert c == "Sri Lanka"
    assert m == "text_fallback_iso"
    assert conf == 0.6

def test_unclassified_location():
    c, r, ct, l, m, conf = normalize_location(raw_location_string="Remote EMEA")
    assert c is None
    assert m == "unclassified"
    assert conf == 0.0

def test_empty_location():
    c, r, ct, l, m, conf = normalize_location()
    assert c is None
    assert m == "none"
    assert conf == 0.0
