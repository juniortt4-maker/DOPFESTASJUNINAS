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
        font-size: 0.88rem !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# LINK DA PLANILHA
# =========================================================

url = (
    "https://docs.google.com/spreadsheets/d/"
    "1U2re0vGfssfUAFzra2oJoIVp4klRsbkpWBXVXSFd2Rs/"
    "export?format=csv&gid=459543687"
)

# =========================================================
# CORES
# =========================================================

PALETA_BARRAS = [
    "#5B8FF9", "#61DDAA", "#65789B", "#F6BD16",
    "#7262FD", "#78D3F8", "#9661BC",
    "#F6903D", "#008685", "#F08BB4"
]

PALETA_PIZZA = [
    "#5B8FF9", "#61DDAA", "#F6BD16",
    "#7262FD", "#F08BB4", "#78D3F8"
]

COR_LINHA_1 = "#5B8FF9"
COR_LINHA_2 = "#61DDAA"
COR_HISTOGRAMA = "#9CC3FF"

# =========================================================
# FUNÇÕES
# =========================================================

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

    df.columns = [c.strip() for c in df.columns]

    return df


def localizar_coluna(colunas, termos):

    for termo in termos:

        termo_norm = normalizar_texto(termo)

        for coluna in colunas:

            if termo_norm in normalizar_texto(coluna):
                return coluna

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
        font=dict(size=13, color="#3B4A5A"),
        bargap=0.22,
        margin=dict(l=20, r=20, t=50, b=20),

        xaxis=dict(
            showgrid=False,
            zeroline=False,
            linecolor="#D9E2EC",
            tickfont=dict(color="#52606D")
        ),

        yaxis=dict(
            showgrid=True,
            gridcolor="#EEF2F7",
            zeroline=False,
            linecolor="#D9E2EC",
            tickfont=dict(color="#52606D")
        ),

        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


# =========================================================
# INÍCIO
# =========================================================

