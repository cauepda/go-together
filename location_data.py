"""
Dados de localizações populares em São Paulo
"""

# Localizações organizadas por categoria
LOCATIONS = {
    "Estações de Metrô": {
        "Sé": (-23.5505, -46.6333),
        "República": (-23.5475, -46.6361),
        "Anhangabaú": (-23.5458, -46.6339),
        "Consolação": (-23.5558, -46.6396),
        "Paulista": (-23.5567, -46.6622),
        "Faria Lima": (-23.5781, -46.6925),
        "Vila Madalena": (-23.5629, -46.6544),
        "Pinheiros": (-23.5617, -46.7017),
        "Morumbi": (-23.6033, -46.7019),
        "Butantã": (-23.5717, -46.7236),
        "Cidade Universitária": (-23.5586, -46.7311),
        "Vila Olímpia": (-23.5986, -46.6731),
        "Berrini": (-23.6108, -46.6944),
        "Brooklin": (-23.6147, -46.6875),
        "Santo Amaro": (-23.6528, -46.7081)
    },
    "Bairros Centrais": {
        "Centro": (-23.5505, -46.6333),
        "Liberdade": (-23.5583, -46.6347),
        "Bela Vista": (-23.5558, -46.6396),
        "Santa Cecília": (-23.5361, -46.6500),
        "Higienópolis": (-23.5444, -46.6556),
        "Pacaembu": (-23.5361, -46.6667)
    },
    "Zona Oeste": {
        "Vila Madalena": (-23.5629, -46.6544),
        "Pinheiros": (-23.5617, -46.7017),
        "Perdizes": (-23.5361, -46.6889),
        "Lapa": (-23.5278, -46.7056),
        "Pompéia": (-23.5278, -46.6889),
        "Barra Funda": (-23.5194, -46.6556)
    },
    "Zona Sul": {
        "Vila Olímpia": (-23.5986, -46.6731),
        "Itaim Bibi": (-23.5889, -46.6778),
        "Moema": (-23.6000, -46.6556),
        "Ibirapuera": (-23.5917, -46.6556),
        "Brooklin": (-23.6147, -46.6875),
        "Campo Belo": (-23.6167, -46.6667),
        "Santo Amaro": (-23.6528, -46.7081)
    },
    "Zona Norte": {
        "Santana": (-23.5056, -46.6278),
        "Tucuruvi": (-23.4806, -46.6056),
        "Vila Guilherme": (-23.4944, -46.6056),
        "Casa Verde": (-23.5056, -46.6556)
    },
    "Zona Leste": {
        "Tatuapé": (-23.5361, -46.5778),
        "Mooca": (-23.5583, -46.6056),
        "Vila Prudente": (-23.5889, -46.5889),
        "São Mateus": (-23.6167, -46.4778)
    },
    "Universidades": {
        "USP - Cidade Universitária": (-23.5586, -46.7311),
        "Insper - Vila Olímpia": (-23.5986, -46.6731),
        "FGV - Bela Vista": (-23.5558, -46.6396),
        "Mackenzie - Higienópolis": (-23.5444, -46.6556),
        "PUC-SP - Perdizes": (-23.5361, -46.6889),
        "ESPM - Vila Olímpia": (-23.5986, -46.6731)
    }
}

def get_all_locations():
    """Retorna todas as localizações em uma lista plana"""
    all_locations = {}
    for category, locations in LOCATIONS.items():
        for name, coords in locations.items():
            all_locations[name] = coords
    return all_locations

def search_locations(query):
    """Busca localizações por nome"""
    query = query.lower()
    results = []
    
    for category, locations in LOCATIONS.items():
        for name, coords in locations.items():
            if query in name.lower():
                results.append({
                    'name': name,
                    'category': category,
                    'coords': coords
                })
    
    return results