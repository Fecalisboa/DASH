import streamlit as st
import pandas as pd
import io  # Adicione esta linha no início do seu script
import random


# CSS para estilizar os expanders
expander_bar_css = """
<style>
div.st-Expander {
    border: 2px solid rgba(28, 131, 225, 0.1);
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 10px;
}
div.st-Expander > label {
    font-weight: 500;
    font-size: 16px;
    color: rgba(30, 103, 119, 1);
}
</style>
"""

# # Injetando o CSS com st.markdown
# st.markdown(expander_bar_css, unsafe_allow_html=True)
# Configuração da página
st.set_page_config(page_title="Miceli", page_icon="images/logo-miceli.ico", layout="wide")

st.title("Acordo Eficaz")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# Carrega a planilha automaticamente
nome_do_arquivo = "base.xlsx"  # Altere para o nome do seu arquivo Excel

try:
    # Convertendo a coluna OAB para string no momento do carregamento
    df = pd.read_excel(nome_do_arquivo, engine='openpyxl', dtype={'OAB': str})
    # Removendo vírgulas que possam existir na coluna OAB
    df['OAB'] = df['OAB'].str.replace(',', '')
except FileNotFoundError:
    st.error(f"O arquivo {nome_do_arquivo} não foi encontrado no diretório do projeto.")
    st.stop()

# Função para verificar se o número da OAB existe no DataFrame
def pesquisa_oab(numero_oab, oab_estado):
    # Removendo vírgulas do número inserido pelo usuário, caso existam
    numero_oab = numero_oab.replace(',', '')
    return df[(df['OAB'] == numero_oab) & (df['Estado OAB'] == oab_estado)]

def obter_media_dano_moral(resultados_pesquisa):
    # Supondo que a coluna 'Média DM' contém a média pré-calculada de Dano Moral para cada OAB
    if 'Média DM' in resultados_pesquisa.columns:
        # Supõe-se que há apenas uma linha por OAB, então pegue o primeiro valor encontrado
        return resultados_pesquisa['Média DM'].iloc[0]
    else:
        return None

# Função para calcular as estrelas baseada na coluna 'JULGO PROCEDENTE'
def calcular_estrelas_por_julgo_procedente(resultados_pesquisa):
    procedentes_count = resultados_pesquisa['JULGO PROCEDENTE'].str.contains("procedente", case=False, na=False).sum()
    total_count = resultados_pesquisa['JULGO PROCEDENTE'].notna().sum()
    proporcao_procedentes = procedentes_count / total_count if total_count else 0
    estrelas = round(proporcao_procedentes * 5)
    return estrelas, proporcao_procedentes

# Função para verificar a litigância de má-fé
def verificar_litigancia(resultados_pesquisa):
    if resultados_pesquisa['Sentenca'].str.contains("Litigância", case=False, na=False).any():
        return "Litigância de Má Fé encontrada nos processos."
    else:
        return "Litigância de Má Fé não encontrada nos processos."

# Função para obter o nome do advogado da coluna 'Advogado'
def obter_nome_advogado(resultados_pesquisa):
    # Verifica se existe a coluna 'Advogado' e se ela não está vazia
    if 'Advogado' in resultados_pesquisa.columns and not resultados_pesquisa['Advogado'].isnull().all():
        # Pega o primeiro nome de advogado encontrado (supondo que cada OAB tem um advogado único)
        return resultados_pesquisa['Advogado'].dropna().iloc[0]
    else:
        return "Não disponível"

# Função para limpar e converter os valores monetários para float
def limpar_valor_monetario(valor):
    if isinstance(valor, str):
        # Remover o símbolo da moeda e substituir vírgula por ponto
        valor = valor.replace('R$', '').replace('.', '').replace(',', '.').strip()
    try:
        return float(valor)
    except ValueError:  # Se a conversão falhar, retorne None ou 0
        return None

# Função para calcular a média de 'Valor de Ação' por 'Sentenca'
def calcular_media_valor_acao_por_sentenca(resultados_pesquisa):
    resultados_pesquisa['Valor da Ação Limpo'] = resultados_pesquisa['Valor da Ação'].apply(limpar_valor_monetario)
    media_por_sentenca = resultados_pesquisa.groupby('Sentenca')['Valor da Ação Limpo'].mean().reset_index()
    return media_por_sentenca

