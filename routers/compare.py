from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from routers.used_cars import get_car_with_relations, format_used_car_output
from services.AIComparision import generate_comparison_with_pdf  # keep this import as in your project

router = APIRouter(prefix="/compare", tags=["AI Comparison"])


@router.get("/")
async def compare_cars(
    car1_id: int,
    car2_id: int,
    pdf_path: str | None = None,  # now optional
    db: Session = Depends(get_db),
):
    """
    Compare two used cars by ID using an AI summary based on a PDF catalog.

    - car1_id, car2_id: IDs from the used cars table
    - pdf_path: optional override; if omitted, the service uses its DEFAULT_PDF_PATH
    """
    # Fetch cars with all relations (brand, model, categories, features)
    car1 = get_car_with_relations(db, car1_id)
    car2 = get_car_with_relations(db, car2_id)

    if not car1 or not car2:
        raise HTTPException(status_code=404, detail="Car not found")

    # Convert ORM objects → schema dicts used by the AI comparison
    car1_dict = format_used_car_output(car1).dict()
    car2_dict = format_used_car_output(car2).dict()

    # Generate AI summary (RAG over catalog PDF)
    ai_summary = await generate_comparison_with_pdf(car1_dict, car2_dict, pdf_path)

    return {
        "car1_id": car1_id,
        "car2_id": car2_id,
        "pdf_used": pdf_path,  # will be None if default was used—optional, but handy
        "ai_summary": ai_summary,
    }
