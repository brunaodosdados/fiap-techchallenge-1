# Comando para ativar o ambiente virtual:
# .\venv\Scripts/activate

# Comando para abrir o dashboard do Streamlit:
# streamlit run Relatório_interativo.py

# Importando bibliotecas
import streamlit as st
import pandas as pd
import plotly.express as px

## Configurações do aplicativo do Streamlit
st.set_page_config(layout='wide')

## Título
st.title('DASHBOARD - EXPORTAÇÃO DE VINHOS BRASILEIROS')

## Importando dados

### Exportação de vinhos
url_exportacao = 'https://raw.githubusercontent.com/brunaodosdados/fiap-techchallenge-1/refs/heads/main/dados/dados_tratados/exportacao_vinhos.csv'
df_exportacao = pd.read_csv(url_exportacao)

### Produção de vinhos
url_producao = 'https://raw.githubusercontent.com/brunaodosdados/fiap-techchallenge-1/refs/heads/main/dados/dados_tratados/producao_vinhos.csv'
df_producao = pd.read_csv(url_producao)

## Tratativas nos dados
def formata_numero(valor, prefixo = ''):
    for unidade in ['','mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'


## Sidebar com filtros
st.sidebar.title('Filtros')

### Filtro de data
filtro_data = st.sidebar.slider('Período',value=[df_exportacao['ano'].min(),df_exportacao['ano'].max()],min_value=df_exportacao['ano'].min(), max_value=df_exportacao['ano'].max())
df_exportacao = df_exportacao[(df_exportacao['ano'] >= filtro_data[0]) & (df_exportacao['ano'] <= filtro_data[1])]

### Filtro de continentes
filtro_paises = st.sidebar.checkbox('Selecionar todos os continentes',value=True)
if filtro_paises:
    continentes = st.sidebar.multiselect('Continentes',df_exportacao['Continente'].unique(),df_exportacao['Continente'].unique())
    df_exportacao = df_exportacao[df_exportacao['Continente'].isin(continentes)]
else:
    continentes = st.sidebar.multiselect('Continentes',df_exportacao['Continente'].unique())
    df_exportacao = df_exportacao[df_exportacao['Continente'].isin(continentes)]

### Filtro de países
filtro_paises = st.sidebar.checkbox('Selecionar todos os países',value=True)
if filtro_paises:
    paises = st.sidebar.multiselect('Países',df_exportacao['País'].unique(),df_exportacao['País'].unique())
    df_exportacao = df_exportacao[df_exportacao['País'].isin(paises)]
else:
    paises = st.sidebar.multiselect('Países',df_exportacao['País'].unique())
    df_exportacao = df_exportacao[df_exportacao['País'].isin(paises)]

## Tabelas

### Dados de exportação

receita_anual = df_exportacao.groupby('ano')['valor'].sum().reset_index(name='Receita')
receita_por_pais = df_exportacao.groupby('País')['valor'].sum().reset_index(name='Receita').sort_values('Receita',ascending=True)
quantidade_anual = df_exportacao.groupby('ano')['quantidade'].sum().reset_index(name='Quantidade (Litros)')
quantidade_por_pais = df_exportacao.groupby('País')['quantidade'].sum().reset_index(name='Quantidade (Litros)').sort_values('Quantidade (Litros)',ascending=True)

tabela_mapa = df_exportacao.groupby(['País','latitude','longitude'])['valor'].sum().reset_index()

tabela_stacked_receita = df_exportacao.copy()
tabela_stacked_receita['Países'] = tabela_stacked_receita.apply(lambda x: x['País'] if x['valor_pct'] > 1 else 'Outros', axis=1)
tabela_stacked_receita = tabela_stacked_receita.groupby(['Países','ano'])['valor_pct'].sum().reset_index(name='Representatividade_valor')

tabela_stacked_receita_continentes = df_exportacao.copy()
# tabela_stacked_receita_continentes['Países'] = tabela_stacked_receita_continentes.apply(lambda x: x['País'] if x['valor_pct'] > 1 else 'Outros', axis=1)
tabela_stacked_receita_continentes = tabela_stacked_receita_continentes.groupby(['Continente','ano'])['valor_pct'].sum().reset_index(name='Representatividade_valor')

# tabela_stacked_quantidade = df_exportacao.copy()
# tabela_stacked_quantidade['Países'] = tabela_stacked_quantidade.apply(lambda x: x['País'] if x['quantidade_pct'] > 1 else 'Outros', axis=1)
# tabela_stacked_quantidade = tabela_stacked_quantidade.groupby(['Países','ano'])['quantidade_pct'].sum().reset_index(name='Representatividade_quant')

tabela_consolidada = pd.merge(quantidade_por_pais,receita_por_pais,how='left',on='País')
tabela_consolidada.sort_values('Quantidade (Litros)', ascending=False, inplace=True)
tabela_consolidada['País de origem'] = 'Brasil'
tabela_consolidada.rename(columns={'País':'País destino da exportação','Receita':'Receita (US$)'},inplace=True)
tabela_consolidada = tabela_consolidada[['País de origem','País destino da exportação','Quantidade (Litros)','Receita (US$)']]
tabela_consolidada = tabela_consolidada.reset_index().drop('index',axis=1)

### Dados de produção

# exportacao_por_ano = df_exportacao.groupby('ano')['quantidade'].sum().reset_index(name='quantidade_exportada')
# producao_vinho = df_producao[df_producao['produto'] == 'VINHO DE MESA']
# producao_vinho = producao_vinho.merge(exportacao_por_ano,on='ano',how='left')

## Gráficos

### Exportação de vinhos
fig_receita_anual = px.line(receita_anual,
                             x='ano',
                             y='Receita',
                             markers=True,
                             hover_data={'Receita':':.0f'},
                             range_y=(0,receita_anual.max()),
                             title='Receita por ano (US$)'
                            )
fig_receita_anual.update_yaxes(rangemode="tozero")

fig_quantidade_anual = px.line(quantidade_anual,
                             x='ano',
                             y='Quantidade (Litros)',
                             markers=True,
                             hover_data={'Quantidade (Litros)':':.0f'},
                             range_y=(0,receita_anual.max()),
                             title='Quantidade em litros por ano'
                            )
fig_quantidade_anual.update_yaxes(rangemode="tozero")

fig_receita_paises = px.bar(receita_por_pais.tail(10),
                             x='Receita',
                             y='País',
                            #  text_auto=True,
                             title='Top 10 países (Receita em US$)',
                             text_auto='.3s',
                             hover_data={'Receita':':.0f'}
                            )

fig_quantidade_paises = px.bar(quantidade_por_pais.tail(10),
                             x='Quantidade (Litros)',
                             y='País',
                            #  text_auto=True,
                             title='Top 10 países (Quantidade em litros)',
                             text_auto='.3s',
                             hover_data={'Quantidade (Litros)':':.0f'}
                            )

fig_mapa = px.scatter_geo(tabela_mapa,
                                       lat='latitude',
                                       lon='longitude',
                                       size='valor',
                                       template='seaborn',
                                       hover_name='País',
                                       hover_data={'latitude':False,'longitude':False},
                                       title='Vinhos exportados por país'
                            )
fig_mapa.update_layout(
    autosize=False,
    width=1024,
    height=576,
)

fig_stacked_receita = px.bar(tabela_stacked_receita,
                      x='ano',
                      y='Representatividade_valor',
                      color='Países',
                      title='Representatividade de receita de exportação por país',
                      hover_data={'Representatividade_valor':':.1f'},
                      labels={'valor': 'Valor (em unidades monetárias)', 'ano': 'Ano'},
                    #   color_discrete_sequence=px.colors.qualitative.Bold,
             barmode='stack')

fig_stacked_receita_continentes = px.bar(tabela_stacked_receita_continentes,
                      x='ano',
                      y='Representatividade_valor',
                      color='Continente',
                      title='Representatividade de receita de exportação por continentes',
                      hover_data={'Representatividade_valor':':.1f'},
                      labels={'valor': 'Valor (em unidades monetárias)', 'ano': 'Ano'},
                    #   color_discrete_sequence=px.colors.qualitative.Bold,
             barmode='stack')

### Produção de vinhos
# fig_producao_por_ano = px.line(producao_vinho,
#                              x='ano',
#                              y='quantidade',
#                              markers=True,
#                              hover_data={'quantidade':':.0f'},
#                              range_y=(0,producao_vinho['quantidade'].max()*1.2),
#                              title='Quantidade em litros produzida por ano'
#                             )
# fig_producao_por_ano.update_yaxes(rangemode="tozero")

# fig_exportacao_por_ano = px.line(producao_vinho,
#                              x='ano',
#                              y='quantidade_exportada',
#                              markers=True,
#                              hover_data={'quantidade':':.0f'},
#                              range_y=(0,producao_vinho['quantidade_exportada'].max()*1.2),
#                              title='Quantidade em litros exportada por ano'
#                             )
# fig_exportacao_por_ano.update_yaxes(rangemode="tozero")

## Visualizações do aplicativo

aba1,aba2 = st.tabs(['Exportação','Tabela - Dados de exportação consolidados'])

with aba1:

    coluna1, coluna2, coluna3 = st.columns(3)

    with coluna1:
        st.metric('Quantidade',formata_numero(df_exportacao['quantidade'].sum()))
    with coluna2:
        st.metric('Valor em US$',formata_numero(df_exportacao['valor'].sum(),'US$'))  
    with coluna3:
        st.metric('Países que compram vinho brasileiro',df_exportacao['País'].nunique())
    
    
    coluna1 = st.columns(1)
    st.plotly_chart(fig_mapa, use_container_width=False)

    coluna1, coluna2 = st.columns(2)
    with coluna1:
        # st.metric('Quantidade',formata_numero(df_exportacao['quantidade'].sum()))
        st.plotly_chart(fig_receita_paises, use_container_width=True)
        st.plotly_chart(fig_quantidade_paises, use_container_width=True)

    with coluna2:
        # st.metric('Valor em US$',formata_numero(df_exportacao['valor'].sum(),'US$'))
        st.plotly_chart(fig_receita_anual, use_container_width=True)
        st.plotly_chart(fig_quantidade_anual, use_container_width=True)

    st.plotly_chart(fig_stacked_receita_continentes)

    st.plotly_chart(fig_stacked_receita)

# st.dataframe(df_exportacao)

    # st.dataframe(receita_por_pais)

# with aba2:
    
#     st.metric('Quantidade de vinho produzida',formata_numero(producao_vinho['quantidade'].sum()))

#     # coluna1, coluna2 = st.columns(2)    
#     # with coluna1:
#     st.plotly_chart(fig_producao_por_ano, use_container_width=True)

#     # with coluna2:
#     st.plotly_chart(fig_exportacao_por_ano, use_container_width=True)



with aba2:

    st.dataframe(tabela_consolidada.set_index(tabela_consolidada.columns[0]))
