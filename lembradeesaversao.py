import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
import pandas as pd
import os
import warnings


# Se o arquivo se chamar "logo-miceli.icon" e estiver na pasta "images"
st.set_page_config(page_title="Miceli", page_icon="images/logo-miceli.ico", layout="wide")

st.title("Acordo Eficaz")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a file",type=(["csv","txt","xlsx","xls"]))

if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_excel(filename, encoding = "ISO-8859-1")
else:
    os.chdir(r"C:\Users\fernando.lisboa\Dowmload\Dashoard Acordo Eficaz")
    df = pd.read_excel("1 Base subir template.xlsx", encoding = "ISO-8859-1")
with st.sidebar:
    selected = option_menu("Main Menu", ["Acordo Eficaz", 'Settings'], 
        icons=['house', 'gear'], menu_icon="cast", default_index=1)
    selected

# 2. horizontal menu
selected2 = option_menu(None, ["Acordo Eficaz", "Upload", "Tasks", 'Settings'], 
    icons=['house', 'cloud-upload', "list-task", 'gear'], 
    menu_icon="cast", default_index=0, orientation="horizontal")
selected2


# 3. CSS style definitions
selected3 = option_menu(None, ["Acordo Eficaz"], 
    icons=['house', 'cloud-upload', "list-task", 'gear'], 
    menu_icon="cast", default_index=0, orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "orange", "font-size": "25px"}, 
        "nav-link": {"font-size": "25px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "green"},
    }
)

# 4. Manual Item Selection
if st.session_state.get('switch_button', False):
    st.session_state['menu_option'] = (st.session_state.get('menu_option',0) + 1) % 4
    manual_select = st.session_state['menu_option']
else:
    manual_select = None
    
selected4 = option_menu(None, ["Acordo Eficaz", "Upload", "Tasks", 'Settings'], 
    icons=['house', 'cloud-upload', "list-task", 'gear'], 
    orientation="horizontal", manual_select=manual_select, key='menu_4')
st.button(f"Move to Next {st.session_state.get('menu_option',1)}", key='switch_button')
selected4

st.sidebar.header("Escolha o JUIZ")
# Escolha tipo de Réu
Juiz = st.sidebar.multiselect("Escolha JUIZ", df["Juiz do Processo"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Juiz do Processo"].isin(region)]

# Escolha Sentenca
Sentenca = st.sidebar.multiselect("Tipo de Sentenca", df2["Sentenca"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["Sentenca"].isin(state)]

# Esolha Estado OAB 
city = st.sidebar.multiselect("Estado OAB",df3["City"].unique())

# Campo para digitar o número da OAB
numero_oab = st.sidebar.text_input("Digite a OAB")

# Botão para realizar a pesquisa
if st.sidebar.button('Pesquisar'):
    # Aqui você pode adicionar a lógica de pesquisa
    # Por exemplo, filtrar o DataFrame baseado no número de OAB
    resultados_pesquisa = df3[df3['OAB'] == numero_oab]
    
    # E então mostrar os resultados da pesquisa
    st.write(resultados_pesquisa)