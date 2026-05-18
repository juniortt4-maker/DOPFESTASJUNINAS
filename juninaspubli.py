import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import unicodedata
import re

st.set_page_config(
    page_title="Operação - São João 2026",
    page_icon="🚔",
    layout="wide"
)

st.title("🚔 Operação - São João 2026")

url = (
    "https://docs.google.com/spreadsheets/d/"
    "1qQrvomIDols1qLFsziiCP2BZtXLRXpjsErXKqONTsVE/"
    "export?format=csv&gid=1996198248"
)

PALETA_BARRAS = [
    "#5B8FF9", "#61DDAA", "#65789B", "#F6BD16", "#7262FD",
    "#78D3F8", "#9661BC", "#F6903D", "#008685", "#F08BB4"
]

PALETA_PIZZA = [
    "#5B8FF9", "#61DDAA", "#F6BD16", "#7262FD", "#F08BB4", "#78D3F8"
]

COR_BARRA_UNICA = "#5B8FF9"
COR_LINHA_1 = "#5B8FF9"
COR_LINHA_2 = "#61DDAA"
COR_HISTOGRAMA = "#9CC3FF"

def normalizar_texto(texto):
    texto = str(texto).strip().upper()
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8")
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

    s = re.sub(r"[^0-9\.-]", "", s)

    try:
        return float(s)
    except:
        return pd.NA

def tratar_coluna_numerica(df, coluna):
    if coluna and coluna in df.columns:
        df[coluna] = df[coluna].apply(converter_numero_misto)
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
    return df

def tratar_coluna_data(df, coluna):
    if coluna and coluna in df.columns:
        df[coluna] = pd.to_datetime(df[coluna], errors="coerce", dayfirst=True)
    return df

def tratar_coluna_categorica(df, coluna):
    if coluna and coluna in df.columns:
        df[coluna] = (
            df[coluna]
            .astype(str)
            .str.strip()
            .replace(["", "NAN", "None", "none", "nan", "<NA>"], pd.NA)
        )
    return df

def normalizar_cobranca(valor):
    if pd.isna(valor):
        return pd.NA

    txt = normalizar_texto(valor)

    if txt in ["", "NAN", "NONE", "NULL", "NA", "<NA>"]:
        return pd.NA

    mapa_nao = {
        "NAO", "NAO PAGO", "SEM COBRANCA", "SEM COBRANCA DE INGRESSO",
        "GRATUITO", "GRATUITA", "LIVRE", "ISENTO", "ISENTA",
        "FRANQUEADO", "FRANQUEADA", "ENTRADA FRANCA", "SEM PAGAMENTO"
    }

    mapa_sim = {
        "SIM", "COBRADO", "COBRANCA", "PAGO", "PAGA", "PAGAMENTO",
        "INGRESSO PAGO", "COM COBRANCA", "PAGOU", "PAGA ENTRADA",
        "VENDA DE INGRESSO", "COBRANCA DE INGRESSO"
    }

    if txt in mapa_nao:
        return "NÃO"
    if txt in mapa_sim:
        return "SIM"

    if "SEM COBRANCA" in txt or "GRATUIT" in txt or "ENTRADA FRANCA" in txt:
        return "NÃO"
    if "COBRAN" in txt or "PAG" in txt or "INGRESSO" in txt:
        return "SIM"

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

