import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from passenger_matcher import Location, Passenger, PassengerMatcher
from location_data import LOCATIONS, get_all_locations, search_locations

st.set_page_config(page_title="Go Together", page_icon="🚗", layout="wide")

FIXED_DESTINATION = Location(-23.508386086677678, -46.66748112547857, "Pro Magno Centro de Eventos")

# Session state
if 'passengers' not in st.session_state:
    st.session_state.passengers = []
if 'interests' not in st.session_state:
    st.session_state.interests = {}
if 'formed_groups' not in st.session_state:
    st.session_state.formed_groups = []

def add_passenger(name, phone, origin_lat, origin_lon, origin_name, max_group_size, max_detour):
    origin = Location(origin_lat, origin_lon, origin_name)
    passenger = Passenger(name, phone, origin, FIXED_DESTINATION, max_group_size, max_detour)
    st.session_state.passengers.append(passenger)

def find_suggestions(current_user):
    suggestions = []
    current_passenger = None
    
    for p in st.session_state.passengers:
        if p.name == current_user:
            current_passenger = p
            break
    
    if not current_passenger:
        return []
    
    for other in st.session_state.passengers:
        if other.name != current_user:
            test_group = [current_passenger, other]
            if PassengerMatcher.is_compatible_group(test_group):
                distance = PassengerMatcher.haversine_distance(current_passenger.origin, other.origin)
                suggestions.append({
                    'name': other.name,
                    'phone': other.phone,
                    'origin': other.origin.name,
                    'distance': round(distance, 2),
                    'passenger': other
                })
    
    return sorted(suggestions, key=lambda x: x['distance'])

def express_interest(from_user, to_user):
    if from_user not in st.session_state.interests:
        st.session_state.interests[from_user] = []
    if to_user not in st.session_state.interests[from_user]:
        st.session_state.interests[from_user].append(to_user)

def check_mutual_interest(user1, user2):
    interest1 = user2 in st.session_state.interests.get(user1, [])
    interest2 = user1 in st.session_state.interests.get(user2, [])
    return interest1 and interest2

def form_group(user1, user2):
    passengers = [p for p in st.session_state.passengers if p.name in [user1, user2]]
    if len(passengers) == 2:
        group_distance = PassengerMatcher.calculate_group_route_distance(passengers)
        group = {
            'members': [user1, user2],
            'distance_km': round(group_distance, 2),
            'phones': [p.phone for p in passengers],
            'origins': [p.origin.name for p in passengers]
        }
        st.session_state.formed_groups.append(group)
        
        # Limpar interesses
        for user in [user1, user2]:
            if user in st.session_state.interests:
                other = user2 if user == user1 else user1
                if other in st.session_state.interests[user]:
                    st.session_state.interests[user].remove(other)

# Interface
st.title("🚗 Go Together")
st.subheader(f"Destino: {FIXED_DESTINATION.name}")
st.caption("👥 Sistema de conexão entre passageiros")

# Sidebar
with st.sidebar:
    st.header("📝 Cadastrar-se")
    
    user_name = st.text_input("Seu nome")
    phone = st.text_input("Celular", placeholder="(11) 99999-9999")
    
    st.subheader("📍 Selecionar Origem")
    
    selection_method = st.radio(
        "Como deseja selecionar?",
        ["🔍 Buscar local", "🗺️ Usar mapa", "📋 Lista por categoria"]
    )
    
    if 'selected_location' not in st.session_state:
        st.session_state.selected_location = {
            'lat': -23.5505,
            'lon': -46.6333,
            'name': 'Centro SP'
        }
    
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
                    st.session_state.selected_location = {
                        'lat': results[selected]['coords'][0],
                        'lon': results[selected]['coords'][1],
                        'name': results[selected]['name']
                    }
                    st.success(f"📍 {results[selected]['name']} selecionado")
            else:
                st.warning("Nenhum local encontrado")
    
    elif selection_method == "🗺️ Usar mapa":
        st.write("Clique no mapa para selecionar sua origem:")
        
        m = folium.Map(location=[-23.5505, -46.6333], zoom_start=11)
        
        folium.Marker(
            [FIXED_DESTINATION.lat, FIXED_DESTINATION.lon],
            popup=FIXED_DESTINATION.name,
            icon=folium.Icon(color='red', icon='star')
        ).add_to(m)
        
        map_data = st_folium(m, width=300, height=300, key="sidebar_map")
        
        if map_data['last_clicked']:
            st.session_state.selected_location = {
                'lat': map_data['last_clicked']['lat'],
                'lon': map_data['last_clicked']['lng'],
                'name': f"Local ({map_data['last_clicked']['lat']:.4f}, {map_data['last_clicked']['lng']:.4f})"
            }
            st.success(f"📍 Localização selecionada: {st.session_state.selected_location['lat']:.4f}, {st.session_state.selected_location['lon']:.4f}")
    
    elif selection_method == "📋 Lista por categoria":
        category = st.selectbox("Escolha uma categoria:", list(LOCATIONS.keys()))
        location_names = list(LOCATIONS[category].keys())
        selected_location = st.selectbox("Escolha o local:", location_names)
        
        if selected_location:
            lat, lon = LOCATIONS[category][selected_location]
            st.session_state.selected_location = {
                'lat': lat,
                'lon': lon,
                'name': selected_location
            }
            st.success(f"📍 {selected_location} selecionado")
    
    st.info(f"**Local:** {st.session_state.selected_location['name']}\n**Coordenadas:** {st.session_state.selected_location['lat']:.4f}, {st.session_state.selected_location['lon']:.4f}")
    
    st.subheader("⚙️ Preferências")
    max_group_size = st.slider("Tamanho máx do grupo", 2, 6, 4)
    max_detour = st.slider("Desvio máximo (km)", 1.0, 8.0, 3.0, 0.5)
    
    if st.button("➕ Cadastrar", type="primary"):
        if user_name and phone:
            existing = [p for p in st.session_state.passengers if p.name == user_name]
            if not existing:
                add_passenger(
                    user_name, 
                    phone, 
                    st.session_state.selected_location['lat'], 
                    st.session_state.selected_location['lon'], 
                    st.session_state.selected_location['name'], 
                    max_group_size, 
                    max_detour
                )
                st.success("Cadastrado com sucesso!")
                st.rerun()
            else:
                st.error("Nome já existe!")
        else:
            st.error("Preencha nome e celular!")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔍 Encontrar Parceiros", "💬 Meus Interesses", "👥 Grupos Formados", "📋 Pessoas Cadastradas", "✏️ Editar Dados"])

with tab1:
    st.header("Encontrar Parceiros de Viagem")
    
    if st.session_state.passengers:
        user_names = [p.name for p in st.session_state.passengers]
        selected_user = st.selectbox("Selecione seu nome:", user_names)
        
        if selected_user:
            suggestions = find_suggestions(selected_user)
            
            if suggestions:
                st.success(f"Encontradas {len(suggestions)} pessoas compatíveis!")
                
                for suggestion in suggestions:
                    with st.expander(f"👤 {suggestion['name']} - {suggestion['origin']} ({suggestion['distance']} km de você)"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Nome:** {suggestion['name']}")
                            st.write(f"**Origem:** {suggestion['origin']}")
                            st.write(f"**Telefone:** {suggestion['phone']}")
                            st.write(f"**Distância entre origens:** {suggestion['distance']} km")
                        
                        with col2:
                            already_interested = suggestion['name'] in st.session_state.interests.get(selected_user, [])
                            
                            if already_interested:
                                if check_mutual_interest(selected_user, suggestion['name']):
                                    st.success("🎉 Interesse mútuo!")
                                    if st.button(f"Formar grupo", key=f"form_{suggestion['name']}"):
                                        form_group(selected_user, suggestion['name'])
                                        st.success("Grupo formado!")
                                        st.rerun()
                                else:
                                    st.success("✅ Interesse enviado!")
                            else:
                                if st.button(f"💚 Tenho interesse", key=f"int_{suggestion['name']}"):
                                    express_interest(selected_user, suggestion['name'])
                                    st.success("Interesse enviado!")
                                    st.rerun()
            else:
                st.info("Nenhuma pessoa compatível encontrada.")
    else:
        st.info("Cadastre-se primeiro para encontrar parceiros!")

with tab2:
    st.header("Meus Interesses")
    
    if st.session_state.passengers:
        user_names = [p.name for p in st.session_state.passengers]
        selected_user = st.selectbox("Ver interesses de:", user_names, key="int_user")
        
        if selected_user:
            sent = st.session_state.interests.get(selected_user, [])
            if sent:
                st.subheader("💚 Interesses enviados:")
                for person in sent:
                    st.write(f"• {person}")
            
            received = [user for user, interests in st.session_state.interests.items() 
                       if selected_user in interests]
            
            if received:
                st.subheader("💌 Interesses recebidos:")
                for person in received:
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"• {person}")
                    with col2:
                        if st.button(f"Aceitar", key=f"acc_{person}"):
                            express_interest(selected_user, person)
                            form_group(selected_user, person)
                            st.success("Grupo formado!")
                            st.rerun()
            
            if not sent and not received:
                st.info("Nenhum interesse ainda.")

