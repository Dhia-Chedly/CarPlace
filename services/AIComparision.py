from transformers import pipeline

generator = pipeline("text-generation", model="EleutherAI/gpt-neo-1.3B", device=0)
def generate_comparison(car1: dict, car2: dict) -> str:
    prompt = (
        "Compare the following two cars objectively in 2 sentences. Do not give personal opinions.\n\n"
        f"Car 1 Characteristics:\n"
        f"- Brand: {car1['brand_name']}\n"
        f"- Model: {car1['model_name']}\n"
        f"- Year: {car1['year']}\n"
        f"- Horsepower: {car1['horsepower']} HP\n"
        f"- Price: ${car1['price']}\n"
        f"- Mileage: {car1['mileage']} km\n"
        f"- Fuel: {car1['fuel_type']}\n"
        f"- Transmission: {car1['transmission']}\n"
        f"- Features: {', '.join([f['name'] for f in car1['features']])}\n\n"
        
        f"Car 2 Characteristics:\n"
        f"- Brand: {car2['brand_name']}\n"
        f"- Model: {car2['model_name']}\n"
        f"- Year: {car2['year']}\n"
        f"- Horsepower: {car2['horsepower']} HP\n"
        f"- Price: ${car2['price']}\n"
        f"- Mileage: {car2['mileage']} km\n"
        f"- Fuel: {car2['fuel_type']}\n"
        f"- Transmission: {car2['transmission']}\n"
        f"- Features: {', '.join([f['name'] for f in car2['features']])}\n\n"
       
    )

    result = generator(prompt, max_length=60, num_return_sequences=1)
    summary = result[0]["generated_text"]
    return summary