try:
    df = carregar_dados()
    horario = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    st.sidebar.success("🟢 Dashboard sincronizado")
    st.sidebar.info(f"Última atualização da carga:\n{horario}")

    colunas = df.columns.tolist()

    coluna_comando = localizar_coluna(colunas, ["COMANDO"])
    coluna_cidade = localizar_coluna(colunas, ["CIDADE", "MUNICIPIO"])
    coluna_evento = localizar_coluna(colunas, ["EVENTO", "NOME EVENTO"])
    coluna_publico = localizar_coluna(colunas, ["PUBLICO", "PUBLICO PREVISTO"])
    coluna_data = localizar_coluna(colunas, ["DATA"])
    coluna_natureza = localizar_coluna(colunas, ["NATUREZA"])
    coluna_tipo_publico = localizar_coluna(colunas, ["TIPO DE PUBLICO", "TIPO PUBLICO"])
    coluna_cobranca = colunas[19] if len(colunas) > 19 else None

    df = tratar_coluna_numerica(df, coluna_publico)
    df = tratar_coluna_data(df, coluna_data)
    df = tratar_coluna_categorica(df, coluna_tipo_publico)
    df = tratar_coluna_categorica(df, coluna_natureza)
    df = tratar_coluna_categorica(df, coluna_cobranca)

    if coluna_cobranca and coluna_cobranca in df.columns:
        df[coluna_cobranca] = df[coluna_cobranca].apply(normalizar_cobranca)

    if coluna_data and coluna_data in df.columns:
        df = df[df[coluna_data].notna()].copy()

        df["Ano"] = df[coluna_data].dt.year
        df["Mes_Num"] = df[coluna_data].dt.month

        df = df[df["Ano"] != 2022].copy()
        df = df[df["Mes_Num"].isin([5, 6, 7, 8])].copy()

        mapa_meses = {
            1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
            7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
        }

        df["Mes_Abrev"] = df["Mes_Num"].map(mapa_meses)
        df["AnoMes"] = df["Ano"].astype("Int64").astype(str) + "-" + df["Mes_Abrev"].fillna("")
        df.loc[df["Ano"].isna(), "AnoMes"] = None

    df_historico = df.copy()
    df_filtrado = df.copy()

    st.sidebar.subheader("🎯 Filtros")

    if "Ano" in df_filtrado.columns and df_filtrado["Ano"].notna().any():
        opcoes_ano = sorted(df_filtrado["Ano"].dropna().astype(int).unique().tolist())
        anos_sel = st.sidebar.multiselect("Filtrar Ano", options=opcoes_ano, default=[])
        if anos_sel:
            df_filtrado = df_filtrado[df_filtrado["Ano"].isin(anos_sel)]

    if coluna_comando:
        opcoes_comando = sorted(df_filtrado[coluna_comando].dropna().astype(str).unique().tolist())
        comandos_sel = st.sidebar.multiselect("Filtrar Comando", options=opcoes_comando, default=[])
        if comandos_sel:
            df_filtrado = df_filtrado[df_filtrado[coluna_comando].astype(str).isin(comandos_sel)]

    if coluna_cidade:
        opcoes_cidade = sorted(df_filtrado[coluna_cidade].dropna().astype(str).unique().tolist())
        cidades_sel = st.sidebar.multiselect("Filtrar Cidade", options=opcoes_cidade, default=[])
        if cidades_sel:
            df_filtrado = df_filtrado[df_filtrado[coluna_cidade].astype(str).isin(cidades_sel)]

    if coluna_natureza:
        opcoes_natureza = sorted(df_filtrado[coluna_natureza].dropna().astype(str).unique().tolist())
        natureza_sel = st.sidebar.multiselect("Filtrar Natureza", options=opcoes_natureza, default=[])
        if natureza_sel:
            df_filtrado = df_filtrado[df_filtrado[coluna_natureza].astype(str).isin(natureza_sel)]

    if coluna_data and df_filtrado[coluna_data].notna().any():
        data_min = df_filtrado[coluna_data].min().date()
        data_max = df_filtrado[coluna_data].max().date()

        intervalo = st.sidebar.date_input(
            "Filtrar Período",
            value=(data_min, data_max),
            min_value=data_min,
            max_value=data_max
        )

        if isinstance(intervalo, tuple) and len(intervalo) == 2:
            data_ini, data_fim = intervalo
            df_filtrado = df_filtrado[
                (df_filtrado[coluna_data].dt.date >= data_ini) &
                (df_filtrado[coluna_data].dt.date <= data_fim)
            ]

    st.subheader("📚 Panorama Geral")
    st.caption("Os gráficos abaixo permanecem fixos e não são alterados pelos filtros operacionais da barra lateral.")

    if "Ano" in df_historico.columns and df_historico["Ano"].notna().any():
        st.markdown("### 📊 Comparativo de Eventos por Ano")
        eventos_ano = (
            df_historico.dropna(subset=["Ano"])
            .groupby("Ano")
            .size()
            .reset_index(name="Eventos")
            .sort_values("Ano")
        )
        eventos_ano["Ano"] = eventos_ano["Ano"].astype(str)

        fig = px.bar(
            eventos_ano,
            x="Ano",
            y="Eventos",
            color="Ano",
            text_auto=True,
            color_discrete_sequence=PALETA_BARRAS,
            template="simple_white"
        )
        fig.update_layout(xaxis_title="Ano", yaxis_title="Eventos", showlegend=False)
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if "Ano" in df_historico.columns and coluna_publico and df_historico["Ano"].notna().any():
        st.markdown("### 👥 Público Previsto por Ano")
        publico_ano = (
            df_historico.dropna(subset=["Ano"])
            .groupby("Ano")[coluna_publico]
            .sum()
            .reset_index()
            .sort_values("Ano")
        )
        publico_ano["Ano"] = publico_ano["Ano"].astype(str)

        fig = px.bar(
            publico_ano,
            x="Ano",
            y=coluna_publico,
            color="Ano",
            text_auto=".2s",
            color_discrete_sequence=PALETA_BARRAS,
            template="simple_white"
        )
        fig.update_layout(xaxis_title="Ano", yaxis_title="Público Previsto", showlegend=False)
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if "Ano" in df_historico.columns and "Mes_Num" in df_historico.columns and df_historico["Ano"].notna().any():
        st.markdown("### 📅 Comparativo de Eventos por Mês e Ano")
        eventos_mes_ano = (
            df_historico.dropna(subset=["Ano", "Mes_Num"])
            .groupby(["Ano", "Mes_Num", "Mes_Abrev"])
            .size()
            .reset_index(name="Eventos")
            .sort_values(["Ano", "Mes_Num"])
        )

        ordem_meses_abrev = ["Mai", "Jun", "Jul", "Ago"]
        eventos_mes_ano["Mes_Abrev"] = pd.Categorical(
            eventos_mes_ano["Mes_Abrev"],
            categories=ordem_meses_abrev,
            ordered=True
        )
        eventos_mes_ano["Ano"] = eventos_mes_ano["Ano"].astype(str)
        eventos_mes_ano = eventos_mes_ano.sort_values(["Ano", "Mes_Abrev"])

        fig = px.bar(
            eventos_mes_ano,
            x="Mes_Abrev",
            y="Eventos",
            color="Ano",
            barmode="group",
            text_auto=True,
            color_discrete_sequence=PALETA_BARRAS,
            template="simple_white"
        )
        fig.update_layout(xaxis_title="Mês", yaxis_title="Eventos", legend_title="Ano")
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if "AnoMes" in df_historico.columns and df_historico["AnoMes"].notna().any():
        st.markdown("### 📌 Eventos por Ano-Mês")
        ordem_meses = (
            df_historico.dropna(subset=["Ano", "Mes_Num", "AnoMes"])
            [["Ano", "Mes_Num", "AnoMes"]]
            .drop_duplicates()
            .sort_values(["Ano", "Mes_Num"])["AnoMes"]
            .tolist()
        )

        eventos_anomes = (
            df_historico.dropna(subset=["AnoMes"])
            .groupby("AnoMes")
            .size()
            .reset_index(name="Eventos")
        )

        eventos_anomes["AnoMes"] = pd.Categorical(
            eventos_anomes["AnoMes"],
            categories=ordem_meses,
            ordered=True
        )
        eventos_anomes = eventos_anomes.sort_values("AnoMes")
        eventos_anomes["AnoMes_str"] = eventos_anomes["AnoMes"].astype(str)

        fig = px.bar(
            eventos_anomes,
            x="AnoMes",
            y="Eventos",
            color="AnoMes_str",
            text_auto=True,
            color_discrete_sequence=PALETA_BARRAS,
            template="simple_white"
        )
        fig.update_layout(xaxis_title="Ano-Mês", yaxis_title="Eventos", showlegend=False)
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if df_filtrado.empty:
        st.warning("Nenhum registro encontrado com os filtros aplicados.")
        st.stop()

    st.subheader("📌 Indicadores Operacionais")

    total_eventos = len(df_filtrado)
    total_publico = int(df_filtrado[coluna_publico].sum()) if coluna_publico and coluna_publico in df_filtrado.columns else 0
    total_cidades = df_filtrado[coluna_cidade].nunique() if coluna_cidade and coluna_cidade in df_filtrado.columns else 0
    total_comandos = df_filtrado[coluna_comando].nunique() if coluna_comando and coluna_comando in df_filtrado.columns else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🎉 Eventos", total_eventos)
    col2.metric("👥 Público Previsto", f"{total_publico:,}".replace(",", "."))
    col3.metric("🏙️ Cidades", total_cidades)
    col4.metric("🚔 Comandos", total_comandos)

    if coluna_natureza:
        st.subheader("🎭 Eventos por Natureza")
        natureza_eventos = (
            df_filtrado.dropna(subset=[coluna_natureza])
            .groupby(coluna_natureza)
            .size()
            .reset_index(name="Eventos")
            .sort_values(by="Eventos", ascending=False)
        )
        fig = px.pie(
            natureza_eventos,
            names=coluna_natureza,
            values="Eventos",
            hole=0.45,
            color_discrete_sequence=PALETA_PIZZA,
            template="simple_white"
        )
        fig.update_traces(
            textinfo="percent+label",
            marker=dict(line=dict(color="white", width=2))
        )
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if coluna_tipo_publico:
        st.subheader("🥧 Tipo de Público")
        pizza_publico = (
            df_filtrado.dropna(subset=[coluna_tipo_publico])
            .groupby(coluna_tipo_publico)
            .size()
            .reset_index(name="Quantidade")
            .sort_values(by="Quantidade", ascending=False)
        )
        fig = px.pie(
            pizza_publico,
            names=coluna_tipo_publico,
            values="Quantidade",
            hole=0.45,
            color_discrete_sequence=PALETA_PIZZA,
            template="simple_white"
        )
        fig.update_traces(
            textinfo="percent+label",
            marker=dict(line=dict(color="white", width=2))
        )
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if coluna_cobranca and coluna_cobranca in df_filtrado.columns:
        st.subheader("🎟️ Tipo de Cobrança de Ingresso")

        pizza_cobranca = (
            df_filtrado.dropna(subset=[coluna_cobranca])
            .groupby(coluna_cobranca)
            .size()
            .reset_index(name="Quantidade")
            .sort_values(by="Quantidade", ascending=False)
        )

        if not pizza_cobranca.empty:
            fig = px.pie(
                pizza_cobranca,
                names=coluna_cobranca,
                values="Quantidade",
                hole=0.45,
                color_discrete_sequence=["#61DDAA", "#F6BD16"],
                template="simple_white"
            )
            fig.update_traces(
                textinfo="percent+label",
                marker=dict(line=dict(color="white", width=2))
            )
            fig = aplicar_estilo(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há dados válidos para o campo de cobrança com os filtros atuais.")

    if coluna_comando:
        st.subheader("🚔 Comandos com Mais Eventos")
        comando_eventos = (
            df_filtrado.groupby(coluna_comando)
            .size()
            .reset_index(name="Eventos")
            .sort_values(by="Eventos", ascending=False)
        )
        comando_eventos["categoria_cor"] = comando_eventos[coluna_comando].astype(str)

        fig = px.bar(
            comando_eventos,
            x=coluna_comando,
            y="Eventos",
            color="categoria_cor",
            text_auto=True,
            color_discrete_sequence=PALETA_BARRAS,
            template="simple_white"
        )
        fig.update_layout(showlegend=False)
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if coluna_cidade:
        st.subheader("🏙️ Cidades com Mais Eventos")
        cidade_eventos = (
            df_filtrado.groupby(coluna_cidade)
            .size()
            .reset_index(name="Eventos")
            .sort_values(by="Eventos", ascending=False)
            .head(15)
        )
        cidade_eventos["categoria_cor"] = cidade_eventos[coluna_cidade].astype(str)

        fig = px.bar(
            cidade_eventos,
            x=coluna_cidade,
            y="Eventos",
            color="categoria_cor",
            text_auto=True,
            color_discrete_sequence=PALETA_BARRAS,
            template="simple_white"
        )
        fig.update_layout(showlegend=False)
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if coluna_evento and coluna_publico:
        st.subheader("🎯 Eventos com Maior Público Previsto")
        eventos_publico = (
            df_filtrado.groupby(coluna_evento)[coluna_publico]
            .sum()
            .reset_index()
            .sort_values(by=coluna_publico, ascending=False)
            .head(10)
        )
        eventos_publico["categoria_cor"] = eventos_publico[coluna_evento].astype(str)

        fig = px.bar(
            eventos_publico,
            x=coluna_evento,
            y=coluna_publico,
            color="categoria_cor",
            text_auto=".2s",
            color_discrete_sequence=PALETA_BARRAS,
            template="simple_white"
        )
        fig.update_layout(showlegend=False)
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if coluna_publico:
        st.subheader("📊 Distribuição do Público Previsto")
        fig = px.histogram(
            df_filtrado,
            x=coluna_publico,
            nbins=20,
            color_discrete_sequence=[COR_HISTOGRAMA],
            template="simple_white"
        )
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if coluna_comando and coluna_publico:
        st.subheader("🚔 Público Previsto por Comando")
        publico_comando = (
            df_filtrado.groupby(coluna_comando)[coluna_publico]
            .sum()
            .reset_index()
            .sort_values(by=coluna_publico, ascending=False)
        )
        publico_comando["categoria_cor"] = publico_comando[coluna_comando].astype(str)

        fig = px.bar(
            publico_comando,
            x=coluna_comando,
            y=coluna_publico,
            color="categoria_cor",
            text_auto=".2s",
            color_discrete_sequence=PALETA_BARRAS,
            template="simple_white"
        )
        fig.update_layout(showlegend=False)
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if coluna_cidade:
        st.subheader("🥧 Participação das Cidades")
        pizza_cidade = (
            df_filtrado.groupby(coluna_cidade)
            .size()
            .reset_index(name="Eventos")
            .sort_values(by="Eventos", ascending=False)
            .head(10)
        )
        fig = px.pie(
            pizza_cidade,
            names=coluna_cidade,
            values="Eventos",
            hole=0.45,
            color_discrete_sequence=PALETA_PIZZA,
            template="simple_white"
        )
        fig.update_traces(
            textinfo="percent+label",
            marker=dict(line=dict(color="white", width=2))
        )
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if coluna_cidade and coluna_publico:
        st.subheader("📈 Média de Público por Cidade")
        media_cidade = (
            df_filtrado.groupby(coluna_cidade)[coluna_publico]
            .mean()
            .reset_index()
            .sort_values(by=coluna_publico, ascending=False)
            .head(15)
        )
        fig = px.line(
            media_cidade,
            x=coluna_cidade,
            y=coluna_publico,
            markers=True,
            template="simple_white"
        )
        fig.update_traces(
            line=dict(color=COR_LINHA_1, width=3),
            marker=dict(size=7, color=COR_LINHA_1)
        )
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🌡️ Intensidade de Público por Cidade")
        mapa_df = (
            df_filtrado[[coluna_cidade, coluna_publico]]
            .dropna()
            .groupby(coluna_cidade)[coluna_publico]
            .sum()
            .reset_index()
        )

        fig_heat = go.Figure(
            data=go.Heatmap(
                z=[mapa_df[coluna_publico].tolist()],
                x=mapa_df[coluna_cidade].astype(str).tolist(),
                y=["Público"],
                colorscale="Blues"
            )
        )
        fig_heat.update_layout(height=450, template="simple_white")
        fig_heat = aplicar_estilo(fig_heat)
        st.plotly_chart(fig_heat, use_container_width=True)

    if coluna_data and coluna_publico and df_filtrado[coluna_data].notna().any():
        st.subheader("📈 Evolução do Público")
        evolucao = (
            df_filtrado.dropna(subset=[coluna_data])
            .groupby(coluna_data)[coluna_publico]
            .sum()
            .reset_index()
            .sort_values(coluna_data)
        )
        fig = px.line(
            evolucao,
            x=coluna_data,
            y=coluna_publico,
            markers=True,
            template="simple_white"
        )
        fig.update_traces(
            line=dict(color=COR_LINHA_2, width=3),
            marker=dict(size=7, color=COR_LINHA_2)
        )
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if coluna_publico:
        st.subheader("🔥 TOP 10 - Público Previsto")
        top_publico = df_filtrado.sort_values(by=coluna_publico, ascending=False).head(10)
        st.dataframe(top_publico, use_container_width=True)

    st.subheader("🧠 Análise Inteligente Operacional")

    if coluna_publico and not df_filtrado[coluna_publico].dropna().empty:
        maior_publico = df_filtrado.loc[df_filtrado[coluna_publico].idxmax()]
        menor_publico = df_filtrado.loc[df_filtrado[coluna_publico].idxmin()]
        media_geral = round(df_filtrado[coluna_publico].mean(), 2)
        mediana = round(df_filtrado[coluna_publico].median(), 2)

        nome_maior = maior_publico[coluna_evento] if coluna_evento else "N/D"
        nome_menor = menor_publico[coluna_evento] if coluna_evento else "N/D"

        st.info(f"""
🚨 Evento com MAIOR público previsto:
{nome_maior} ({int(maior_publico[coluna_publico]):,} pessoas)

⚠️ Evento com MENOR público previsto:
{nome_menor} ({int(menor_publico[coluna_publico]):,} pessoas)

📊 Média geral de público:
{media_geral:,.0f} pessoas

📈 Mediana de público:
{mediana:,.0f} pessoas

🎉 Total de eventos monitorados:
{len(df_filtrado)}

🏙️ Total de cidades:
{df_filtrado[coluna_cidade].nunique() if coluna_cidade else 0}

🚔 Total de comandos:
{df_filtrado[coluna_comando].nunique() if coluna_comando else 0}
""")

    if coluna_comando and coluna_publico:
        st.subheader("🏆 Ranking Operacional dos Comandos")
        ranking_operacional = (
            df_filtrado.groupby(coluna_comando)[coluna_publico]
            .agg(["sum", "mean", "count"])
            .reset_index()
        )
        ranking_operacional.columns = ["Comando", "Público Total", "Média Público", "Eventos"]
        st.dataframe(ranking_operacional, use_container_width=True)

    st.subheader("📄 Dados Operacionais")
    pesquisa_final = st.text_input("🔎 Pesquisar na tabela final", key="pesquisa_final")

    df_tabela = df_filtrado.copy()
    if pesquisa_final:
        df_tabela = df_tabela[
            df_tabela.astype(str)
            .apply(lambda x: x.str.contains(pesquisa_final, case=False, na=False))
            .any(axis=1)
        ]

    st.dataframe(df_tabela, use_container_width=True, height=450)

    csv = df_tabela.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="⬇️ Baixar CSV",
        data=csv,
        file_name="sao_joao_2026_filtrado.csv",
        mime="text/csv"
    )

    st.success(f"✅ Dashboard carregado com sucesso em {horario}")

except Exception as erro:
    st.error(f"Erro ao carregar dados: {erro}")