with tab3:
    st.header("Grupos Formados")
    
    if st.session_state.formed_groups:
        for i, group in enumerate(st.session_state.formed_groups, 1):
            with st.expander(f"Grupo {i} - {', '.join(group['members'])}"):
                st.write(f"**Membros:** {', '.join(group['members'])}")
                st.write(f"**Origens:** {', '.join(group['origins'])}")
                st.write(f"**Contatos:** {', '.join(group['phones'])}")
                st.write(f"**Distância total:** {group['distance_km']} km")
    else:
        st.info("Nenhum grupo formado ainda.")

with tab4:
    st.header("Pessoas Cadastradas")
    
    if st.session_state.passengers:
        data = []
        for p in st.session_state.passengers:
            distance = PassengerMatcher.haversine_distance(p.origin, FIXED_DESTINATION)
            data.append({
                'Nome': p.name,
                'Telefone': p.phone,
                'Origem': p.origin.name,
                'Distância (km)': round(distance, 2),
                'Grupo Máx': p.max_group_size,
                'Desvio Máx (km)': p.max_detour_km
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
        if st.button("🗑️ Limpar todos os passageiros"):
            st.session_state.passengers = []
            st.session_state.interests = {}
            st.session_state.formed_groups = []
            st.rerun()
    else:
        st.info("Nenhuma pessoa cadastrada ainda")

with tab5:
    st.header("✏️ Editar Meus Dados")
    
    if st.session_state.passengers:
        user_names = [p.name for p in st.session_state.passengers]
        selected_user = st.selectbox("Selecione seu nome para editar:", user_names, key="edit_user")
        
        if selected_user:
            current_passenger = None
            for p in st.session_state.passengers:
                if p.name == selected_user:
                    current_passenger = p
                    break
            
            if current_passenger:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Dados atuais:**")
                    st.write(f"Nome: {current_passenger.name}")
                    st.write(f"Telefone: {current_passenger.phone}")
                    st.write(f"Origem: {current_passenger.origin.name}")
                    st.write(f"Grupo máx: {current_passenger.max_group_size}")
                    st.write(f"Desvio máx: {current_passenger.max_detour_km} km")
                
                with col2:
                    st.write("**Novos dados:**")
                    
                    new_name = st.text_input("Novo nome:", value=current_passenger.name)
                    new_phone = st.text_input("Novo telefone:", value=current_passenger.phone)
                    
                    edit_method = st.radio(
                        "Alterar localização?",
                        ["📍 Manter atual", "🔍 Buscar", "📋 Categoria"]
                    )
                    
                    new_lat, new_lon, new_location_name = current_passenger.origin.lat, current_passenger.origin.lon, current_passenger.origin.name
                    
                    if edit_method == "🔍 Buscar":
                        search_edit = st.text_input("Buscar novo local:")
                        if search_edit:
                            results = search_locations(search_edit)
                            if results:
                                selected_edit = st.selectbox(
                                    "Locais encontrados:",
                                    options=range(len(results)),
                                    format_func=lambda i: f"{results[i]['name']}"
                                )
                                if selected_edit is not None:
                                    new_lat, new_lon = results[selected_edit]['coords']
                                    new_location_name = results[selected_edit]['name']
                    
                    elif edit_method == "📋 Categoria":
                        edit_category = st.selectbox("Categoria:", list(LOCATIONS.keys()))
                        edit_locations = list(LOCATIONS[edit_category].keys())
                        edit_location = st.selectbox("Local:", edit_locations)
                        
                        if edit_location:
                            new_lat, new_lon = LOCATIONS[edit_category][edit_location]
                            new_location_name = edit_location
                    
                    new_max_group = st.slider("Novo tamanho máx do grupo:", 2, 6, current_passenger.max_group_size)
                    new_max_detour = st.slider("Novo desvio máx (km):", 1.0, 8.0, current_passenger.max_detour_km, 0.5)
                    
                    st.info(f"Nova localização: {new_location_name}")
                
                col1_btn, col2_btn = st.columns(2)
                
                with col1_btn:
                    if st.button("✅ Salvar Alterações", type="primary"):
                        if new_name and new_phone:
                            name_exists = any(p.name == new_name for p in st.session_state.passengers if p.name != selected_user)
                            
                            if not name_exists:
                                for i, p in enumerate(st.session_state.passengers):
                                    if p.name == selected_user:
                                        new_origin = Location(new_lat, new_lon, new_location_name)
                                        updated_passenger = Passenger(new_name, new_phone, new_origin, FIXED_DESTINATION, new_max_group, new_max_detour)
                                        st.session_state.passengers[i] = updated_passenger
                                        
                                        if selected_user != new_name:
                                            if selected_user in st.session_state.interests:
                                                st.session_state.interests[new_name] = st.session_state.interests.pop(selected_user)
                                            
                                            for user, interests in st.session_state.interests.items():
                                                if selected_user in interests:
                                                    interests.remove(selected_user)
                                                    interests.append(new_name)
                                            
                                            for group in st.session_state.formed_groups:
                                                if selected_user in group['members']:
                                                    group['members'] = [new_name if m == selected_user else m for m in group['members']]
                                        break
                                
                                st.success("Dados atualizados!")
                                st.rerun()
                            else:
                                st.error("Nome já existe!")
                        else:
                            st.error("Preencha nome e telefone!")
                
                with col2_btn:
                    if st.button("🗑️ Excluir Cadastro"):
                        st.session_state.passengers = [p for p in st.session_state.passengers if p.name != selected_user]
                        
                        if selected_user in st.session_state.interests:
                            del st.session_state.interests[selected_user]
                        
                        for user, interests in st.session_state.interests.items():
                            if selected_user in interests:
                                interests.remove(selected_user)
                        
                        st.session_state.formed_groups = [g for g in st.session_state.formed_groups if selected_user not in g['members']]
                        
                        st.success("Cadastro excluído!")
                        st.rerun()
    else:
        st.info("Nenhuma pessoa cadastrada para editar.")

# Mapa geral
if st.session_state.passengers:
    st.markdown("---")
    st.subheader("🗺️ Mapa dos Passageiros")
    
    map_center = [-23.5505, -46.6333]
    m = folium.Map(location=map_center, zoom_start=10)
    
    folium.Marker(
        [FIXED_DESTINATION.lat, FIXED_DESTINATION.lon],
        popup=f"🎯 {FIXED_DESTINATION.name}",
        icon=folium.Icon(color='red', icon='star')
    ).add_to(m)
    
    for passenger in st.session_state.passengers:
        folium.Marker(
            [passenger.origin.lat, passenger.origin.lon],
            popup=f"👤 {passenger.name}\n📍 {passenger.origin.name}\n📱 {passenger.phone}",
            icon=folium.Icon(color='blue', icon='user')
        ).add_to(m)
    
    st_folium(m, width=700, height=400, key="main_map")

st.markdown("---")
st.markdown("💡 **Como funciona**: Cadastre-se, encontre parceiros, demonstre interesse e forme grupos!")
st.markdown("📍 **Dica**: Use a busca, mapa ou categorias para encontrar sua origem facilmente.")
st.markdown(f"📊 **Total de locais disponíveis**: {len(get_all_locations())} locais em {len(LOCATIONS)} categorias")