from fastapi import FastAPI, HTTPException
from mangum import Mangum
from pydantic import BaseModel
from typing import List, Optional
import json

app = FastAPI(title="Go Together API")

# Dados em memória
routes_data = []

class Location(BaseModel):
    lat: float
    lon: float
    name: str

class Passenger(BaseModel):
    name: str
    phone: str
    origin: Location
    destination: Location
    max_group_size: int
    max_detour_km: float

class MatchRequest(BaseModel):
    passenger: Passenger

@app.get("/")
def root():
    return {"message": "Go Together API funcionando!", "passengers": len(routes_data)}

@app.post("/passengers")
def create_passenger(passenger: Passenger):
    # Verificar se já existe
    existing = [p for p in routes_data if p["name"] == passenger.name]
    if existing:
        raise HTTPException(status_code=400, detail="Passageiro já existe")
    
    routes_data.append(passenger.dict())
    return {"message": "Passageiro cadastrado", "total": len(routes_data)}

@app.get("/passengers")
def get_passengers():
    return routes_data

@app.post("/find-matches")
def find_matches(request: MatchRequest):
    current = request.passenger
    matches = []
    
    for other_data in routes_data:
        if other_data["name"] != current.name:
            # Calcular distância entre origens
            distance = haversine_distance(
                current.origin.lat, current.origin.lon,
                other_data["origin"]["lat"], other_data["origin"]["lon"]
            )
            
            # Verificar compatibilidade básica
            if distance <= min(current.max_detour_km, other_data["max_detour_km"]):
                matches.append({
                    "name": other_data["name"],
                    "phone": other_data["phone"],
                    "origin": other_data["origin"],
                    "distance_km": round(distance, 2)
                })
    
    return {"matches": sorted(matches, key=lambda x: x["distance_km"])}

@app.delete("/passengers")
def clear_passengers():
    routes_data.clear()
    return {"message": "Passageiros limpos"}

@app.delete("/passengers/{name}")
def delete_passenger(name: str):
    global routes_data
    routes_data = [p for p in routes_data if p["name"] != name]
    return {"message": f"Passageiro {name} removido"}

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calcula distância entre dois pontos usando fórmula de Haversine"""
    import math
    
    R = 6371  # Raio da Terra em km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lon / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

# Handler para Lambda
handler = Mangum(app)