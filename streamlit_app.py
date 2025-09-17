import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from passenger_matcher import Location, Passenger, PassengerMatcher
from location_data import LOCATIONS, get_all_locations, search_locations

# Configuração da página
st.set_page_config(page_title="Go Together", page_icon="🚗", layout="wide")

# Destino fixo (exemplo: Insper)
FIXED_DESTINATION = Location(-23.508386086677678, -46.66748112547857, "Pro Magno Centro de Eventos")

# Inicializar session state
if 'passengers' not in st.session_state:
    st.session_state.passengers = []

def add_passenger(name, phone, origin_lat, origin_lon, origin_name, max_group_size, max_detour):
    """Adiciona novo passageiro"""
    origin = Location(origin_lat, origin_lon, origin_name)
    passenger = Passenger(name, phone, origin, FIXED_DESTINATION, max_group_size, max_detour)
    st.session_state.passengers.append(passenger)

def find_passenger_groups():
    """Encontra grupos de passageiros compatíveis"""
    if not st.session_state.passengers:
        return []
    
    groups = PassengerMatcher.find_passenger_groups(st.session_state.passengers)
    
    # Formatar resultados para exibição
    results = []
    for group in groups:
        passenger_names = [p.name for p in group['passengers']]
        origins = [p.origin.name for p in group['passengers']]
        
        results.append({
            'Grupo': ', '.join(passenger_names),
            'Tamanho': group['size'],
            'Origens': ', '.join(origins),
            'Distância Total (km)': group['total_distance_km'],
            'Custo por Pessoa (R$)': group['cost_per_person'],
            'Economia por Pessoa (R$)': group['savings_per_person'],
            'Contatos': ', '.join(group['phones'])
        })
    
    return results

# Interface principal
st.title("🚗 Go Together")
st.subheader(f"Destino fixo: {FIXED_DESTINATION.name}")
st.caption("📱 Sistema de conexão entre passageiros")

# Sidebar para cadastro
with st.sidebar:
    st.header("📝 Cadastrar Passageiro")
    
    user_name = st.text_input("Seu nome")
    phone = st.text_input("Celular", placeholder="(11) 99999-9999")
    
    st.subheader("📍 Selecionar Origem")
    
    # Método de seleção
    selection_method = st.radio(
        "Como deseja selecionar?",
        ["🔍 Buscar local", "🗺️ Usar mapa", "📋 Lista por categoria"]
    )
    
    origin_lat, origin_lon, origin_name = -23.5505, -46.6333, "Centro SP"
    
    if selection_method == "🔍 Buscar local":
        search_query = st.text_input("Digite o nome do local")
        if search_query:
            results = search_locations(search_query)
            if results:
                selected = st.selectbox(
                    "Locais encontrados:",
                    options=range(len(results)),
                    format_func=lambda i: f"{results[i]['name']} ({results[i]['category']})"
                )
                if selected is not None:
                    origin_lat, origin_lon = results[selected]['coords']
                    origin_name = results[selected]['name']
                    st.success(f"📍 {origin_name} selecionado")
            else:
                st.warning("Nenhum local encontrado")
    
    elif selection_method == "🗺️ Usar mapa":
        st.write("Clique no mapa para selecionar sua origem:")
        
        # Criar mapa centrado em SP
        m = folium.Map(location=[-23.5505, -46.6333], zoom_start=11)
        
        # Adicionar marcador do destino
        folium.Marker(
            [FIXED_DESTINATION.lat, FIXED_DESTINATION.lon],
            popup=FIXED_DESTINATION.name,
            icon=folium.Icon(color='red', icon='star')
        ).add_to(m)
        
        # Exibir mapa
        map_data = st_folium(m, width=300, height=300)
        
        # Capturar clique no mapa
        if map_data['last_clicked']:
            origin_lat = map_data['last_clicked']['lat']
            origin_lon = map_data['last_clicked']['lng']
            origin_name = f"Local ({origin_lat:.4f}, {origin_lon:.4f})"
            st.success(f"📍 Localização selecionada: {origin_lat:.4f}, {origin_lon:.4f}")
    
    elif selection_method == "📋 Lista por categoria":
        category = st.selectbox("Escolha uma categoria:", list(LOCATIONS.keys()))
        location_names = list(LOCATIONS[category].keys())
        selected_location = st.selectbox("Escolha o local:", location_names)
        
        if selected_location:
            origin_lat, origin_lon = LOCATIONS[category][selected_location]
            origin_name = selected_location
            st.success(f"📍 {origin_name} selecionado")
    
    # Mostrar coordenadas selecionadas
    st.info(f"**Local:** {origin_name}\n**Coordenadas:** {origin_lat:.4f}, {origin_lon:.4f}")
    
    st.subheader("⚙️ Preferências")
    max_group_size = st.slider("Tamanho máx do grupo", 2, 6, 4)
    max_detour = st.slider("Desvio máximo (km)", 1.0, 8.0, 3.0, 0.5)
    
    if st.button("➕ Cadastrar", type="primary"):
        if user_name and phone and origin_name:
            add_passenger(user_name, phone, origin_lat, origin_lon, origin_name, max_group_size, max_detour)
            st.success("Passageiro cadastrado!")
            st.rerun()
        else:
            st.error("Preencha nome, celular e selecione origem")

