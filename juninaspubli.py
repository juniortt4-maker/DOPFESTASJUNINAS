# =========================
# OPERAÇÃO SÃO JOÃO 2026
# DASHBOARD COMPLETO
# =========================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import unicodedata
import re

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================

st.set_page_config(
    page_title="OPERAÇÃO - SÃO JOÃO 2026",
    page_icon="🚔",
    layout="wide"
)

st.title("🚔 OPERAÇÃO - SÃO JOÃO 2026")

# =========================
# ESTILO VISUAL
# =========================

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
    background-color: #111827;
    border: 1px solid #1F2937;
    padding: 15px;
    border-radius: 12px;
}

div[data-testid="metric-container"] label {
    color: white !important;
}

div[data-testid="metric-container"] div {
    color: #61DDAA !important;
}

</style>
""", unsafe_allow_html=True)

# =========================
# URL GOOGLE SHEETS
# =========================

url = (
    "https://docs.google.com/spreadsheets/d/"
    "1U2re0vGfssfUAFzra2oJoIVp4klRsbkpWBXVXSFd2Rs/"
    "export?format=csv&gid=1866688086"
)

# =========================
# PALETAS
# =========================

PALETA_BARRAS = [
    "#5B8FF9", "#61DDAA", "#65789B",
    "#F6BD16", "#7262FD", "#78D3F8",
    "#9661BC", "#F6903D", "#008685",
    "#F08BB4"
]

PALETA_PIZZA = [
    "#5B8FF9", "#61DDAA",
    "#F6BD16", "#7262FD",
    "#F08BB4", "#78D3F8"
]

COR_HISTOGRAMA = "#9CC3FF"

# =========================
# FUNÇÕES
# =========================

def normalizar_texto(texto):

    texto = str(texto).strip().upper()

    texto = unicodedata.normalize(
        "NFKD",
        texto
    ).encode(
        "ASCII",
        "ignore"
    ).decode("utf-8")

    texto = re.sub(r"\s+", " ", texto)

    return texto

@st.cache_data(ttl=60)
def carregar_dados():

    df = pd.read_csv(url)

    df = df.dropna(how="all")

    df.columns = [col.strip() for col in df.columns]

    return df

def localizar_coluna(colunas, termos):

    for termo in termos:

        termo_norm = normalizar_texto(termo)

        for c in colunas:

            if termo_norm in normalizar_texto(c):
                return c

    return None

def converter_numero_misto(valor):

    if pd.isna(valor):
        return pd.NA

    s = str(valor).strip()

    if s == "":
        return pd.NA

    s = s.replace(" ", "")

    s = re.sub(r"[R$\u00A0]", "", s)

    if "," in s and "." in s:

        if s.rfind(",") > s.rfind("."):

            s = s.replace(".", "")
            s = s.replace(",", ".")

        else:

            s = s.replace(",", "")

    elif "," in s:

        s = s.replace(".", "")
        s = s.replace(",", ".")

    else:

        s = s.replace(",", "")

    s = re.sub(r"[^0-9\\.-]", "", s)

    try:
        return float(s)

    except:
        return pd.NA

def tratar_coluna_numerica(df, coluna):

    if coluna and coluna in df.columns:

        df[coluna] = df[coluna].apply(converter_numero_misto)

        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce"
        )

    return df

def tratar_coluna_data(df, coluna):

    if coluna and coluna in df.columns:

        df[coluna] = pd.to_datetime(
            df[coluna],
            errors="coerce",
            dayfirst=True
        )

    return df

def aplicar_estilo(fig):

    fig.update_layout(

        template="simple_white",

        plot_bgcolor="white",

        paper_bgcolor="white",

        font=dict(
            size=13,
            color="#3B4A5A"
        ),

        bargap=0.22,

        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        ),

        xaxis=dict(
            showgrid=False,
            zeroline=False,
            linecolor="#D9E2EC"
        ),

        yaxis=dict(
            showgrid=True,
            gridcolor="#EEF2F7",
            zeroline=False,
            linecolor="#D9E2EC"
        )
    )

    return fig

def preparar_base_eventos(df, coluna_evento):

    if not coluna_evento:
        return df.copy()

    base = df.copy()

    base["_EVENTO_TEXTO_"] = (
        base[coluna_evento]
        .astype(str)
        .str.strip()
    )

    base = base[
        base["_EVENTO_TEXTO_"] != ""
    ]

    return base

# =========================
# PROCESSAMENTO
# =========================

try:

    df = carregar_dados()

    horario = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    st.sidebar.success("🟢 DASHBOARD SINCRONIZADO")

    st.sidebar.info(
        f"ÚLTIMA ATUALIZAÇÃO:\n{horario}"
    )

    colunas = df.columns.tolist()

    coluna_comando = localizar_coluna(
        colunas,
        ["COMANDO"]
    )

    coluna_cidade = localizar_coluna(
        colunas,
        ["CIDADE", "MUNICIPIO"]
    )

    coluna_evento = localizar_coluna(
        colunas,
        ["EVENTO", "NOME EVENTO"]
    )

    coluna_publico = localizar_coluna(
        colunas,
        ["PUBLICO", "PUBLICO PREVISTO"]
    )

    coluna_data = localizar_coluna(
        colunas,
        ["DATA"]
    )

    coluna_natureza = localizar_coluna(
        colunas,
        ["NATUREZA"]
    )

    # =========================
    # TRATAMENTO
    # =========================

    df = tratar_coluna_numerica(
        df,
        coluna_publico
    )

    df = tratar_coluna_data(
        df,
        coluna_data
    )

    if coluna_data:

        df["Ano"] = df[coluna_data].dt.year

        df["Mes_Num"] = df[coluna_data].dt.month

        mapa_meses = {
            1: "Jan",
            2: "Fev",
            3: "Mar",
            4: "Abr",
            5: "Mai",
            6: "Jun",
            7: "Jul",
            8: "Ago",
            9: "Set",
            10: "Out",
            11: "Nov",
            12: "Dez"
        }

        df["Mes_Abrev"] = (
            df["Mes_Num"]
            .map(mapa_meses)
        )

    df_historico = preparar_base_eventos(
        df.copy(),
        coluna_evento
    )

    df_filtrado = df.copy()

    # =========================
    # FILTROS
    # =========================

    st.sidebar.subheader("🎯 FILTROS")

    if "Ano" in df.columns:

        anos = sorted(
            df["Ano"]
            .dropna()
            .astype(int)
            .unique()
        )

        anos_sel = st.sidebar.multiselect(
            "FILTRAR ANO",
            anos
        )

        if anos_sel:

            df_filtrado = df_filtrado[
                df_filtrado["Ano"].isin(anos_sel)
            ]

    # =========================
    # BASE FILTRADA
    # =========================

    df_filtrado_eventos = preparar_base_eventos(
        df_filtrado.copy(),
        coluna_evento
    )

    # =========================
    # COMPARATIVO ANO
    # =========================

    st.subheader("📊 COMPARATIVO DE EVENTOS POR ANO")

    eventos_ano = (
        df_historico
        .groupby("Ano")
        .size()
        .reset_index(name="Eventos")
        .sort_values("Ano")
    )

    fig = px.bar(
        eventos_ano,
        x="Ano",
        y="Eventos",
        color="Ano",
        text_auto=True,
        color_discrete_sequence=PALETA_BARRAS
    )

    fig = aplicar_estilo(fig)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =========================
    # COMPARATIVO MÊS / ANO
    # =========================

    st.subheader("📅 COMPARATIVO ANO/MÊS")

    eventos_mes = (
        df_historico
        .groupby(
            ["Ano", "Mes_Abrev"]
        )
        .size()
        .reset_index(name="Eventos")
    )

    fig = px.bar(
        eventos_mes,
        x="Mes_Abrev",
        y="Eventos",
        color="Ano",
        barmode="group",
        text_auto=True,
        color_discrete_sequence=PALETA_BARRAS
    )

    fig = aplicar_estilo(fig)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =========================
    # INDICADORES
    # =========================

    st.subheader("📌 INDICADORES OPERACIONAIS")

    total_eventos = len(df_filtrado_eventos)

    total_publico = int(
        df_filtrado[coluna_publico]
        .fillna(0)
        .sum()
    )

    total_cidades = (
        df_filtrado[coluna_cidade]
        .nunique()
        if coluna_cidade else 0
    )

    total_comandos = (
        df_filtrado[coluna_comando]
        .nunique()
        if coluna_comando else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "🎉 EVENTOS",
        total_eventos
    )

    col2.metric(
        "👥 PÚBLICO",
        f"{total_publico:,}".replace(",", ".")
    )

    col3.metric(
        "🏙️ CIDADES",
        total_cidades
    )

    col4.metric(
        "🚔 COMANDOS",
        total_comandos
    )

    # =========================
    # TOP 10
    # =========================

    if coluna_publico:

        st.subheader(
            "🔥 TOP 10 - PÚBLICO PREVISTO"
        )

        top_publico = (
            df_filtrado
            .sort_values(
                by=coluna_publico,
                ascending=False
            )
            .head(10)
        )

        st.dataframe(
            top_publico,
            use_container_width=True
        )

    # =========================
    # ANÁLISE INTELIGENTE
    # =========================

    st.subheader(
        "🧠 ANÁLISE INTELIGENTE OPERACIONAL"
    )

    if coluna_publico:

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

{str(nome_maior).upper()}
({int(maior_publico[coluna_publico]):,} PESSOAS)

⚠️ EVENTO COM MENOR PÚBLICO PREVISTO:

{str(nome_menor).upper()}
({int(menor_publico[coluna_publico]):,} PESSOAS)

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

    # =========================
    # RANKING COMANDOS
    # =========================

    if coluna_comando and coluna_publico:

        st.subheader(
            "🏆 RANKING OPERACIONAL DOS COMANDOS"
        )

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

    # =========================
    # EVENTOS POR COMANDO
    # =========================

    if coluna_comando:

        st.subheader(
            "🚔 EVENTOS POR COMANDO"
        )

        comando_eventos = (
            df_filtrado_eventos
            .groupby(coluna_comando)
            .size()
            .reset_index(name="Eventos")
            .sort_values(
                by="Eventos",
                ascending=False
            )
        )

        fig = px.bar(
            comando_eventos,
            x=coluna_comando,
            y="Eventos",
            color=coluna_comando,
            text_auto=True,
            color_discrete_sequence=PALETA_BARRAS
        )

        fig.update_layout(
            showlegend=False
        )

        fig = aplicar_estilo(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # =========================
    # HISTOGRAMA
    # =========================

    if coluna_publico:

        st.subheader(
            "📊 DISTRIBUIÇÃO DO PÚBLICO"
        )

        fig = px.histogram(
            df_filtrado,
            x=coluna_publico,
            nbins=20
        )

        fig.update_traces(
            marker_color=COR_HISTOGRAMA
        )

        fig = aplicar_estilo(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # =========================
    # EVOLUÇÃO
    # =========================

    if coluna_data and coluna_publico:

        st.subheader(
            "📈 EVOLUÇÃO DO PÚBLICO"
        )

        evolucao = (
            df_filtrado
            .groupby(coluna_data)[coluna_publico]
            .sum()
            .reset_index()
        )

        fig = px.line(
            evolucao,
            x=coluna_data,
            y=coluna_publico,
            markers=True
        )

        fig = aplicar_estilo(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # =========================
    # TABELA FINAL
    # =========================

    st.subheader("📄 DADOS OPERACIONAIS")

    pesquisa = st.text_input(
        "🔎 PESQUISAR NA TABELA"
    )

    df_tabela = df_filtrado.copy()

    if pesquisa:

        df_tabela = df_tabela[
            df_tabela.astype(str)
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
        df_tabela,
        use_container_width=True,
        height=500
    )

    # =========================
    # DOWNLOAD CSV
    # =========================

    csv = df_tabela.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="⬇️ BAIXAR CSV",
        data=csv,
        file_name="operacao_sao_joao.csv",
        mime="text/csv"
    )

    st.success(
        f"✅ DASHBOARD ATUALIZADO EM {horario}"
    )

except Exception as erro:

    st.error(
        f"ERRO AO CARREGAR DADOS: {str(erro)}"
    )
