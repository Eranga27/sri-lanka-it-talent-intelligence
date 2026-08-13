import pytest
from datetime import datetime
from pydantic import BaseModel, ValidationError
from pipelines.quality.framework import DataQualityFramework

class DummySchema(BaseModel):
    id: int
    name: str

def test_data_quality_framework_valid():
    framework = DataQualityFramework(DummySchema)
    records = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    result = framework.check_schema_validity(records)
    
    assert len(result["accepted"]) == 2
    assert len(result["rejected"]) == 0
    assert len(result["errors"]) == 0
    
def test_data_quality_framework_invalid():
    framework = DataQualityFramework(DummySchema)
    records = [{"id": 1, "name": "Alice"}, {"id": "invalid", "name": "Bob"}, {"name": "Charlie"}]
    result = framework.check_schema_validity(records)
    
    assert len(result["accepted"]) == 1
    assert len(result["rejected"]) == 2
    assert "id" in result["errors"]

def test_data_quality_score():
    framework = DataQualityFramework(DummySchema)
    assert framework.calculate_quality_score(10, 8) == 80.0
    assert framework.calculate_quality_score(0, 0) == 0.0
