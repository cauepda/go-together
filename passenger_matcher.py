import math
from typing import List, Dict, Optional
from datetime import datetime
from mcp_aws_pricing import AWSPricingMCP

class Location:
    def __init__(self, lat: float, lon: float, name: str = ""):
        self.lat = lat
        self.lon = lon
        self.name = name

class Passenger:
    def __init__(self, name: str, phone: str, origin: Location, destination: Location, 
                 max_group_size: int = 4, max_detour_km: float = 3.0):
        self.name = name
        self.phone = phone
        self.origin = origin
        self.destination = destination
        self.max_group_size = max_group_size
        self.max_detour_km = max_detour_km
        self.registered_at = datetime.now()

class PassengerMatcher:
    @staticmethod
    def haversine_distance(loc1: Location, loc2: Location) -> float:
        """Calcula distância em km entre duas coordenadas"""
        R = 6371
        
        lat1, lon1 = math.radians(loc1.lat), math.radians(loc1.lon)
        lat2, lon2 = math.radians(loc2.lat), math.radians(loc2.lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c

    @staticmethod
    def calculate_group_route_distance(passengers: List[Passenger]) -> float:
        """Calcula distância total da rota do grupo"""
        if len(passengers) <= 1:
            return PassengerMatcher.haversine_distance(passengers[0].origin, passengers[0].destination)
        
        # Rota: origem mais distante → outras origens → destino
        origins = [p.origin for p in passengers]
        destination = passengers[0].destination  # Destino fixo
        
        # Encontrar origem mais distante do destino
        farthest_origin = max(origins, key=lambda o: PassengerMatcher.haversine_distance(o, destination))
        other_origins = [o for o in origins if o != farthest_origin]
        
        # Calcular rota otimizada
        total_distance = 0
        current_location = farthest_origin
        
        # Visitar outras origens na ordem mais próxima
        remaining_origins = other_origins.copy()
        while remaining_origins:
            nearest = min(remaining_origins, key=lambda o: PassengerMatcher.haversine_distance(current_location, o))
            total_distance += PassengerMatcher.haversine_distance(current_location, nearest)
            current_location = nearest
            remaining_origins.remove(nearest)
        
        # Ir para o destino
        total_distance += PassengerMatcher.haversine_distance(current_location, destination)
        
        return total_distance

    @staticmethod
    def is_compatible_group(passengers: List[Passenger]) -> bool:
        """Verifica se passageiros podem formar um grupo"""
        if len(passengers) <= 1:
            return True
        
        # Verificar se todos têm o mesmo destino
        destinations = set((p.destination.lat, p.destination.lon) for p in passengers)
        if len(destinations) > 1:
            return False
        
        # Verificar tamanho do grupo
        max_size = min(p.max_group_size for p in passengers)
        if len(passengers) > max_size:
            return False
        
        # Verificar desvio máximo para cada passageiro
        group_distance = PassengerMatcher.calculate_group_route_distance(passengers)
        
        for passenger in passengers:
            solo_distance = PassengerMatcher.haversine_distance(passenger.origin, passenger.destination)
            detour = group_distance - solo_distance
            
            if detour > passenger.max_detour_km:
                return False
        
        return True

    @staticmethod
    def find_passenger_groups(passengers: List[Passenger]) -> List[Dict]:
        """Encontra grupos compatíveis de passageiros"""
        groups = []
        used_passengers = set()
        aws_pricing = AWSPricingMCP()
        
        for i, passenger in enumerate(passengers):
            if passenger.name in used_passengers:
                continue
            
            # Tentar formar grupos de diferentes tamanhos
            for group_size in range(min(passenger.max_group_size, len(passengers) - i), 0, -1):
                potential_group = [passenger]
                
                # Adicionar passageiros compatíveis
                for other in passengers[i+1:]:
                    if (other.name not in used_passengers and 
                        len(potential_group) < group_size):
                        
                        test_group = potential_group + [other]
                        if PassengerMatcher.is_compatible_group(test_group):
                            potential_group.append(other)
                
                # Se encontrou um grupo válido
                if len(potential_group) >= 1:
                    group_distance = PassengerMatcher.calculate_group_route_distance(potential_group)
                    
                    # Calcular custos (estimativa de R$ 1.50/km)
                    total_cost = group_distance * 1.5
                    cost_per_person = total_cost / len(potential_group)
                    
                    # Calcular economia média
                    solo_costs = [PassengerMatcher.haversine_distance(p.origin, p.destination) * 1.5 
                                 for p in potential_group]
                    avg_solo_cost = sum(solo_costs) / len(solo_costs)
                    savings_per_person = max(0, avg_solo_cost - cost_per_person)
                    
                    # Calcular custos AWS por grupo
                    aws_costs = aws_pricing.calculate_cost_per_passenger_group(len(potential_group))
                    
                    groups.append({
                        'passengers': potential_group,
                        'size': len(potential_group),
                        'total_distance_km': round(group_distance, 2),
                        'cost_per_person': round(cost_per_person, 2),
                        'savings_per_person': round(savings_per_person, 2),
                        'phones': [p.phone for p in potential_group],
                        'aws_cost_per_passenger_usd': aws_costs['aws_cost_per_passenger_usd'],
                        'aws_cost_per_match_usd': aws_costs['aws_cost_per_match_usd']
                    })
                    
                    # Marcar passageiros como usados
                    for p in potential_group:
                        used_passengers.add(p.name)
                    break
        
        # Ordenar por economia
        groups.sort(key=lambda x: x['savings_per_person'], reverse=True)
        return groups