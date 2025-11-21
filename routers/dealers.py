from fastapi import APIRouter

router = APIRouter(prefix="/dealers", tags=["dealers"])

dealers_db = [
    {"id": 1, "name": "Peugeot Tunis", "location": "Cité El Intilaka, Tunis"},
    {"id": 2, "name": "Toyota Center", "location": "La Marsa, Tunis"}
]

@router.get("/")
def list_dealers():
    return dealers_db
@router.get("/{dealer_id}")
def get_dealer(dealer_id: int):
    dealer = next((d for d in dealers_db if d["id"] == dealer_id), None)
    if dealer:
        return dealer
    return {"error": "Dealer not found"}