try:

    df = carregar_dados()

    horario = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    st.sidebar.success("🟢 DASHBOARD SINCRONIZADO")
    st.sidebar.info(f"ÚLTIMA ATUALIZAÇÃO:\n{horario}")

    colunas = df.columns.tolist()

    # =====================================================
    # LOCALIZAÇÃO DAS COLUNAS
    # =====================================================

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
        ["DATA EVENTO", "DATA"]
    )

    coluna_natureza = localizar_coluna(
        colunas,
        ["NATUREZA"]
    )

    coluna_tipo_publico = localizar_coluna(
        colunas,
        ["TIPO DE PUBLICO", "TIPO PUBLICO"]
    )

    # =====================================================
    # TRATAMENTOS
    # =====================================================

    if coluna_publico:
        df[coluna_publico] = df[coluna_publico].apply(converter_numero_misto)
        df[coluna_publico] = pd.to_numeric(
            df[coluna_publico],
            errors="coerce"
        )

    # =====================================================
    # DATA
    # =====================================================

    if coluna_data and coluna_data in df.columns:

        df[coluna_data] = pd.to_datetime(
            df[coluna_data],
            errors="coerce",
            dayfirst=True
        )

        df = df[df[coluna_data].notna()].copy()

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

        df["Mes_Abrev"] = df["Mes_Num"].map(mapa_meses)

        df["AnoMes"] = (
            df["Ano"].astype(str)
            + "-"
            + df["Mes_Abrev"].astype(str)
        )

    # =====================================================
    # REMOVE ANO 2022
    # =====================================================

    if "Ano" in df.columns:
        df = df[df["Ano"] != 2022]

    # =====================================================
    # BASE FILTRADA
    # =====================================================

    df_filtrado = df.copy()

    # =====================================================
    # FILTROS
    # =====================================================

    st.sidebar.subheader("🎯 FILTROS")

    # FILTRO ANO

    if "Ano" in df_filtrado.columns:

        anos = sorted(
            df_filtrado["Ano"]
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
                df_filtrado["Ano"].isin(anos_sel)
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

    # FILTRO PERÍODO

    if coluna_data and df_filtrado[coluna_data].notna().any():

        data_min = df_filtrado[coluna_data].min().date()
        data_max = df_filtrado[coluna_data].max().date()

        intervalo = st.sidebar.date_input(
            "FILTRAR PERÍODO",
            value=(data_min, data_max),
            min_value=data_min,
            max_value=data_max
        )

        if isinstance(intervalo, tuple) and len(intervalo) == 2:

            data_ini, data_fim = intervalo

            df_filtrado = df_filtrado[
                (df_filtrado[coluna_data].dt.date >= data_ini)
                &
                (df_filtrado[coluna_data].dt.date <= data_fim)
            ]

    # =====================================================
    # VALIDAÇÃO
    # =====================================================

    if df_filtrado.empty:
        st.warning("NENHUM REGISTRO ENCONTRADO.")
        st.stop()

    # =====================================================
    # PANORAMA GERAL
    # =====================================================

    st.subheader("📚 PANORAMA GERAL")

    # EVENTOS POR ANO

    if "Ano" in df.columns:

        st.markdown("### 📊 COMPARATIVO DE EVENTOS POR ANO")

        eventos_ano = (
            df.groupby("Ano")
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

        st.plotly_chart(fig, use_container_width=True)

    # EVENTOS POR MÊS / ANO

    if "Mes_Abrev" in df.columns:

        st.markdown("### 📅 COMPARATIVO ANO/MÊS")

        eventos_mes = (
            df.groupby(["Ano", "Mes_Num", "Mes_Abrev"])
            .size()
            .reset_index(name="Eventos")
            .sort_values(["Ano", "Mes_Num"])
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

        st.plotly_chart(fig, use_container_width=True)

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
    # EVENTOS POR NATUREZA
    # =====================================================

    if coluna_natureza:

        st.subheader("🎭 EVENTOS POR NATUREZA")

        natureza_df = (
            df_filtrado
            .groupby(coluna_natureza)
            .size()
            .reset_index(name="Eventos")
            .sort_values(by="Eventos", ascending=False)
        )

        fig = px.pie(
            natureza_df,
            names=coluna_natureza,
            values="Eventos",
            hole=0.45,
            color_discrete_sequence=PALETA_PIZZA
        )

        fig = aplicar_estilo(fig)

        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # EVENTOS POR COMANDO
    # =====================================================

    if coluna_comando:

        st.subheader("🚔 EVENTOS POR COMANDO")

        comando_df = (
            df_filtrado
            .groupby(coluna_comando)
            .size()
            .reset_index(name="Eventos")
            .sort_values(by="Eventos", ascending=False)
        )

        fig = px.bar(
            comando_df,
            x=coluna_comando,
            y="Eventos",
            color=coluna_comando,
            text_auto=True,
            color_discrete_sequence=PALETA_BARRAS
        )

        fig = aplicar_estilo(fig)

        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # CIDADES
    # =====================================================

    if coluna_cidade:

        st.subheader("🏙️ CIDADES COM MAIS EVENTOS")

        cidade_df = (
            df_filtrado
            .groupby(coluna_cidade)
            .size()
            .reset_index(name="Eventos")
            .sort_values(by="Eventos", ascending=False)
            .head(15)
        )

        fig = px.bar(
            cidade_df,
            x=coluna_cidade,
            y="Eventos",
            color=coluna_cidade,
            text_auto=True,
            color_discrete_sequence=PALETA_BARRAS
        )

        fig = aplicar_estilo(fig)

        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # TOP EVENTOS
    # =====================================================

    if coluna_evento and coluna_publico:

        st.subheader("🎯 EVENTOS COM MAIOR PÚBLICO PREVISTO")

        top_eventos = (
            df_filtrado
            .groupby(coluna_evento)[coluna_publico]
            .sum()
            .reset_index()
            .sort_values(by=coluna_publico, ascending=False)
            .head(10)
        )

        fig = px.bar(
            top_eventos,
            x=coluna_evento,
            y=coluna_publico,
            color=coluna_evento,
            text_auto=".2s",
            color_discrete_sequence=PALETA_BARRAS
        )

        fig = aplicar_estilo(fig)

        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # HISTOGRAMA
    # =====================================================

    if coluna_publico:

        st.subheader("📊 DISTRIBUIÇÃO DO PÚBLICO")

        fig = px.histogram(
            df_filtrado,
            x=coluna_publico,
            nbins=20
        )

        fig.update_traces(
            marker_color=COR_HISTOGRAMA
        )

        fig = aplicar_estilo(fig)

        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # EVOLUÇÃO
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

        fig.update_traces(
            line=dict(color=COR_LINHA_2, width=3)
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

    pesquisa = st.text_input(
        "🔎 PESQUISAR NA TABELA"
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
        height=450
    )

    # =====================================================
    # DOWNLOAD
    # =====================================================

    csv = tabela.to_csv(
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

# =========================================================
# ERRO
# =========================================================

except Exception as erro:

    st.error(
        f"ERRO AO CARREGAR DADOS: {str(erro)}"
    )
