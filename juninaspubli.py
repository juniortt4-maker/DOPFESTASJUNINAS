import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import unicodedata
import re

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================

st.set_page_config(
    page_title="OPERAÇÃO - SÃO JOÃO 2026",
    page_icon="🚔",
    layout="wide"
)

st.title("🚔 OPERAÇÃO - SÃO JOÃO 2026")

# =========================================================
# ESTILO
# =========================================================

st.markdown("""
<style>

.stApp {
    background: #0B0F14;
}

h1, h2, h3 {
    color: #E5E7EB;
}

.stCaption {
    color: #94A3B8 !important;
}

div[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #1F2937;
    padding: 15px;
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# URL DA PLANILHA
# =========================================================

url = (
    "https://docs.google.com/spreadsheets/d/"
    "1U2re0vGfssfUAFzra2oJoIVp4klRsbkpWBXVXSFd2Rs/"
    "export?format=csv&gid=1866688086"
)

# =========================================================
# PALETAS
# =========================================================

PALETA_BARRAS = [
    "#5B8FF9",
    "#61DDAA",
    "#65789B",
    "#F6BD16",
    "#7262FD",
    "#78D3F8",
    "#9661BC",
    "#F6903D",
    "#008685",
    "#F08BB4"
]

PALETA_PIZZA = [
    "#5B8FF9",
    "#61DDAA",
    "#F6BD16",
    "#7262FD",
    "#F08BB4",
    "#78D3F8"
]

# =========================================================
# FUNÇÕES
# =========================================================

def normalizar_texto(texto):
    texto = str(texto).strip().upper()
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8")
    texto = re.sub(r"\s+", " ", texto)
    return texto

@st.cache_data(ttl=60)
def carregar_dados():
    df = pd.read_csv(url)
    df = df.dropna(how="all")
    df.columns = [c.strip() for c in df.columns]
    return df

def localizar_coluna(colunas, termos):

    for termo in termos:

        termo_norm = normalizar_texto(termo)

        for coluna in colunas:

            if termo_norm in normalizar_texto(coluna):
                return coluna

    return None

def converter_numero(valor):

    if pd.isna(valor):
        return pd.NA

    valor = str(valor).strip()

    if valor == "":
        return pd.NA

    valor = valor.replace(".", "")
    valor = valor.replace(",", ".")

    valor = re.sub(r"[^0-9.-]", "", valor)

    try:
        return float(valor)
    except:
        return pd.NA

def aplicar_estilo(fig):

    fig.update_layout(
        template="simple_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(size=13),
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig

# =========================================================
# INÍCIO
# =========================================================

try:

    df = carregar_dados()

    horario = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    st.sidebar.success("🟢 DASHBOARD ONLINE")
    st.sidebar.info(f"ATUALIZADO EM:\n{horario}")

    # =====================================================
    # IDENTIFICAR COLUNAS
    # =====================================================

    colunas = df.columns.tolist()

    coluna_comando = localizar_coluna(colunas, ["COMANDO"])
    coluna_cidade = localizar_coluna(colunas, ["CIDADE", "MUNICIPIO"])
    coluna_evento = localizar_coluna(colunas, ["EVENTO"])
    coluna_publico = localizar_coluna(colunas, ["PUBLICO"])
    coluna_data = localizar_coluna(colunas, ["DATA"])
    coluna_natureza = localizar_coluna(colunas, ["NATUREZA"])
    coluna_tipo_publico = localizar_coluna(colunas, ["TIPO DE PUBLICO"])
    coluna_cobranca = localizar_coluna(colunas, ["COBRANÇA", "COBRANCA"])

    # =====================================================
    # TRATAMENTO
    # =====================================================

    if coluna_publico:

        df[coluna_publico] = df[coluna_publico].apply(converter_numero)

        df[coluna_publico] = pd.to_numeric(
            df[coluna_publico],
            errors="coerce"
        )

    if coluna_data:

        df[coluna_data] = pd.to_datetime(
            df[coluna_data],
            errors="coerce",
            dayfirst=True
        )

        df["ANO"] = df[coluna_data].dt.year
        df["MES"] = df[coluna_data].dt.month

        mapa_meses = {
            1: "JAN",
            2: "FEV",
            3: "MAR",
            4: "ABR",
            5: "MAI",
            6: "JUN",
            7: "JUL",
            8: "AGO",
            9: "SET",
            10: "OUT",
            11: "NOV",
            12: "DEZ"
        }

        df["MES_NOME"] = df["MES"].map(mapa_meses)

    # =====================================================
    # FILTROS
    # =====================================================

    st.sidebar.subheader("🎯 FILTROS")

    df_filtrado = df.copy()

    # FILTRO ANO

    if "ANO" in df_filtrado.columns:

        anos = sorted(
            df_filtrado["ANO"]
            .dropna()
            .astype(int)
            .unique()
            .tolist()
        )

        anos_sel = st.sidebar.multiselect(
            "FILTRAR ANO",
            options=anos,
            default=[]
        )

        if anos_sel:

            df_filtrado = df_filtrado[
                df_filtrado["ANO"].isin(anos_sel)
            ]

    # FILTRO COMANDO

    if coluna_comando:

        comandos = sorted(
            df_filtrado[coluna_comando]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        comandos_sel = st.sidebar.multiselect(
            "FILTRAR COMANDO",
            options=comandos,
            default=[]
        )

        if comandos_sel:

            df_filtrado = df_filtrado[
                df_filtrado[coluna_comando]
                .astype(str)
                .isin(comandos_sel)
            ]

    # FILTRO CIDADE

    if coluna_cidade:

        cidades = sorted(
            df_filtrado[coluna_cidade]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        cidades_sel = st.sidebar.multiselect(
            "FILTRAR CIDADE",
            options=cidades,
            default=[]
        )

        if cidades_sel:

            df_filtrado = df_filtrado[
                df_filtrado[coluna_cidade]
                .astype(str)
                .isin(cidades_sel)
            ]

    # FILTRO NATUREZA

    if coluna_natureza:

        natureza = sorted(
            df_filtrado[coluna_natureza]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        natureza_sel = st.sidebar.multiselect(
            "FILTRAR NATUREZA",
            options=natureza,
            default=[]
        )

        if natureza_sel:

            df_filtrado = df_filtrado[
                df_filtrado[coluna_natureza]
                .astype(str)
                .isin(natureza_sel)
            ]

    # FILTRO TIPO PÚBLICO

    if coluna_tipo_publico:

        tipos = sorted(
            df_filtrado[coluna_tipo_publico]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        tipos_sel = st.sidebar.multiselect(
            "FILTRAR TIPO PÚBLICO",
            options=tipos,
            default=[]
        )

        if tipos_sel:

            df_filtrado = df_filtrado[
                df_filtrado[coluna_tipo_publico]
                .astype(str)
                .isin(tipos_sel)
            ]

    # FILTRO EVENTO

    if coluna_evento:

        eventos = sorted(
            df_filtrado[coluna_evento]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        eventos_sel = st.sidebar.multiselect(
            "FILTRAR EVENTO",
            options=eventos,
            default=[]
        )

        if eventos_sel:

            df_filtrado = df_filtrado[
                df_filtrado[coluna_evento]
                .astype(str)
                .isin(eventos_sel)
            ]

    # FILTRO COBRANÇA

    if coluna_cobranca:

        cobrancas = sorted(
            df_filtrado[coluna_cobranca]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        cobrancas_sel = st.sidebar.multiselect(
            "FILTRAR COBRANÇA",
            options=cobrancas,
            default=[]
        )

        if cobrancas_sel:

            df_filtrado = df_filtrado[
                df_filtrado[coluna_cobranca]
                .astype(str)
                .isin(cobrancas_sel)
            ]

    # FILTRO PÚBLICO

    if coluna_publico and df_filtrado[coluna_publico].notna().any():

        publico_min = int(df_filtrado[coluna_publico].min())
        publico_max = int(df_filtrado[coluna_publico].max())

        faixa_publico = st.sidebar.slider(
            "FILTRAR PÚBLICO PREVISTO",
            min_value=publico_min,
            max_value=publico_max,
            value=(publico_min, publico_max)
        )

        df_filtrado = df_filtrado[
            (df_filtrado[coluna_publico] >= faixa_publico[0]) &
            (df_filtrado[coluna_publico] <= faixa_publico[1])
        ]

    # FILTRO DATA

    if coluna_data and df_filtrado[coluna_data].notna().any():

        data_min = df_filtrado[coluna_data].min().date()
        data_max = df_filtrado[coluna_data].max().date()

        periodo = st.sidebar.date_input(
            "FILTRAR PERÍODO",
            value=(data_min, data_max),
            min_value=data_min,
            max_value=data_max
        )

        if isinstance(periodo, tuple) and len(periodo) == 2:

            inicio, fim = periodo

            df_filtrado = df_filtrado[
                (df_filtrado[coluna_data].dt.date >= inicio) &
                (df_filtrado[coluna_data].dt.date <= fim)
            ]

    # PESQUISA GLOBAL

    pesquisa_sidebar = st.sidebar.text_input(
        "🔎 PESQUISA GLOBAL"
    )

    if pesquisa_sidebar:

        df_filtrado = df_filtrado[
            df_filtrado.astype(str)
            .apply(
                lambda x: x.str.contains(
                    pesquisa_sidebar,
                    case=False,
                    na=False
                )
            )
            .any(axis=1)
        ]

    # =====================================================
    # INDICADORES
    # =====================================================

    st.subheader("📌 INDICADORES OPERACIONAIS")

    total_eventos = len(df_filtrado)

    total_publico = int(
        df_filtrado[coluna_publico]
        .fillna(0)
        .sum()
    ) if coluna_publico else 0

    total_cidades = (
        df_filtrado[coluna_cidade]
        .nunique()
    ) if coluna_cidade else 0

    total_comandos = (
        df_filtrado[coluna_comando]
        .nunique()
    ) if coluna_comando else 0

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🎉 EVENTOS", total_eventos)
    c2.metric("👥 PÚBLICO", f"{total_publico:,}".replace(",", "."))
    c3.metric("🏙️ CIDADES", total_cidades)
    c4.metric("🚔 COMANDOS", total_comandos)

    # =====================================================
    # COMPARATIVO ANO/MÊS
    # =====================================================

    if "ANO" in df_filtrado.columns and "MES_NOME" in df_filtrado.columns:

        st.subheader("📅 COMPARATIVO ANO/MÊS")

        comparativo = (
            df_filtrado
            .groupby(["ANO", "MES", "MES_NOME"])
            .size()
            .reset_index(name="EVENTOS")
            .sort_values(["ANO", "MES"])
        )

        fig = px.bar(
            comparativo,
            x="MES_NOME",
            y="EVENTOS",
            color="ANO",
            barmode="group",
            text_auto=True,
            color_discrete_sequence=PALETA_BARRAS
        )

        fig = aplicar_estilo(fig)

        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # EVENTOS POR COMANDO
    # =====================================================

    if coluna_comando:

        st.subheader("🚔 EVENTOS POR COMANDO")

        dados = (
            df_filtrado
            .groupby(coluna_comando)
            .size()
            .reset_index(name="EVENTOS")
            .sort_values(by="EVENTOS", ascending=False)
        )

        fig = px.bar(
            dados,
            x=coluna_comando,
            y="EVENTOS",
            color=coluna_comando,
            text_auto=True,
            color_discrete_sequence=PALETA_BARRAS
        )

        fig.update_layout(showlegend=False)

        fig = aplicar_estilo(fig)

        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # EVENTOS POR CIDADE
    # =====================================================

    if coluna_cidade:

        st.subheader("🏙️ CIDADES COM MAIS EVENTOS")

        cidades = (
            df_filtrado
            .groupby(coluna_cidade)
            .size()
            .reset_index(name="EVENTOS")
            .sort_values(by="EVENTOS", ascending=False)
            .head(15)
        )

        fig = px.bar(
            cidades,
            x=coluna_cidade,
            y="EVENTOS",
            color=coluna_cidade,
            text_auto=True,
            color_discrete_sequence=PALETA_BARRAS
        )

        fig.update_layout(showlegend=False)

        fig = aplicar_estilo(fig)

        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # EVENTOS COM MAIOR PÚBLICO
    # =====================================================

    if coluna_evento and coluna_publico:

        st.subheader("🎯 EVENTOS COM MAIOR PÚBLICO PREVISTO")

        eventos_publico = (
            df_filtrado
            .groupby(coluna_evento)[coluna_publico]
            .sum()
            .reset_index()
            .sort_values(by=coluna_publico, ascending=False)
            .head(10)
        )

        fig = px.bar(
            eventos_publico,
            x=coluna_evento,
            y=coluna_publico,
            color=coluna_evento,
            text_auto=".2s",
            color_discrete_sequence=PALETA_BARRAS
        )

        fig.update_layout(showlegend=False)

        fig = aplicar_estilo(fig)

        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # DISTRIBUIÇÃO PÚBLICO
    # =====================================================

    if coluna_publico:

        st.subheader("📊 DISTRIBUIÇÃO DO PÚBLICO PREVISTO")

        fig = px.histogram(
            df_filtrado,
            x=coluna_publico,
            nbins=20
        )

        fig = aplicar_estilo(fig)

        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # EVOLUÇÃO PÚBLICO
    # =====================================================

    if coluna_data and coluna_publico:

        st.subheader("📈 EVOLUÇÃO DO PÚBLICO")

        evolucao = (
            df_filtrado
            .groupby(coluna_data)[coluna_publico]
            .sum()
            .reset_index()
            .sort_values(coluna_data)
        )

        fig = px.line(
            evolucao,
            x=coluna_data,
            y=coluna_publico,
            markers=True
        )

        fig = aplicar_estilo(fig)

        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # TOP 10
    # =====================================================

    if coluna_publico:

        st.subheader("🔥 TOP 10 - PÚBLICO PREVISTO")

        top_publico = (
            df_filtrado
            .sort_values(by=coluna_publico, ascending=False)
            .head(10)
        )

        st.dataframe(
            top_publico,
            use_container_width=True
        )

    # =====================================================
    # ANÁLISE INTELIGENTE
    # =====================================================

    st.subheader("🧠 ANÁLISE INTELIGENTE OPERACIONAL")

    if coluna_publico and not df_filtrado[coluna_publico].dropna().empty:

        maior_publico = df_filtrado.loc[
            df_filtrado[coluna_publico].idxmax()
        ]

        menor_publico = df_filtrado.loc[
            df_filtrado[coluna_publico].idxmin()
        ]

        media_geral = round(
            df_filtrado[coluna_publico].mean(),
            2
        )

        mediana = round(
            df_filtrado[coluna_publico].median(),
            2
        )

        nome_maior = (
            maior_publico[coluna_evento]
            if coluna_evento else "N/D"
        )

        nome_menor = (
            menor_publico[coluna_evento]
            if coluna_evento else "N/D"
        )

        st.info(f"""
🚨 EVENTO COM MAIOR PÚBLICO PREVISTO:
{str(nome_maior).upper()} ({int(maior_publico[coluna_publico]):,} PESSOAS)

⚠️ EVENTO COM MENOR PÚBLICO PREVISTO:
{str(nome_menor).upper()} ({int(menor_publico[coluna_publico]):,} PESSOAS)

📊 MÉDIA GERAL DE PÚBLICO:
{media_geral:,.0f} PESSOAS

📈 MEDIANA DE PÚBLICO:
{mediana:,.0f} PESSOAS

🎉 TOTAL DE EVENTOS:
{total_eventos}

🏙️ TOTAL DE CIDADES:
{total_cidades}

🚔 TOTAL DE COMANDOS:
{total_comandos}
""")

    # =====================================================
    # RANKING OPERACIONAL
    # =====================================================

    if coluna_comando and coluna_publico:

        st.subheader("🏆 RANKING OPERACIONAL DOS COMANDOS")

        ranking = (
            df_filtrado
            .groupby(coluna_comando)[coluna_publico]
            .agg(["sum", "mean", "count"])
            .reset_index()
        )

        ranking.columns = [
            "COMANDO",
            "PÚBLICO TOTAL",
            "MÉDIA PÚBLICO",
            "REGISTROS"
        ]

        st.dataframe(
            ranking,
            use_container_width=True
        )

    # =====================================================
    # TABELA FINAL
    # =====================================================

    st.subheader("📄 DADOS OPERACIONAIS")

    pesquisa = st.text_input("🔎 PESQUISAR")

    tabela = df_filtrado.copy()

    if pesquisa:

        tabela = tabela[
            tabela.astype(str)
            .apply(
                lambda x: x.str.contains(
                    pesquisa,
                    case=False,
                    na=False
                )
            )
            .any(axis=1)
        ]

    st.dataframe(
        tabela,
        use_container_width=True,
        height=450
    )

    # =====================================================
    # DOWNLOAD CSV
    # =====================================================

    csv = tabela.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="⬇️ BAIXAR CSV",
        data=csv,
        file_name="operacao_sao_joao.csv",
        mime="text/csv"
    )

    st.success(f"✅ DASHBOARD ATUALIZADO EM {horario}")

except Exception as erro:

    st.error(
        f"ERRO AO CARREGAR DADOS: {str(erro).upper()}"
    )
