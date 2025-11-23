import requests
from fastapi import HTTPException
from typing import Optional, Dict

NHTSA_API_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json"

def decode_vin(vin: str) -> Dict[str, Optional[str]]:
    """
    Decodes a 17-character VIN using the public NHTSA API.
    Returns a dict containing 'brand_name', 'model_name', and 'year'.
    """
    if len(vin) != 17:
        raise HTTPException(
            status_code=400, detail="Invalid VIN format. Must be 17 characters."
        )

    try:
        response = requests.get(NHTSA_API_URL.format(vin=vin), timeout=10)
        response.raise_for_status() # Raises an exception for 4xx or 5xx errors
        data = response.json()
    except requests.RequestException as e:
        print(f"VIN Decoder API error: {e}")
        # Return a 503 error if the external service is down
        raise HTTPException(status_code=503, detail="VIN Decoder service is temporarily unavailable.")

    # NHTSA API uses 'Results' key
    results = data.get('Results', [])
    if not results or data.get('Count', 0) == 0:
        raise HTTPException(status_code=404, detail="VIN could not be decoded or is invalid.")

    # Extract required fields from the results list
    brand_name = next((item['Value'] for item in results if item['Variable'] == 'Make'), None)
    model_name = next((item['Value'] for item in results if item['Variable'] == 'Model'), None)
    year = next((item['Value'] for item in results if item['Variable'] == 'Model Year'), None)

    if not brand_name or brand_name == 'Not Applicable':
        raise HTTPException(status_code=404, detail="VIN is valid but could not determine the Brand.")

    return {
        "brand_name": brand_name,
        "model_name": model_name,
        "year": year
    }