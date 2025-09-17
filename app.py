import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
from location_data import LOCATIONS, search_locations

# Configuração da API Lambda
LAMBDA_API_URL = st.secrets.get("LAMBDA_API_URL", "https://chbqketohp4xwr64xuihvhcrq40ydpdb.lambda-url.us-east-1.on.aws")

st.set_page_config(page_title="Go Together", page_icon="🚗", layout="wide")

FIXED_DESTINATION = {"lat": -23.508386086677678, "lon": -46.66748112547857, "name": "Pro Magno Centro de Eventos"}

# Session state
if 'formed_groups' not in st.session_state:
    st.session_state.formed_groups = []
if 'pending_invites' not in st.session_state:
    st.session_state.pending_invites = []
if 'sent_invites' not in st.session_state:
    st.session_state.sent_invites = []

def call_api(method, endpoint, data=None):
    """Chama a API Lambda"""
    try:
        url = f"{LAMBDA_API_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro na API: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

def get_passengers():
    """Busca passageiros da API"""
    return call_api("GET", "/passengers") or []

def create_passenger(name, phone, origin_lat, origin_lon, origin_name, max_group_size, max_detour):
    """Cria passageiro via API"""
    data = {
        "name": name,
        "phone": phone,
        "origin": {"lat": origin_lat, "lon": origin_lon, "name": origin_name},
        "destination": FIXED_DESTINATION,
        "max_group_size": max_group_size,
        "max_detour_km": max_detour
    }
    return call_api("POST", "/passengers", data)

def find_matches(passenger_data):
    """Busca matches via API"""
    data = {"passenger": passenger_data}
    result = call_api("POST", "/find-matches", data)
    return result.get("matches", []) if result else []

# Interface
st.title("🚗 Go Together")
st.subheader(f"Destino: {FIXED_DESTINATION['name']}")
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
    
    elif selection_method == "🗺️ Usar mapa":
        st.write("Clique no mapa para selecionar sua origem:")
        
        m = folium.Map(location=[-23.5505, -46.6333], zoom_start=11)
        
        folium.Marker(
            [FIXED_DESTINATION['lat'], FIXED_DESTINATION['lon']],
            popup=FIXED_DESTINATION['name'],
            icon=folium.Icon(color='red', icon='star')
        ).add_to(m)
        
        map_data = st_folium(m, width=300, height=300, key="sidebar_map")
        
        if map_data['last_clicked']:
            st.session_state.selected_location = {
                'lat': map_data['last_clicked']['lat'],
                'lon': map_data['last_clicked']['lng'],
                'name': f"Local ({map_data['last_clicked']['lat']:.4f}, {map_data['last_clicked']['lng']:.4f})"
            }
            st.success(f"📍 Localização selecionada")
    
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
    
    st.info(f"**Local:** {st.session_state.selected_location['name']}")
    
    st.subheader("⚙️ Preferências")
    max_group_size = st.slider("Tamanho máx do grupo", 2, 6, 4)
    max_detour = st.slider("Desvio máximo (km)", 1.0, 8.0, 3.0, 0.5)
    
    if st.button("➕ Cadastrar", type="primary"):
        if user_name and phone:
            result = create_passenger(
                user_name, 
                phone, 
                st.session_state.selected_location['lat'], 
                st.session_state.selected_location['lon'], 
                st.session_state.selected_location['name'], 
                max_group_size, 
                max_detour
            )
            if result:
                st.success("Cadastrado com sucesso!")
                st.rerun()
        else:
            st.error("Preencha nome e celular!")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Encontrar Parceiros", "📨 Convites", "👥 Grupos Formados", "📋 Pessoas Cadastradas"])

with tab1:
    st.header("Encontrar Parceiros de Viagem")
    
    passengers = get_passengers()
    
    if passengers:
        user_names = [p['name'] for p in passengers]
        selected_user = st.selectbox("Selecione seu nome:", user_names)
        
        if selected_user:
            current_user_data = next((p for p in passengers if p['name'] == selected_user), None)
            
            if current_user_data:
                matches = find_matches(current_user_data)
                
                if matches:
                    st.success(f"Encontradas {len(matches)} pessoas compatíveis!")
                    
                    for match in matches:
                        with st.expander(f"👤 {match['name']} - {match['origin']['name']} ({match['distance_km']} km de você)"):
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.write(f"**Nome:** {match['name']}")
                                st.write(f"**Origem:** {match['origin']['name']}")
                                st.write(f"**Telefone:** {match['phone']}")
                                st.write(f"**Distância:** {match['distance_km']} km")
                            
                            with col2:
                                # Verificar se já enviou convite
                                invite_key = f"{selected_user}-{match['name']}"
                                already_sent = any(inv['key'] == invite_key for inv in st.session_state.sent_invites)
                                
                                if already_sent:
                                    st.info("📨 Convite enviado")
                                elif st.button(f"📨 Enviar Convite", key=f"invite_{match['name']}"):
                                    invite = {
                                        'key': invite_key,
                                        'from_user': selected_user,
                                        'to_user': match['name'],
                                        'from_phone': current_user_data['phone'],
                                        'to_phone': match['phone'],
                                        'from_origin': current_user_data['origin']['name'],
                                        'to_origin': match['origin']['name'],
                                        'distance_km': match['distance_km']
                                    }
                                    st.session_state.pending_invites.append(invite)
                                    st.session_state.sent_invites.append(invite)
                                    st.success("📨 Convite enviado! Aguarde a resposta.")
                                    st.rerun()
                else:
                    st.info("Nenhuma pessoa compatível encontrada.")
    else:
        st.info("Cadastre-se primeiro para encontrar parceiros!")