# Função para calcular a média de 'Valor de Ação' por 'Instituição'
def calcular_media_valor_acao_por_instituicao(resultados_pesquisa):
    resultados_pesquisa['Valor da Ação Limpo'] = resultados_pesquisa['Valor da Ação'].apply(limpar_valor_monetario)
    media_por_instituicao = resultados_pesquisa.groupby('Instituição')['Valor da Ação Limpo'].mean().reset_index()
    return media_por_instituicao

# Aplicar a função para a coluna 'Valor de Ação' antes de calcular a média
df['Valor da Ação'] = df['Valor da Ação'].apply(limpar_valor_monetario)

with st.sidebar:
    selected = option_menu(
        menu_title="Menu",
        options=["Acordo Eficaz", "IA Acordo Eficaz"],
        icons=["house", "book"],
        menu_icon="cast",
        default_index=0,
    )

    # Mostra as opções de acordo com o que foi selecionado no menu da barra lateral
    if selected == "Acordo Eficaz":
        # Expander para ocultar/mostrar a pesquisa OAB
        with st.sidebar.expander("Pesquisa OAB"):
            oab_estado = st.selectbox("Escolha o Estado da OAB", ['', 'SP', 'RJ', 'MG', 'ES'])
            numero_oab = st.text_input("Digite a OAB", max_chars=10)
            pesquisar_button = st.button('Pesquisar OAB')

    # Se o usuário clicar no botão de pesquisa e os campos estiverem preenchidos, faz a pesquisa
    if selected == "Acordo Eficaz" and pesquisar_button:
        numero_oab = numero_oab.replace(',', '').strip()
        resultados_pesquisa = pesquisa_oab(numero_oab, oab_estado)
        if not resultados_pesquisa.empty:
            # Ações a serem tomadas após encontrar resultados
            st.session_state['resultados_pesquisa'] = resultados_pesquisa
            st.success("OAB encontrada!")
        else:
            st.error("OAB Não encontrada!")


    if selected == "IA Acordo Eficaz":
        with st.sidebar:
            # File uploader permite ao usuário carregar o arquivo .xlsx
            uploaded_file_ia = st.file_uploader("Carregue a planilha IA", type='xlsx')
            if uploaded_file_ia:
                try:
                    # Processamento do arquivo IA
                    df_ia_acordo_eficaz = pd.read_excel(uploaded_file_ia, engine='openpyxl')
                    st.success("Planilha IA Acordo Eficaz carregada com sucesso!")
                    # Agora df_ia_acordo_eficaz é o DataFrame do arquivo carregado
                    # Implemente qualquer processamento ou filtragem necessária aqui
                except Exception as e:
                    st.error(f"Erro ao processar a planilha IA: {e}")