# Área principal
tab1, tab2 = st.tabs(["👥 Grupos Formados", "📋 Passageiros Cadastrados"])

with tab1:
    st.header("Grupos de Passageiros")
    
    if st.button("🔄 Atualizar Grupos", type="primary"):
        groups = find_passenger_groups()
        
        if groups:
            st.success(f"Formados {len(groups)} grupos!")
            
            for i, group in enumerate(groups, 1):
                with st.expander(f"Grupo {i} - {group['Tamanho']} pessoas (R$ {group['Custo por Pessoa (R$)']} cada)"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Participantes:** {group['Grupo']}")
                        st.write(f"**Origens:** {group['Origens']}")
                        st.write(f"**Distância:** {group['Distância Total (km)']} km")
                    
                    with col2:
                        st.write(f"**Custo por pessoa:** R$ {group['Custo por Pessoa (R$)']}")
                        st.write(f"**Economia:** R$ {group['Economia por Pessoa (R$)']}")
                        st.write(f"**Contatos:** {group['Contatos']}")
        else:
            st.info("Nenhum grupo formado ainda. Cadastre mais passageiros!")
    else:
        st.info("Clique em 'Atualizar Grupos' para formar grupos de passageiros")

with tab2:
    st.header("Passageiros Cadastrados")
    
    if st.session_state.passengers:
        passengers_data = []
        for passenger in st.session_state.passengers:
            distance = PassengerMatcher.haversine_distance(passenger.origin, FIXED_DESTINATION)
            passengers_data.append({
                'Nome': passenger.name,
                'Telefone': passenger.phone,
                'Origem': passenger.origin.name,
                'Distância (km)': round(distance, 2),
                'Grupo Máx': passenger.max_group_size,
                'Desvio Máx (km)': passenger.max_detour_km
            })
        
        df_passengers = pd.DataFrame(passengers_data)
        st.dataframe(df_passengers, use_container_width=True)
        
        if st.button("🗑️ Limpar todos os passageiros"):
            st.session_state.passengers = []
            st.rerun()
    else:
        st.info("Nenhum passageiro cadastrado ainda")

# Mapa geral na área principal
if st.session_state.passengers:
    st.markdown("---")
    st.subheader("🗺️ Mapa dos Passageiros")
    
    # Criar mapa com todos os passageiros
    map_center = [-23.5505, -46.6333]
    m = folium.Map(location=map_center, zoom_start=10)
    
    # Adicionar destino
    folium.Marker(
        [FIXED_DESTINATION.lat, FIXED_DESTINATION.lon],
        popup=f"🎯 {FIXED_DESTINATION.name}",
        icon=folium.Icon(color='red', icon='star')
    ).add_to(m)
    
    # Adicionar passageiros
    for i, passenger in enumerate(st.session_state.passengers):
        folium.Marker(
            [passenger.origin.lat, passenger.origin.lon],
            popup=f"👤 {passenger.name}\n📍 {passenger.origin.name}\n📱 {passenger.phone}",
            icon=folium.Icon(color='blue', icon='user')
        ).add_to(m)
    
    st_folium(m, width=700, height=400)

# Rodapé
st.markdown("---")
st.markdown("💡 **Como funciona**: Cadastre-se como passageiro e o sistema formará grupos otimizados. Use os contatos para se conectar com outros passageiros!")
st.markdown("📍 **Dica**: Use a busca por nome, clique no mapa ou navegue pelas categorias para encontrar sua origem facilmente.")
st.markdown(f"📊 **Total de locais disponíveis**: {len(get_all_locations())} locais em {len(LOCATIONS)} categorias")