with tab2:
    st.header("📨 Convites")
    
    passengers = get_passengers()
    if passengers:
        user_names = [p['name'] for p in passengers]
        selected_user_invites = st.selectbox("Ver convites para:", user_names, key="invite_user")
        
        if selected_user_invites:
            # Convites recebidos
            received_invites = [inv for inv in st.session_state.pending_invites if inv['to_user'] == selected_user_invites]
            
            if received_invites:
                st.subheader("📨 Convites Recebidos")
                for invite in received_invites:
                    with st.expander(f"Convite de {invite['from_user']} - {invite['distance_km']} km"):
                        st.write(f"**De:** {invite['from_user']} ({invite['from_phone']})")
                        st.write(f"**Origem dele:** {invite['from_origin']}")
                        st.write(f"**Sua origem:** {invite['to_origin']}")
                        st.write(f"**Distância:** {invite['distance_km']} km")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"✅ Aceitar", key=f"accept_{invite['key']}"):
                                # Criar grupo
                                group = {
                                    'members': [invite['from_user'], invite['to_user']],
                                    'phones': [invite['from_phone'], invite['to_phone']],
                                    'origins': [invite['from_origin'], invite['to_origin']],
                                    'distance_km': invite['distance_km']
                                }
                                st.session_state.formed_groups.append(group)
                                
                                # Remover convite
                                st.session_state.pending_invites = [inv for inv in st.session_state.pending_invites if inv['key'] != invite['key']]
                                st.session_state.sent_invites = [inv for inv in st.session_state.sent_invites if inv['key'] != invite['key']]
                                
                                st.success("✅ Convite aceito! Grupo formado.")
                                st.rerun()
                        
                        with col2:
                            if st.button(f"❌ Recusar", key=f"reject_{invite['key']}"):
                                # Remover convite
                                st.session_state.pending_invites = [inv for inv in st.session_state.pending_invites if inv['key'] != invite['key']]
                                st.session_state.sent_invites = [inv for inv in st.session_state.sent_invites if inv['key'] != invite['key']]
                                
                                st.success("❌ Convite recusado.")
                                st.rerun()
            
            # Convites enviados
            sent_invites = [inv for inv in st.session_state.sent_invites if inv['from_user'] == selected_user_invites]
            
            if sent_invites:
                st.subheader("📤 Convites Enviados")
                for invite in sent_invites:
                    with st.expander(f"Para {invite['to_user']} - Aguardando resposta"):
                        st.write(f"**Para:** {invite['to_user']} ({invite['to_phone']})")
                        st.write(f"**Origem dele:** {invite['to_origin']}")
                        st.write(f"**Sua origem:** {invite['from_origin']}")
                        st.write(f"**Distância:** {invite['distance_km']} km")
                        st.info("⏳ Aguardando resposta...")
            
            if not received_invites and not sent_invites:
                st.info("Nenhum convite pendente.")
    else:
        st.info("Cadastre-se primeiro para ver convites!")

with tab3:
    st.header("Grupos Formados")
    
    if st.session_state.formed_groups:
        for i, group in enumerate(st.session_state.formed_groups, 1):
            with st.expander(f"Grupo {i} - {', '.join(group['members'])}"):
                st.write(f"**Membros:** {', '.join(group['members'])}")
                st.write(f"**Origens:** {', '.join(group['origins'])}")
                st.write(f"**Contatos:** {', '.join(group['phones'])}")
                st.write(f"**Distância:** {group['distance_km']} km")
                
                if st.button(f"🗑️ Remover Grupo {i}", key=f"remove_group_{i}"):
                    st.session_state.formed_groups.pop(i-1)
                    st.rerun()
    else:
        st.info("Nenhum grupo formado ainda.")

with tab4:
    st.header("Pessoas Cadastradas")
    
    passengers = get_passengers()
    
    if passengers:
        data = []
        for p in passengers:
            data.append({
                'Nome': p['name'],
                'Telefone': p['phone'],
                'Origem': p['origin']['name'],
                'Grupo Máx': p['max_group_size'],
                'Desvio Máx (km)': p['max_detour_km']
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
        # Mapa dos passageiros
        st.subheader("🗺️ Mapa dos Passageiros")
        
        m = folium.Map(location=[-23.5505, -46.6333], zoom_start=10)
        
        folium.Marker(
            [FIXED_DESTINATION['lat'], FIXED_DESTINATION['lon']],
            popup=f"🎯 {FIXED_DESTINATION['name']}",
            icon=folium.Icon(color='red', icon='star')
        ).add_to(m)
        
        for passenger in passengers:
            folium.Marker(
                [passenger['origin']['lat'], passenger['origin']['lon']],
                popup=f"👤 {passenger['name']}\\n📍 {passenger['origin']['name']}\\n📱 {passenger['phone']}",
                icon=folium.Icon(color='blue', icon='user')
            ).add_to(m)
        
        st_folium(m, width=700, height=400, key="main_map")
    else:
        st.info("Nenhuma pessoa cadastrada ainda")

st.markdown("---")
st.markdown("💡 **Como funciona**: Cadastre-se, encontre parceiros compatíveis e forme grupos!")
st.markdown(f"🔗 **API Status**: {LAMBDA_API_URL}")