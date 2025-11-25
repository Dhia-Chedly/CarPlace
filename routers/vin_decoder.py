from fastapi import APIRouter, Depends , UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models import Brand, Model
import pytesseract
from PIL import Image , ImageEnhance, ImageFilter
import io

router = APIRouter(prefix="/vin", tags=["VIN Decoder"])

# VIN year codes (10th character → model year)
VIN_YEAR_CODES = {
    "A": 1980, "B": 1981, "C": 1982, "D": 1983, "E": 1984, "F": 1985,
    "G": 1986, "H": 1987, "J": 1988, "K": 1989, "L": 1990, "M": 1991,
    "N": 1992, "P": 1993, "R": 1994, "S": 1995, "T": 1996, "V": 1997,
    "W": 1998, "X": 1999, "Y": 2000,
    "1": 2001, "2": 2002, "3": 2003, "4": 2004, "5": 2005, "6": 2006,
    "7": 2007, "8": 2008, "9": 2009,
    "A": 2010, "B": 2011, "C": 2012, "D": 2013, "E": 2014, "F": 2015,
    "G": 2016, "H": 2017, "J": 2018, "K": 2019, "L": 2020, "M": 2021,
    "N": 2022, "P": 2023, "R": 2024, "S": 2025
}

@router.get("/{vin}")
def decode_vin(vin: str, db: Session = Depends(get_db)):
    """
    Decode VIN → Identify brand + model from DB → Return year of fabrication
    """
    vin = vin.strip().upper()
    if len(vin) < 10:
        return {"error": "VIN must be at least 10 characters long"}

    wmi = vin[:3]   # first 3 characters → brand
    vds = vin[3:9]  # characters 4–9 → model descriptor
    year_code = vin[9]  # 10th character → year

    # --- Decode year ---
    year = VIN_YEAR_CODES.get(year_code)
    if not year:
        year = "Unknown"

    # --- Find brand by WMI in DB ---
    brand = db.query(Brand).filter(Brand.wmi == wmi).first()
    if not brand:
        return {"error": f"Brand with WMI {wmi} not found in database"}

    # --- Find model by VDS in DB ---
    model = db.query(Model).filter(
        Model.brand_id == brand.id,
        Model.vds.ilike(f"%{vds}%")
    ).first()

    if model:
        return {
            "vin": vin,
            "wmi": wmi,
            "vds": vds,
            "year_code": year_code,
            "year": year,
            "brand": brand.name,
            "model": model.name
        }

    # Fallback: return brand + all models if exact VDS not matched
    models = db.query(Model).filter(Model.brand_id == brand.id).all()
    return {
        "vin": vin,
        "wmi": wmi,
        "vds": vds,
        "year_code": year_code,
        "year": year,
        "brand": brand.name,
        "models": [m.name for m in models],
        "note": "Exact model not identified, showing all models for brand."
    }

@router.post("/scan")
async def scan_vin(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload an image containing a VIN → OCR → Decode VIN
    """
    # Read image into memory
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))

    # --- Preprocess image for better OCR ---
    image = image.convert("L")  # grayscale
    image = ImageEnhance.Contrast(image).enhance(2)  # increase contrast
    image = image.filter(ImageFilter.MedianFilter())  # reduce noise

    # Extract text using OCR
    vin_text = pytesseract.image_to_string(image).strip().upper()

    # Clean VIN (remove spaces/newlines, keep alphanumeric only)
    vin_text = "".join(c for c in vin_text if c.isalnum())

    if len(vin_text) < 10:
        return {"error": "Could not detect a valid VIN in the image", "raw_text": vin_text}

    # Reuse your existing decode function
    return decode_vin(vin_text, db)