if 'resultados_pesquisa' in st.session_state:
    resultados_pesquisa = st.session_state['resultados_pesquisa']

    if not resultados_pesquisa.empty:
        st.success("OAB encontrada!")
        quantidade_processos = len(resultados_pesquisa)
        
        # Chame a função obter_nome_advogado para obter o nome do advogado
        nome_advogado = obter_nome_advogado(resultados_pesquisa)
        
        st.write(f"Quantidade de processos encontrados: {quantidade_processos}")
        st.write(f"Advogado: {nome_advogado}")

        # Cálculo da média de Dano Moral
        # Chama a função para calcular a média de Dano Moral
        # Calcula a média de Dano Moral
        media_dano_moral = obter_media_dano_moral(resultados_pesquisa)
        
        
        
        estrelas, proporcao_procedentes = calcular_estrelas_por_julgo_procedente(resultados_pesquisa)

        col1, col2, col3 = st.columns(3)
        with col1:
            if media_dano_moral is not None:
                st.write(f"Média de Dano Moral: R$ {media_dano_moral}")
            else:
                st.write("Média de Dano Moral não disponível.")
        with col2:
            st.write(f"Classificação: {'⭐' * estrelas} ({proporcao_procedentes:.0%} de sucesso)")
        with col3:
            mensagem_litigancia = verificar_litigancia(resultados_pesquisa)
            st.write(mensagem_litigancia)

        st.markdown("---")
   
        # Preparando os dados para os gráficos
        sentenca_counts = resultados_pesquisa['Sentenca'].value_counts()
        instituicao_counts = resultados_pesquisa['Instituição'].value_counts()

        # Layout para os gráficos lado a lado
        grafico_col1, grafico_col2 = st.columns(2)
        
        with grafico_col1:
            # Gráfico de pizza para a coluna Sentença
            fig_pizza = px.pie(
                values=sentenca_counts.values, 
                names=sentenca_counts.index, 
                title='Sentenças', 
                hole=0.5
            )
            fig_pizza.update_traces(textinfo='percent+label+value')
            st.plotly_chart(fig_pizza, use_container_width=True)

        with grafico_col2:
            # Gráfico de barras para a coluna Instituição
            fig_barra = px.bar(
                x=instituicao_counts.index, 
                y=instituicao_counts.values, 
                text=instituicao_counts.values,
                title='Tipo Réu'
            )
            fig_barra.update_traces(texttemplate='%{text}', textposition='outside')
            st.plotly_chart(fig_barra, use_container_width=True)
        
        st.markdown("---")

        # Certifique-se de limpar os valores antes de fazer o cálculo das médias
        resultados_pesquisa['Valor da Ação Limpo'] = resultados_pesquisa['Valor da Ação'].apply(limpar_valor_monetario)

        # Agora é seguro calcular a média, pois 'Valor de Ação' é numérico
        media_valor_acao_por_sentenca = calcular_media_valor_acao_por_sentenca(resultados_pesquisa)
        media_valor_acao_por_instituicao = calcular_media_valor_acao_por_instituicao(resultados_pesquisa)

        # ... (código anterior) ...

        graficos_media_col1, graficos_media_col2 = st.columns(2)

        with graficos_media_col1:
            # Gráfico da média do valor de ação por sentença
            if not media_valor_acao_por_sentenca.empty:
                fig_media_sentenca = px.bar(
                    media_valor_acao_por_sentenca, 
                    x='Sentenca', 
                    y='Valor da Ação Limpo',  # Aqui você usa a coluna correta
                    title='Média de Valor da Ação por Sentença'
                )
                fig_media_sentenca.update_traces(texttemplate='%{y:.2f}', textposition='outside')
                st.plotly_chart(fig_media_sentenca, use_container_width=True)
            else:
                st.write("Não há dados suficientes para exibir a média de Valor de Ação por Sentença.")

        with graficos_media_col2:
            # Gráfico da média do valor de ação por instituição
            if not media_valor_acao_por_instituicao.empty:
                fig_media_instituicao = px.bar(
                    media_valor_acao_por_instituicao, 
                    x='Instituição', 
                    y='Valor da Ação Limpo',  # E aqui também
                    title='Média de Valor de Ação por Instituição'
                )
                fig_media_instituicao.update_traces(texttemplate='%{y:.2f}', textposition='outside')
                st.plotly_chart(fig_media_instituicao, use_container_width=True)
            else:
                st.write("Não há dados suficientes para exibir a média de Valor de Ação por Instituição.")
        st.markdown("---")

     # Contando as ocorrências de cada 'Assunto do Processo'
    contagem_assuntos = resultados_pesquisa['Assunto do Processo'].value_counts().reset_index()
    contagem_assuntos.columns = ['Assunto do Processo', 'Contagem']  # Renomeando colunas para clareza

    # Criação do gráfico de barras horizontais com a contagem em cada barra
    fig_assunto_processo = px.bar(
        contagem_assuntos, 
        x='Contagem', 
        y='Assunto do Processo', 
        orientation='h', 
        title='Contagem por Assunto do Processo',
        text='Contagem'  # Isso adiciona a contagem em cada barra
    )
    fig_assunto_processo.update_traces(texttemplate='%{text}', textposition='inside')  # Configura a posição do texto
    fig_assunto_processo.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_assunto_processo, use_container_width=True)

    # Caixa de seleção para escolher o formato de saída
    formato_saida = st.selectbox('Escolha o formato de saída:', [ 'PDF'])
    if st.button('Download Relatório'):
        if formato_saida == 'PDF':
            # Converter o DataFrame para HTML e depois para PDF
            html = resultados_pesquisa.to_html(index=False)
            pdf = pdfkit.from_string(html, False)
            st.download_button(
                label='Baixar PDF',
                data=pdf,
                file_name='resultados_pesquisa.pdf',
                mime='application/pdf'
            )
        elif formato_saida == 'Excel':
            # Código para criar e baixar como Excel
            towrite = io.BytesIO()
            resultados_pesquisa.to_excel(towrite, index=False, sheet_name='Resultados')
            towrite.seek(0)
            st.download_button(
                label='Baixar Excel',
                data=towrite,
                file_name='resultados_pesquisa.xlsx',
                mime='application/vnd.ms-excel'
            )
