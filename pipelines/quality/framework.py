from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, ValidationError

class DataQualityReport(BaseModel):
    run_id: str
    timestamp: datetime
    records_received: int
    records_accepted: int
    records_rejected: int
    duplicates: int
    validation_errors: Dict[str, int]
    processing_time_ms: float
    data_quality_score: float

class DataQualityFramework:
    def __init__(self, schema_model: type[BaseModel]):
        self.schema_model = schema_model
        
    def check_schema_validity(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate records against Pydantic schema."""
        accepted = []
        rejected = []
        errors = {}
        
        for record in records:
            try:
                valid_record = self.schema_model(**record)
                accepted.append(valid_record.model_dump())
            except ValidationError as e:
                rejected.append(record)
                for err in e.errors():
                    loc = err.get("loc", ["unknown"])[0]
                    errors[loc] = errors.get(loc, 0) + 1
                    
        return {
            "accepted": accepted,
            "rejected": rejected,
            "errors": errors
        }

    def calculate_quality_score(self, total: int, accepted: int) -> float:
        """Calculate simple quality score based on acceptance rate."""
        if total == 0:
            return 0.0
        return round((accepted / total) * 100, 2)
