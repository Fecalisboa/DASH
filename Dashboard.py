import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Miceli", page_icon=":bar_chart:",layout="wide")

st.title(" :bar_chart: Acordo Eficaz!!!")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a file",type=(["csv","txt","xlsx","xls"]))

if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_excel(filename, encoding = "ISO-8859-1")
else:
    os.chdir(r"C:\Users\fernando.lisboa\Dowmload\Dashoard Acordo Eficaz")
    df = pd.read_excel("1 Base subir template.xlsx", encoding = "ISO-8859-1")
    
col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])

# Getting the min and max date 
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

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

# Filter the data based on Region, State and City

if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Juiz"].isin(region)]
elif not region and not city:
    filtered_df = df[df["Sentenca"].isin(state)]
elif state and city:
    filtered_df = df3[df["Sentenca"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Juiz"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df["Juiz"].isin(region) & df3["Sentenca"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Juiz"].isin(region) & df3["Sentenca"].isin(state) & df3["City"].isin(city)]

category_df = filtered_df.groupby(by = ["Sentenca"], as_index = False)["Sales"].sum()

with col1:
    st.subheader("Sentenca")
    fig = px.bar(category_df, x = "Sentenca", y = "Instituição", text = ['${:,.2f}'.format(x) for x in category_df["Instituição"]],
                 template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)

with col2:
    st.subheader("Por assunto:")
    fig = px.pie(filtered_df, values = "Sentenca", names = "Assunto do Processo", hole = 0.5)
    fig.update_traces(text = filtered_df["Sentenca"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)

    
    
cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Sentenca"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')

with cl2:
    with st.expander("Por assunto"):
        region = filtered_df.groupby(by = "Assunto do Processo", as_index = False)["Sentenca"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Region.csv", mime = "text/csv",
                        help = 'Click here to download the data as a CSV file')

#parei aqui
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y="Sales", labels = {"Sales": "Amount"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')

# Create a treem based on Region, category, sub-Category
st.subheader("Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(filtered_df, path = ["Region","Category","Sub-Category"], values = "Sales",hover_data = ["Sales"],
                  color = "Sub-Category")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filtered_df, values = "Sales", names = "Segment", template = "plotly_dark")
    fig.update_traces(text = filtered_df["Segment"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

with chart2:
    st.subheader('Category wise Sales')
    fig = px.pie(filtered_df, values = "Sales", names = "Category", template = "gridon")
    fig.update_traces(text = filtered_df["Category"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region","State","City","Category","Sales","Profit","Quantity"]]
    fig = ff.create_table(df_sample, colorscale = "Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data = filtered_df, values = "Sales", index = ["Sub-Category"],columns = "month")
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

# Create a scatter plot
data1 = px.scatter(filtered_df, x = "Sales", y = "Profit", size = "Quantity")
data1['layout'].update(title="Relationship between Sales and Profits using Scatter Plot.",
                       titlefont = dict(size=20),xaxis = dict(title="Sales",titlefont=dict(size=19)),
                       yaxis = dict(title = "Profit", titlefont = dict(size=19)))
st.plotly_chart(data1,use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))

# Download orginal DataSet
csv = df.to_csv(index = False).encode('utf-8')
st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv")