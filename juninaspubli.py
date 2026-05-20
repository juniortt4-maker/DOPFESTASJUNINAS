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
# ESTILO
# =========================

st.markdown("""
<style>

.stApp {
    background: #0B0F14;
}

h1, h2, h3 {
    color: #E5E7EB;
    letter-spacing: -0.2px;
}

.stCaption {
    color: #94A3B8 !important;
}

</style>
""", unsafe_allow_html=True)

# =========================
# PLANILHA
# =========================

url = (
    "https://docs.google.com/spreadsheets/d/"
    "1U2re0vGfssfUAFzra2oJoIVp4klRsbkpWBXVXSFd2Rs/"
    "export?format=csv&gid=459543687"
)

# =========================
# CORES
# =========================

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

COR_LINHA_1 = "#5B8FF9"
COR_LINHA_2 = "#61DDAA"
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
    ).decode(
        "utf-8"
    )

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

# =========================
# CARREGA DADOS
# =========================

try:

    df = carregar_dados()

    horario = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )

    st.sidebar.success(
        "🟢 DASHBOARD SINCRONIZADO"
    )

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
        ["EVENTO"]
    )

    coluna_publico = localizar_coluna(
        colunas,
        ["PUBLICO"]
    )

    coluna_natureza = localizar_coluna(
        colunas,
        ["NATUREZA"]
    )

    coluna_tipo_publico = localizar_coluna(
        colunas,
        ["TIPO PUBLICO"]
    )

    # =========================
    # DATA AJUSTADA
    # =========================

    coluna_data = localizar_coluna(
        colunas,
        [
            "DATA DO EVENTO",
            "DATA EVENTO",
            "DATA_INICIO",
            "DATA INICIO",
            "DATA"
        ]
    )

    # =========================
    # TRATAMENTO PÚBLICO
    # =========================

    if coluna_publico:

        df[coluna_publico] = (
            df[coluna_publico]
            .apply(converter_numero_misto)
        )

        df[coluna_publico] = pd.to_numeric(
            df[coluna_publico],
            errors="coerce"
        )

    # =========================
    # TRATAMENTO DATA
    # =========================

    if coluna_data and coluna_data in df.columns:

        df[coluna_data] = pd.to_datetime(
            df[coluna_data],
            errors="coerce",
            dayfirst=True
        )

        # remove inválidas
        df = df[df[coluna_data].notna()].copy()

        # remove anos errados
        df = df[
            (df[coluna_data].dt.year >= 2023) &
            (df[coluna_data].dt.year <= 2026)
        ]

        df["Ano"] = (
            df[coluna_data]
            .dt.year
            .astype("Int64")
        )

        df["Mes_Num"] = (
            df[coluna_data]
            .dt.month
            .astype("Int64")
        )

        # remove meses inválidos
        df = df[
            (df["Mes_Num"] >= 1) &
            (df["Mes_Num"] <= 12)
        ]

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

    # =========================
    # FILTROS
    # =========================

    df_filtrado = df.copy()

    st.sidebar.subheader("🎯 FILTROS")

    # ANO
    if "Ano" in df_filtrado.columns:

        anos = sorted(
            df_filtrado["Ano"]
            .dropna()
            .unique()
            .tolist()
        )

        anos_sel = st.sidebar.multiselect(
            "FILTRAR ANO",
            options=anos
        )

        if anos_sel:

            df_filtrado = df_filtrado[
                df_filtrado["Ano"]
                .isin(anos_sel)
            ]

    # COMANDO
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
            options=comandos
        )

        if comandos_sel:

            df_filtrado = df_filtrado[
                df_filtrado[coluna_comando]
                .astype(str)
                .isin(comandos_sel)
            ]

    # CIDADE
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
            options=cidades
        )

        if cidades_sel:

            df_filtrado = df_filtrado[
                df_filtrado[coluna_cidade]
                .astype(str)
                .isin(cidades_sel)
            ]

    # NATUREZA
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
            options=natureza
        )

        if natureza_sel:

            df_filtrado = df_filtrado[
                df_filtrado[coluna_natureza]
                .astype(str)
                .isin(natureza_sel)
            ]

    # =========================
    # INDICADORES
    # =========================

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
        if coluna_cidade else 0
    )

    total_comandos = (
        df_filtrado[coluna_comando]
        .nunique()
        if coluna_comando else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "🎉 EVENTOS",
        total_eventos
    )

    c2.metric(
        "👥 PÚBLICO",
        f"{total_publico:,}".replace(",", ".")
    )

    c3.metric(
        "🏙️ CIDADES",
        total_cidades
    )

    c4.metric(
        "🚔 COMANDOS",
        total_comandos
    )

    # =========================
    # COMPARATIVO ANO/MÊS
    # =========================

    st.subheader("📅 COMPARATIVO ANO/MÊS")

    comparativo = (
        df_filtrado
        .groupby(["Ano", "Mes_Abrev"])
        .size()
        .reset_index(name="Eventos")
    )

    ordem = [
        "Jan", "Fev", "Mar", "Abr",
        "Mai", "Jun", "Jul", "Ago",
        "Set", "Out", "Nov", "Dez"
    ]

    comparativo["Mes_Abrev"] = pd.Categorical(
        comparativo["Mes_Abrev"],
        categories=ordem,
        ordered=True
    )

    comparativo = comparativo.sort_values(
        ["Ano", "Mes_Abrev"]
    )

    fig = px.bar(
        comparativo,
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
    # EVENTOS POR COMANDO
    # =========================

    if coluna_comando:

        st.subheader(
            "🚔 EVENTOS POR COMANDO"
        )

        comando_eventos = (
            df_filtrado
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

        fig = aplicar_estilo(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # =========================
    # EVENTOS POR NATUREZA
    # =========================

    if coluna_natureza:

        st.subheader(
            "🎭 EVENTOS POR NATUREZA"
        )

        natureza_eventos = (
            df_filtrado
            .groupby(coluna_natureza)
            .size()
            .reset_index(name="Eventos")
        )

        fig = px.pie(
            natureza_eventos,
            names=coluna_natureza,
            values="Eventos",
            hole=0.45,
            color_discrete_sequence=PALETA_PIZZA
        )

        fig = aplicar_estilo(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # =========================
    # EVENTOS POR CIDADE
    # =========================

    if coluna_cidade:

        st.subheader(
            "🏙️ CIDADES COM MAIS EVENTOS"
        )

        cidade_eventos = (
            df_filtrado
            .groupby(coluna_cidade)
            .size()
            .reset_index(name="Eventos")
            .sort_values(
                by="Eventos",
                ascending=False
            )
            .head(15)
        )

        fig = px.bar(
            cidade_eventos,
            x=coluna_cidade,
            y="Eventos",
            color=coluna_cidade,
            text_auto=True,
            color_discrete_sequence=PALETA_BARRAS
        )

        fig = aplicar_estilo(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # =========================
    # TOP EVENTOS
    # =========================

    if coluna_evento and coluna_publico:

        st.subheader(
            "🎯 EVENTOS COM MAIOR PÚBLICO"
        )

        eventos_publico = (
            df_filtrado
            .groupby(coluna_evento)[coluna_publico]
            .sum()
            .reset_index()
            .sort_values(
                by=coluna_publico,
                ascending=False
            )
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
            "📊 DISTRIBUIÇÃO DE PÚBLICO"
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
            .sort_values(coluna_data)
        )

        fig = px.line(
            evolucao,
            x=coluna_data,
            y=coluna_publico,
            markers=True
        )

        fig.update_traces(
            line=dict(
                color=COR_LINHA_2,
                width=3
            )
        )

        fig = aplicar_estilo(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
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

    if coluna_publico:

        st.subheader(
            "🧠 ANÁLISE INTELIGENTE OPERACIONAL"
        )

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

        st.info(f"""
🚨 EVENTO COM MAIOR PÚBLICO PREVISTO:
{str(maior_publico[coluna_evento]).upper()} ({int(maior_publico[coluna_publico]):,} PESSOAS)

⚠️ EVENTO COM MENOR PÚBLICO PREVISTO:
{str(menor_publico[coluna_evento]).upper()} ({int(menor_publico[coluna_publico]):,} PESSOAS)

📊 MÉDIA GERAL DE PÚBLICO:
{media_geral:,.0f} PESSOAS

📈 MEDIANA DE PÚBLICO:
{mediana:,.0f} PESSOAS
""")

    # =========================
    # RANKING
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
    # TABELA
    # =========================

    st.subheader(
        "📄 DADOS OPERACIONAIS"
    )

    pesquisa = st.text_input(
        "🔎 PESQUISAR"
    )

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
        height=500
    )

    # =========================
    # DOWNLOAD
    # =========================

    csv = tabela.to_csv(
        index=False
    ).encode(
        "utf-8-sig"
    )

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
