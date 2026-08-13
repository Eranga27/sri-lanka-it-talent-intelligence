"""
Location Transformation Logic

Normalizes location data hierarchically:
1. Structured fields (country, region, city)
2. Textual matching on raw location strings

Provides:
- normalized country (e.g. "Sri Lanka")
- region
- city
- location string
- location_detection_method
- location_confidence
"""
import re
from typing import Optional, Tuple

_SL_KEYWORDS = [
    "sri lanka",
    "srilanka",
    "colombo",
    "kandy",
    "galle",
    "negombo",
    "dehiwala",
    "moratuwa",
    "kotte",
    "nugegoda",
    "battaramulla",
    "malabe",
    "kaduwela",
]

def normalize_location(
    raw_country: Optional[str] = None,
    raw_region: Optional[str] = None,
    raw_city: Optional[str] = None,
    raw_location_string: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], str, float]:
    """
    Returns (country, region, city, location, detection_method, confidence)
    """
    country = raw_country.strip() if raw_country else None
    region = raw_region.strip() if raw_region else None
    city = raw_city.strip() if raw_city else None
    location = raw_location_string.strip() if raw_location_string else None
    
    # Check structured country
    if country:
        c_lower = country.lower()
        if c_lower in ["sri lanka", "lk", "srilanka"]:
            return "Sri Lanka", region, city, location, "structured_country", 1.0
        
        # If country is explicitly not Sri Lanka, we trust the structured data
        return country, region, city, location, "structured_country", 1.0
    
    # No structured country, fallback to text matching on city/region/location
    loc_lower = " ".join(filter(None, [region, city, location])).lower()
    
    if not loc_lower:
        return None, None, None, None, "none", 0.0
    
    for kw in _SL_KEYWORDS:
        if kw in loc_lower:
            return "Sri Lanka", region, city, location, "text_fallback", 0.7
            
    # Check isolated "lk" in the location string
    if re.search(r"\blk\b", loc_lower):
        return "Sri Lanka", region, city, location, "text_fallback_iso", 0.6
        
    # Unmatched location
    return None, region, city, location, "unclassified", 0.0
