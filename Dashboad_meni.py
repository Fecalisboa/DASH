import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
import pandas as pd
import os
import warnings
import openpyxl

# Configuração da página
st.set_page_config(page_title="Miceli", page_icon="images/logo-miceli.ico", layout="wide")


st.title("Acordo Eficaz")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)



# Carrega a planilha automaticamente
nome_do_arquivo = "base.xlsx"  # Altere para o nome do seu arquivo Excel

try:
    df = pd.read_excel(nome_do_arquivo, engine='openpyxl')
except FileNotFoundError:
    st.error(f"O arquivo {nome_do_arquivo} não foi encontrado no diretório do projeto.")
    st.stop()


# Menu lateral para escolher entre 'Acordo Eficaz' e 'IA Acordo Eficaz'
menu_option = st.sidebar.selectbox("Escolha uma opção", ["Acordo Eficaz", "IA Acordo Eficaz"])

# Verifica qual opção foi escolhida e exibe os filtros correspondentes
if menu_option == "Acordo Eficaz":
    st.sidebar.header("Filtros de Pesquisa Acordo Eficaz")


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

    if selected4 == "Acordo Eficaz":
        # Aqui dentro você coloca todos os seus filtros e a lógica de pesquisa
        st.sidebar.header("Filtros de Pesquisa")
        
        # Verifica se a coluna 'Juiz do Processo' existe
        if 'Juiz do Processo' in df.columns:
            juiz = st.sidebar.multiselect("Escolha JUIZ", df["Juiz do Processo"].unique())
            if juiz:
                df = df[df["Juiz do Processo"].isin(juiz)]
        
        # Verifica se a coluna 'Sentenca' existe
        if 'Sentenca' in df.columns:
            sentenca = st.sidebar.multiselect("Tipo de Sentença", df["Sentenca"].unique())
            if sentenca:
                df = df[df["Sentenca"].isin(sentenca)]

        # Verifica se a coluna 'Estado OAB' existe
        if 'Estado OAB' in df.columns:
            oab_estado = st.sidebar.multiselect("Estado OAB", df["Estado OAB"].unique())
        
        # Campo para digitar o número da OAB
        numero_oab = st.sidebar.text_input("Digite a OAB")
        
        # Botão para realizar a pesquisa
        if st.sidebar.button('Pesquisar'):
            # Filtrar DataFrame baseado no número de OAB
            resultados_pesquisa = df[df['OAB'] == numero_oab]
            # Mostrar os resultados da pesquisa
            st.write(resultados_pesquisa)

        # Se nenhum filtro for aplicado, mostrar DataFrame inteiro
        if not (juiz or sentenca or oab_estado or numero_oab):
            st.dataframe(df)

elif menu_option == "IA Acordo Eficaz":
    st.sidebar.header("Filtros de Pesquisa IA Acordo Eficaz")