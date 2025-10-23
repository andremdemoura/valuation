import streamlit as st
import pandas as pd
import plotly.express as px

# --- FUNÇÃO DE VALUATION OTIMIZADA PARA STREAMLIT ---
# (Removidos os 'print' e ajustado o retorno)
def calcular_valuation_completo(lucro_inicial, taxa_crescimento_proj, taxa_desconto, anos_projecao, taxa_crescimento_perpetuo):
    # Condição de erro: retorna valores que podem ser tratados pela interface
    if taxa_desconto <= taxa_crescimento_perpetuo:
        return 0, 0, 0, []

    # Parte 1: Cálculo do Período de Projeção
    detalhes_projecao = []
    vp_total_projecao = 0
    lucro_projetado = lucro_inicial

    for ano in range(1, anos_projecao + 1):
        lucro_projetado *= (1 + taxa_crescimento_proj)
        valor_presente_lucro = lucro_projetado / ((1 + taxa_desconto) ** ano)
        vp_total_projecao += valor_presente_lucro
        
        detalhes_projecao.append({
            "Ano": ano,
            "Lucro Projetado": lucro_projetado,
            "Valor Presente": valor_presente_lucro
        })
    
    # Parte 2: Cálculo da Perpetuidade
    ultimo_lucro_projetado = lucro_projetado
    lucro_ano_perpetuidade = ultimo_lucro_projetado * (1 + taxa_crescimento_perpetuo)
    valor_na_perpetuidade = lucro_ano_perpetuidade / (taxa_desconto - taxa_crescimento_perpetuo)
    vp_perpetuidade = valor_na_perpetuidade / ((1 + taxa_desconto) ** anos_projecao)

    # Parte 3: Resultado Final
    valuation_total = vp_total_projecao + vp_perpetuidade

    return valuation_total, vp_total_projecao, vp_perpetuidade, detalhes_projecao

# --- INTERFACE DO DASHBOARD ---

# Configuração da página
st.set_page_config(
    layout="wide",
    page_title="Calculadora de Valuation Simplificada",
    page_icon="💼"
)

# --- Barra Lateral para Inputs ---
with st.sidebar:
    st.image("https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png", width=200)
    st.title("⚙️ Premissas do Valuation")
    st.markdown("Insira os dados para calcular o valuation.")

    st.header("Dados Atuais")
    lucro_base_anual = st.number_input("Lucro Líquido do Último Ano (R$)", min_value=0, value=500000, step=10000)

    st.header("Premissas de Projeção")
    crescimento_projecao_perc = st.slider("Crescimento do Lucro (% a.a.)", 0.0, 30.0, 5.0, 0.5)
    periodo_em_anos = st.slider("Anos de Projeção", 3, 15, 5)
    
    st.header("Premissas de Desconto")
    taxa_de_desconto_perc = st.slider("Taxa de Desconto (WACC) (%)", 5.0, 25.0, 18.0, 0.5)
    crescimento_perpetuo_perc = st.slider("Crescimento na Perpetuidade (%)", 0.0, 5.0, 2.0, 0.1)

# --- Página Principal para Resultados ---
st.title("💰 Resultado do Valuation")
st.markdown("---")

# Executa o cálculo com os inputs da barra lateral (convertendo % para decimal)
valuation_final, vp_projecao, vp_perpetuidade, projecao_detalhada = calcular_valuation_completo(
    lucro_inicial=lucro_base_anual,
    taxa_crescimento_proj=crescimento_projecao_perc / 100,
    taxa_desconto=taxa_de_desconto_perc / 100,
    anos_projecao=periodo_em_anos,
    taxa_crescimento_perpetuo=crescimento_perpetuo_perc / 100
)

# Verifica se o cálculo é válido antes de exibir os resultados
if valuation_final <= 0:
    st.error("ERRO: A Taxa de Desconto deve ser maior que o Crescimento na Perpetuidade. Por favor, ajuste as premissas na barra lateral.")
else:
    # 1. Métrica Principal: O Valuation Total
    st.header("Valor Total Estimado da Empresa:")
    st.metric(label="", value=f"R$ {valuation_final:,.2f}")

    # 2. Gráfico de Composição do Valor
    st.subheader("Composição do Valor")
    df_composicao = pd.DataFrame({
        'Componente': ['Valor da Projeção Explícita', 'Valor da Perpetuidade'],
        'Valor': [vp_projecao, vp_perpetuidade]
    })
    fig = px.pie(df_composicao, values='Valor', names='Componente',
                 title='De onde vem o valor?', hole=.3,
                 color_discrete_sequence=px.colors.sequential.GnBu_r)
    fig.update_traces(textinfo='percent+label', pull=[0, 0.05])
    st.plotly_chart(fig, use_container_width=True)

    # 3. Tabela com a Projeção Ano a Ano
    st.subheader("Projeção de Lucros e Valor Presente")
    df_para_exibir = pd.DataFrame(projecao_detalhada)
    st.dataframe(df_para_exibir.style.format({
        "Lucro Projetado": "R$ {:,.2f}",
        "Valor Presente": "R$ {:,.2f}"
    }))

st.markdown("---")
st.caption("Esta é uma calculadora simplificada para fins educacionais e de demonstração.")