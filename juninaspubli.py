import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import unicodedata
import re

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="OPERAÇÃO - SÃO JOÃO 2026",
    page_icon="🚔",
    layout="wide"
)

st.title("🚔 OPERAÇÃO - SÃO JOÃO 2026")

# ==========================================
# ESTILO
# ==========================================
st.markdown("""
<style>

.stApp{
    background:#0B0F14;
}

h1,h2,h3{
    color:#E5E7EB;
}

section[data-testid="stSidebar"]{
    background:#111827;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# URL PLANILHA
# ==========================================
url = (
    "https://docs.google.com/spreadsheets/d/"
    "1U2re0vGfssfUAFzra2oJoIVp4klRsbkpWBXVXSFd2Rs/"
    "export?format=csv&gid=459543687"
)

# ==========================================
# CORES
# ==========================================
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

COR_LINHA = "#61DDAA"
COR_HISTOGRAMA = "#9CC3FF"

# ==========================================
# FUNÇÕES
# ==========================================
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

    df.columns = [
        col.strip()
        for col in df.columns
    ]

    return df


def localizar_coluna(colunas, termos):

    for termo in termos:

        termo = normalizar_texto(termo)

        for coluna in colunas:

            if termo in normalizar_texto(coluna):
                return coluna

    return None


def converter_numero_misto(valor):

    if pd.isna(valor):
        return pd.NA

    valor = str(valor).strip()

    if valor == "":
        return pd.NA

    valor = valor.replace(" ", "")
    valor = valor.replace(".", "")
    valor = valor.replace(",", ".")

    valor = re.sub(r"[^0-9.-]", "", valor)

    try:
        return float(valor)

    except:
        return pd.NA


def tratar_coluna_numerica(df, coluna):

    if coluna and coluna in df.columns:

        df[coluna] = df[coluna].apply(
            converter_numero_misto
        )

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
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        )
    )

    return fig


# ==========================================
# INÍCIO
# ==========================================
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

    # ==========================================
    # LOCALIZAÇÃO DAS COLUNAS
    # ==========================================
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

    # ==========================================
    # NOVA LOCALIZAÇÃO AUTOMÁTICA DATA
    # ==========================================
    coluna_data = localizar_coluna(
        colunas,
        [
            "DATA",
            "DATA EVENTO",
            "DATA RECEBIMENTO",
            "DATA INICIO",
            "DATA FINAL",
            "INICIO",
            "FIM"
        ]
    )

    # ==========================================
    # TRATAMENTO
    # ==========================================
    df = tratar_coluna_numerica(
        df,
        coluna_publico
    )

    df = tratar_coluna_data(
        df,
        coluna_data
    )

    # ==========================================
    # CRIAÇÃO ANO / MÊS
    # ==========================================
    if coluna_data and coluna_data in df.columns:

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

        df["Mes_Abrev"] = df["Mes_Num"].map(
            mapa_meses
        )

        df["AnoMes"] = (
            df["Ano"].astype("Int64").astype(str)
            + "-"
            + df["Mes_Abrev"].fillna("")
        )

    else:

        st.warning(
            "⚠️ NENHUMA COLUNA DE DATA FOI ENCONTRADA."
        )

    # ==========================================
    # FILTROS
    # ==========================================
    st.sidebar.subheader("🎯 FILTROS")

    df_filtrado = df.copy()

    # ANO
    if "Ano" in df_filtrado.columns:

        anos = sorted(
            df_filtrado["Ano"]
            .dropna()
            .astype(int)
            .unique()
        )

        anos_sel = st.sidebar.multiselect(
            "FILTRAR ANO",
            options=anos
        )

        if anos_sel:

            df_filtrado = df_filtrado[
                df_filtrado["Ano"].isin(anos_sel)
            ]

    # COMANDO
    if coluna_comando:

        comandos = sorted(
            df_filtrado[coluna_comando]
            .dropna()
            .astype(str)
            .unique()
        )

        comandos_sel = st.sidebar.multiselect(
            "FILTRAR COMANDO",
            options=comandos
        )

        if comandos_sel:

            df_filtrado = df_filtrado[
                df_filtrado[coluna_comando]
                .isin(comandos_sel)
            ]

    # CIDADE
    if coluna_cidade:

        cidades = sorted(
            df_filtrado[coluna_cidade]
            .dropna()
            .astype(str)
            .unique()
        )

        cidades_sel = st.sidebar.multiselect(
            "FILTRAR CIDADE",
            options=cidades
        )

        if cidades_sel:

            df_filtrado = df_filtrado[
                df_filtrado[coluna_cidade]
                .isin(cidades_sel)
            ]

    # NATUREZA
    if coluna_natureza:

        natureza = sorted(
            df_filtrado[coluna_natureza]
            .dropna()
            .astype(str)
            .unique()
        )

        natureza_sel = st.sidebar.multiselect(
            "FILTRAR NATUREZA",
            options=natureza
        )

        if natureza_sel:

            df_filtrado = df_filtrado[
                df_filtrado[coluna_natureza]
                .isin(natureza_sel)
            ]

    # TIPO PÚBLICO
    if coluna_tipo_publico:

        tipos = sorted(
            df_filtrado[coluna_tipo_publico]
            .dropna()
            .astype(str)
            .unique()
        )

        tipos_sel = st.sidebar.multiselect(
            "FILTRAR TIPO PÚBLICO",
            options=tipos
        )

        if tipos_sel:

            df_filtrado = df_filtrado[
                df_filtrado[coluna_tipo_publico]
                .isin(tipos_sel)
            ]

    # DATA
    if coluna_data and df_filtrado[coluna_data].notna().any():

        data_min = df_filtrado[
            coluna_data
        ].min().date()

        data_max = df_filtrado[
            coluna_data
        ].max().date()

        intervalo = st.sidebar.date_input(
            "FILTRAR PERÍODO",
            value=(data_min, data_max)
        )

        if (
            isinstance(intervalo, tuple)
            and len(intervalo) == 2
        ):

            data_ini, data_fim = intervalo

            df_filtrado = df_filtrado[
                (
                    df_filtrado[coluna_data].dt.date
                    >= data_ini
                )
                &
                (
                    df_filtrado[coluna_data].dt.date
                    <= data_fim
                )
            ]

    # ==========================================
    # INDICADORES
    # ==========================================
    st.subheader(
        "📌 INDICADORES OPERACIONAIS"
    )

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

    # ==========================================
    # COMPARATIVO ANO / MÊS
    # ==========================================
    if (
        "Ano" in df_filtrado.columns
        and "Mes_Abrev" in df_filtrado.columns
    ):

        st.subheader(
            "📅 COMPARATIVO ANO/MÊS"
        )

        eventos_mes_ano = (
            df_filtrado
            .groupby(
                ["Ano", "Mes_Num", "Mes_Abrev"]
            )
            .size()
            .reset_index(name="Eventos")
            .sort_values(
                ["Ano", "Mes_Num"]
            )
        )

        ordem = [
            "Jan",
            "Fev",
            "Mar",
            "Abr",
            "Mai",
            "Jun",
            "Jul",
            "Ago",
            "Set",
            "Out",
            "Nov",
            "Dez"
        ]

        eventos_mes_ano[
            "Mes_Abrev"
        ] = pd.Categorical(
            eventos_mes_ano["Mes_Abrev"],
            categories=ordem,
            ordered=True
        )

        fig = px.bar(
            eventos_mes_ano,
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

    # ==========================================
    # EVENTOS POR COMANDO
    # ==========================================
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

        fig.update_layout(
            showlegend=False
        )

        fig = aplicar_estilo(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ==========================================
    # EVENTOS POR CIDADE
    # ==========================================
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

        fig.update_layout(
            showlegend=False
        )

        fig = aplicar_estilo(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ==========================================
    # EVENTOS MAIOR PÚBLICO
    # ==========================================
    if coluna_evento and coluna_publico:

        st.subheader(
            "🎯 EVENTOS COM MAIOR PÚBLICO PREVISTO"
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

        fig.update_layout(
            showlegend=False
        )

        fig = aplicar_estilo(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ==========================================
    # HISTOGRAMA
    # ==========================================
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

    # ==========================================
    # EVOLUÇÃO
    # ==========================================
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
                color=COR_LINHA,
                width=3
            )
        )

        fig = aplicar_estilo(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ==========================================
    # TOP 10
    # ==========================================
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

    # ==========================================
    # ANÁLISE INTELIGENTE
    # ==========================================
    st.subheader(
        "🧠 ANÁLISE INTELIGENTE OPERACIONAL"
    )

    if (
        coluna_publico
        and not df_filtrado[coluna_publico]
        .dropna()
        .empty
    ):

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

    # ==========================================
    # RANKING OPERACIONAL
    # ==========================================
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

    # ==========================================
    # TABELA FINAL
    # ==========================================
    st.subheader(
        "📄 DADOS OPERACIONAIS"
    )

    pesquisa = st.text_input(
        "🔎 PESQUISAR NA TABELA FINAL"
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

    # ==========================================
    # DOWNLOAD CSV
    # ==========================================
    csv = df_tabela.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="⬇️ BAIXAR CSV",
        data=csv,
        file_name="operacao_sao_joao_filtrado.csv",
        mime="text/csv"
    )

    st.success(
        f"✅ DASHBOARD ATUALIZADO EM {horario}"
    )

# ==========================================
# ERRO
# ==========================================
except Exception as erro:

    st.error(
        f"ERRO AO CARREGAR DADOS: {str(erro).upper()}"
    )
