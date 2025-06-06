# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard Financeiro Pessoal para Iasmin",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Estilo CSS para o Tema Claro (Ajustado para Melhor Legibilidade e Fontes) ---
st.markdown(
    """
    <style>
    /* Cores de fundo geral */
    .stApp {
        background-color: #FDFDFD; /* Quase branco puro para o fundo principal */
        color: #333333; /* Cor de texto padrão mais escura para contraste */
    }

    /* Estilo da barra lateral */
    .stSidebar {
        background-color: #E0F7FA; /* Azul claro suave para a barra lateral */
        color: #333333; /* Texto padrão na sidebar */
    }
    .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4, .stSidebar h5, .stSidebar h6 {
        color: #004D40; /* Verde escuro para títulos na sidebar, para bom contraste */
    }

    /* Cores dos Títulos Principais no Conteúdo */
    h1 { color: #004D40; /* Verde escuro forte para o título principal */ }
    h2 { color: #004D40; /* Verde escuro forte para subtítulos */ }
    h3 { color: #00695C; /* Um tom de verde um pouco mais claro para h3 */ }
    h4, h5, h6 { color: #212121; /* Preto quase total para os demais títulos */ }
    
    /* Cores do texto do corpo */
    p, label, .stMarkdown {
        color: #424242; /* Cinza escuro para o texto do corpo, fácil de ler */
    }
    
    /* Cards de métricas */
    [data-testid="stMetric"] {
        background-color: #F0F4C3; /* Verde pastel muito claro para métricas */
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border: 1px solid #DCE775;
    }
    [data-testid="stMetric"] label {
        color: #004D40 !important; /* Cor do rótulo da métrica - Verde escuro com !important */
        font-size: 1.1em !important;
        font-weight: bold !important;
    }
    [data-testid="stMetricValue"] {
        color: #000000 !important; /* PRETO PURO com !important para máxima visibilidade */
        font-size: 1.2em !important; /* Tamanho da fonte ajustado */
        font-weight: bold !important;
    }

    /* Botões */
    .stButton>button {
        background-color: #81D4FA; /* Azul claro para botões */
        color: white;
        border-radius: 8px;
        border: none;
        padding: 12px 24px;
        font-weight: bold;
        transition: background-color 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        background-color: #4FC3F7; /* Azul um pouco mais escuro no hover */
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* Caixas de informação/sucesso/alerta */
    .stAlert {
        border-radius: 10px;
        padding: 15px;
    }
    .stInfo {
        background-color: #E0F7FA; /* Azul claro para info */
        color: #004D40; /* Texto verde escuro */
        border-left: 5px solid #29B6F6; /* Borda azul mais forte */
    }
    .stSuccess {
        background-color: #E8F5E9; /* Verde claro para sucesso */
        color: #1B5E20; /* Texto verde escuro */
        border-left: 5px solid #66BB6A; /* Borda verde mais forte */
    }
    .stWarning {
        background-color: #FFFDE7; /* Amarelo muito claro para warning */
        color: #FF6F00; /* Texto laranja */
        border-left: 5px solid #FFA726; /* Borda laranja mais forte */
    }

    /* Ajuste para o gráfico de pizza */
    .js-plotly-plot .plotly .scatterlayer .fills {
        fill-opacity: 0.9;
    }
    /* Estilo para a tabela de dados */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 5px rgba(0,0,0,0.08);
    }
    .dataframe th {
        background-color: #BBDEFB; /* Azul claro para cabeçalhos da tabela */
        color: #1A237E; /* Azul escuro para texto do cabeçalho */
        font-weight: bold;
    }
    .dataframe tr:nth-child(even) {
        background-color: #F5F5F5; /* Listras leves para legibilidade */
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- Funções de Ajuda para Gerenciamento de Dados ---

# Garante que a pasta 'data' exista
data_dir = "data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Caminhos dos arquivos ajustados para a pasta 'data/'
DATA_FILE = os.path.join(data_dir, "transactions.csv")
BILLS_FILE = os.path.join(data_dir, "bills.csv")


def create_empty_transactions_df():
    """Cria um DataFrame de transações vazio com os tipos de dados corretos."""
    df = pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Valor", "Descrição"])
    return df.astype({
        "Data": 'datetime64[ns]',
        "Tipo": str,
        "Categoria": str,
        "Valor": float,
        "Descrição": str
    })

def create_empty_bills_df():
    """Cria um DataFrame de contas a pagar vazio com os tipos de dados corretos."""
    df = pd.DataFrame(columns=["Descrição", "Valor", "Data de Vencimento", "Pago"])
    return df.astype({
        "Descrição": str,
        "Valor": float,
        "Data de Vencimento": 'datetime64[ns]',
        "Pago": bool
    })

@st.cache_data # Cache para carregar dados de transações (roda apenas se o arquivo muda ou o cache é limpo)
def load_data_from_csv():
    """Carrega o DataFrame de transações ou cria um vazio se não existir, garantindo tipos corretos."""
    try:
        df = pd.read_csv(DATA_FILE)
        
        df["Data"] = pd.to_datetime(df["Data"], format="%Y-%m-%d", errors='coerce')
        df = df.dropna(subset=['Data'])
        
        df["Valor"] = pd.to_numeric(df["Valor"], errors='coerce') 
        df = df.dropna(subset=['Valor'])
        
        return df.astype({
            "Data": 'datetime64[ns]',
            "Tipo": str,
            "Categoria": str,
            "Valor": float,
            "Descrição": str
        })

    except FileNotFoundError:
        return create_empty_transactions_df()
    except Exception as e:
        st.error(f"Erro ao carregar transactions.csv: {e}. Criando DataFrame vazio.")
        return create_empty_transactions_df()

def save_data(df):
    """Salva o DataFrame de transações no arquivo CSV e limpa o cache."""
    df_to_save = df.copy() 
    df_to_save['Data'] = df_to_save['Data'].dt.strftime('%Y-%m-%d') 
    df_to_save.to_csv(DATA_FILE, index=False)
    st.session_state.transactions_df = df 
    st.cache_data.clear() # Limpa o cache para que load_data_from_csv() releia o arquivo na próxima execução


@st.cache_data # Cache para carregar dados de contas (roda apenas se o arquivo muda ou o cache é limpo)
def load_bills_from_csv():
    """Carrega o DataFrame de contas a pagar ou cria um vazio se não existir, garantindo tipos corretos."""
    try:
        df = pd.read_csv(BILLS_FILE)
        
        df["Data de Vencimento"] = pd.to_datetime(df["Data de Vencimento"], format="%Y-%m-%d", errors='coerce')
        df = df.dropna(subset=['Data de Vencimento'])
        df["Valor"] = pd.to_numeric(df["Valor"], errors='coerce')
        df = df.dropna(subset=['Valor'])
        df["Pago"] = df["Pago"].astype(bool)
        return df.astype({
            "Descrição": str,
            "Valor": float,
            "Data de Vencimento": 'datetime64[ns]',
            "Pago": bool
        })
    except FileNotFoundError:
        return create_empty_bills_df()
    except Exception as e:
        st.error(f"Erro ao carregar bills.csv: {e}. Criando DataFrame vazio.")
        return create_empty_bills_df()

def save_bills(df):
    """Salva o DataFrame de contas a pagar no arquivo CSV e limpa o cache."""
    df_to_save = df.copy()
    df_to_save['Data de Vencimento'] = df_to_save['Data de Vencimento'].dt.strftime('%Y-%m-%d')
    df_to_save.to_csv(BILLS_FILE, index=False)
    st.session_state.bills_df = df 
    st.cache_data.clear() # Limpa o cache para que load_bills_from_csv() releia o arquivo na próxima execução


# Inicializa os DataFrames no st.session_state no início da execução do script
if "transactions_df" not in st.session_state:
    st.session_state.transactions_df = load_data_from_csv()
if "bills_df" not in st.session_state:
    st.session_state.bills_df = load_bills_from_csv()

# Acessa os DataFrames através do session_state em todo o script
transactions_df = st.session_state.transactions_df
bills_df = st.session_state.bills_df


# --- Variáveis de Estado da Sessão para Reserva de Viagem ---
if "travel_reserve" not in st.session_state:
    st.session_state.travel_reserve = 0.0


# --- CONTEÚDO DO DASHBOARD ---
st.title("Dashboard Financeiro Pessoal para Iasmin 👩‍⚕️")
st.markdown("Bem-vinda ao seu controle financeiro! Aqui você pode registrar suas receitas e despesas, acompanhar seu caixa e planejar suas viagens.")


# --- Sidebar para Adicionar Transações e Contas ---
with st.sidebar:
    # Adicionar imagem da Iasmin
    iasmin_image_path = "iasmin.jpeg"
    if os.path.exists(iasmin_image_path):
        st.image(iasmin_image_path, caption="Dra Iasmin Cardoso", use_container_width=True)
    else:
        st.warning(f"Imagem '{iasmin_image_path}' não encontrada. Certifique-se de que está na mesma pasta do 'app.py'.")

    st.header("Adicionar Nova Transação")
    with st.form("nova_transacao_form", clear_on_submit=True):
        data = st.date_input("Data", datetime.now())
        tipo = st.selectbox("Tipo", ["Receita", "Despesa", "Reserva para Viagem"])
        
        # LISTA DE CATEGORIAS PREDEFINIDAS
        core_categories = ["Alimentação", "Viagem", "Receita", "Salário", "Aluguel", "Outros"]
        
        # Obter categorias existentes do DataFrame (limpas de NaN e strings vazias)
        existing_categories_from_df = [
            str(cat) for cat in transactions_df["Categoria"].unique() 
            if pd.notna(cat) and str(cat).strip() != "" and str(cat).strip().lower() != 'nan'
        ]
        
        # Construir a lista de categorias para o selectbox
        selectbox_categories = []
        for cat in existing_categories_from_df:
            if cat not in core_categories:
                selectbox_categories.append(cat)
        
        selectbox_categories.extend(core_categories)
        selectbox_categories.append("Outra (especificar)")

        selected_category = st.selectbox("Categoria", selectbox_categories)
        
        custom_category = ""
        if selected_category == "Outra (especificar)":
            custom_category = st.text_input("Nova Categoria (digite aqui)")
            category_to_use = custom_category if custom_category else "Não Especificado"
        else:
            category_to_use = selected_category


        valor = st.number_input("Valor (R$)", min_value=0.01, format="%.2f")
        descricao = st.text_area("Descrição")

        submitted = st.form_submit_button("Adicionar Transação")
        if submitted:
            if selected_category == "Outra (especificar)" and not custom_category.strip():
                st.warning("Por favor, digite o nome da nova categoria ou selecione uma existente.")
                st.stop()
            
            new_transaction_data = {
                "Data": [data], 
                "Tipo": [tipo],
                "Categoria": [category_to_use], 
                "Valor": [float(valor)],
                "Descrição": [descricao],
            }
            
            new_row_df = pd.DataFrame(new_transaction_data).astype({
                "Data": 'datetime64[ns]',
                "Tipo": str,
                "Categoria": str,
                "Valor": float,
                "Descrição": str
            })
            
            current_df = st.session_state.transactions_df 
            
            new_df = pd.concat([current_df, new_row_df], ignore_index=True)
            save_data(new_df) 
            st.success("Transação adicionada com sucesso!")
            st.rerun()

    st.header("Registrar Nova Conta a Pagar")
    with st.form("nova_conta_form", clear_on_submit=True):
        bill_description = st.text_input("Descrição da Conta")
        bill_value = st.number_input("Valor da Conta (R$)", min_value=0.01, format="%.2f")
        bill_due_date = st.date_input("Data de Vencimento", datetime.now() + timedelta(days=30))

        bill_submitted = st.form_submit_button("Registrar Conta")
        if bill_submitted:
            new_bill_data = {
                "Descrição": [bill_description],
                "Valor": [float(bill_value)], 
                "Data de Vencimento": [bill_due_date], 
                "Pago": [False],
            }
            
            new_bill_df = pd.DataFrame(new_bill_data).astype({
                "Descrição": str,
                "Valor": float,
                "Data de Vencimento": 'datetime64[ns]',
                "Pago": bool
            })

            current_bills_df = st.session_state.bills_df 

            new_bills_df = pd.concat([current_bills_df, new_bill_df], ignore_index=True)
            save_bills(new_bills_df) 
            st.success("Conta a pagar registrada com sucesso!")
            st.rerun()

# --- Análise Financeira ---
st.header("Visão Geral Financeira")

df_sorted = transactions_df.sort_values(by="Data", ascending=True)

# --- Gráfico de Receitas e Despesas Acumuladas ao Longo do Tempo ---
st.subheader("Receitas e Despesas Acumuladas ao Longo do Tempo")

if not df_sorted.empty:
    min_available_date = df_sorted["Data"].min()
    max_available_date = df_sorted["Data"].max()
    
    try:
        default_start_date = min_available_date.date() if pd.notna(min_available_date) else datetime.now().replace(day=1).date() - timedelta(days=365)
    except: 
        default_start_date = datetime.now().replace(day=1).date() - timedelta(days=365) 
    
    try:
        default_end_date = max_available_date.date() if pd.notna(max_available_date) else datetime.now().date()
    except: 
        default_end_date = datetime.now().date()


    col_start_date, col_end_date = st.columns(2)
    with col_start_date:
        start_date_filter = st.date_input(
            "Data de Início", 
            value=default_start_date, 
            min_value=min_available_date.date() if pd.notna(min_available_date) else datetime(1900, 1, 1).date(),
            max_value=default_end_date,
            key="start_date_cumulative_graph"
        )
    with col_end_date:
        end_date_filter = st.date_input(
            "Data de Fim", 
            value=default_end_date, 
            min_value=start_date_filter, 
            max_value=datetime.now().date(),
            key="end_date_cumulative_graph"
        )

    df_filtered_by_date = df_sorted[(df_sorted["Data"].dt.date >= start_date_filter) & 
                                    (df_sorted["Data"].dt.date <= end_date_filter)].copy()

    if not df_filtered_by_date.empty:
        min_date_filtered = df_filtered_by_date["Data"].min()
        max_date_filtered = df_filtered_by_date["Data"].max()
        
        all_dates_filtered = pd.date_range(start=min_date_filtered, end=max_date_filtered, freq='D')

        daily_summary = df_filtered_by_date.groupby(df_filtered_by_date["Data"].dt.date).apply(
            lambda x: pd.Series({
                'Receita': x[x["Tipo"] == "Receita"]["Valor"].sum(),
                'Despesa': x[x["Tipo"] == "Despesa"]["Valor"].sum()
            })
        ).reset_index()
        daily_summary.columns = ['Data', 'Receita', 'Despesa']
        daily_summary['Data'] = pd.to_datetime(daily_summary['Data'])

        full_date_range = pd.DataFrame(all_dates_filtered, columns=['Data'])
        merged_df = pd.merge(full_date_range, daily_summary, on='Data', how='left').fillna(0)
        
        merged_df['Receita Acumulada'] = merged_df['Receita'].cumsum()
        merged_df['Despesa Acumulada'] = merged_df['Despesa'].cumsum()

        df_plot = merged_df.melt(id_vars=['Data'], value_vars=['Receita Acumulada', 'Despesa Acumulada'],
                                 var_name='Tipo de Valor', value_name='Valor Acumulado')
        
        fig_cumulative = px.line(
            df_plot,
            x="Data",
            y="Valor Acumulado",
            color="Tipo de Valor",
            title=f"Receitas e Despesas Acumuladas de {start_date_filter.strftime('%d/%m/%Y')} a {end_date_filter.strftime('%d/%m/%Y')}",
            labels={"Valor Acumulado": "Valor (R$)", "Data": "Data"},
            line_shape="linear",
            render_mode="svg",
            color_discrete_map={
                'Receita Acumulada': '#4CAF50', 
                'Despesa Acumulada': '#F44336'
            }
        )
        fig_cumulative.update_layout(hovermode="x unified")
        st.plotly_chart(fig_cumulative, use_container_width=True)
    else:
        st.info("Não há transações no período selecionado para gerar o gráfico acumulado.")
else:
    st.info("Adicione transações para ver o gráfico de receitas e despesas acumuladas.")


# Cálculo do Caixa (Receita total - Despesa total)
total_receita = transactions_df[transactions_df["Tipo"] == "Receita"]["Valor"].sum()
total_despesa_from_transactions = transactions_df[transactions_df["Tipo"] == "Despesa"]["Valor"].sum()
total_despesa_from_paid_bills = bills_df[bills_df["Pago"] == True]["Valor"].sum()
total_despesa = total_despesa_from_transactions + total_despesa_from_paid_bills

# Desconsidera o valor de "Reserva para Viagem" do caixa para o cálculo de fluxo
total_reserva_viagem_movimentado = transactions_df[transactions_df["Tipo"] == "Reserva para Viagem"]["Valor"].sum()
caixa_atual = total_receita - total_despesa - total_reserva_viagem_movimentado

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Receita Total", f"R$ {total_receita:,.2f}")
with col2:
    st.metric("Despesa Total", f"R$ {total_despesa:,.2f}")
with col3:
    st.metric("Caixa Atual", f"R$ {caixa_atual:,.2f}")
with col4:
    st.metric("Reserva Atual para Viagem", f"R$ {st.session_state.travel_reserve:,.2f}")


st.markdown("---")

# --- Média de Gastos Mensal (Agora incluindo despesas de transações e contas pagas) ---
st.subheader("Média de Gastos Mensal")

all_expenses_data = []

if not transactions_df.empty:
    df_exp_trans = transactions_df[transactions_df["Tipo"] == "Despesa"].copy()
    if not df_exp_trans.empty:
        df_exp_trans = df_exp_trans[['Data', 'Valor']].copy()
        all_expenses_data.append(df_exp_trans)

if not bills_df.empty:
    df_exp_bills = bills_df[bills_df["Pago"] == True].copy()
    if not df_exp_bills.empty:
        df_exp_bills = df_exp_bills[['Data de Vencimento', 'Valor']].rename(columns={'Data de Vencimento': 'Data'}).copy()
        all_expenses_data.append(df_exp_bills)

if all_expenses_data:
    combined_expenses_df = pd.concat(all_expenses_data, ignore_index=True)
    
    combined_expenses_df['Data'] = pd.to_datetime(combined_expenses_df['Data'], errors='coerce')
    combined_expenses_df = combined_expenses_df.dropna(subset=['Data'])
    combined_expenses_df['Valor'] = pd.to_numeric(combined_expenses_df['Valor'], errors='coerce')
    combined_expenses_df = combined_expenses_df.dropna(subset=['Valor'])

    if not combined_expenses_df.empty:
        combined_expenses_df["AnoMes"] = combined_expenses_df["Data"].dt.to_period("M")
        gastos_por_mes = combined_expenses_df.groupby("AnoMes")["Valor"].sum()

        if len(gastos_por_mes) > 0:
            media_gastos_mensal = gastos_por_mes.mean()
            st.info(f"Sua média de gastos mensais nos últimos **{len(gastos_por_mes)}** meses é de: **R$ {media_gastos_mensal:,.2f}**")
            
            # --- Gráfico de Despesas por Mês (Reativado e Usando Dados Combinados) ---
            st.markdown("### Total de Despesas por Mês")
            fig_monthly_expenses = px.bar(
                x=gastos_por_mes.index.astype(str),
                y=gastos_por_mes.values,
                labels={"x": "Mês", "y": "Valor (R$)"},
                title="Distribuição Mensal das Despesas (Transações + Contas Pagas)",
                text_auto=True,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_monthly_expenses, use_container_width=True)
        else:
            st.warning("Não há despesas registradas para calcular a média mensal.")
    else:
        st.warning("Não há despesas registradas para calcular a média mensal.")
else:
    st.warning("Não há despesas registradas para calcular a média mensal.")


st.markdown("---")

# --- Simulação de Aplicação Financeira (AGORA SEMPRE VISÍVEL) ---
st.header("Simulação de Aplicação Financeira")

# Removido o 'with st.expander("Calcule o crescimento do seu investimento"):'
# O conteúdo agora fica direto abaixo do cabeçalho da seção

col_inv_init, col_aporte = st.columns(2)
with col_inv_init:
    initial_investment = st.number_input("Investimento Inicial (R$)", min_value=0.0, value=1000.0, format="%.2f")
with col_aporte:
    monthly_contribution = st.number_input("Aporte Mensal (R$)", min_value=0.0, value=100.0, format="%.2f")

col_taxa, col_periodo = st.columns(2)
with col_taxa:
    annual_interest_rate_percent = st.number_input("Taxa de Juros Anual (%)", min_value=0.0, value=10.0, format="%.2f")
with col_periodo:
    investment_period_years = st.number_input("Período de Investimento (Anos)", min_value=1, value=5)

if st.button("Simular Crescimento"):
    if initial_investment <= 0 and monthly_contribution <= 0:
        st.warning("Por favor, insira um Investimento Inicial ou um Aporte Mensal.")
    else:
        monthly_interest_rate = (1 + annual_interest_rate_percent / 100)**(1/12) - 1
        total_months = investment_period_years * 12

        months = []
        invested_capital = []
        accumulated_capital = []

        current_accumulated = initial_investment
        total_invested = initial_investment

        for month in range(1, total_months + 1):
            if month > 1:
                current_accumulated += monthly_contribution
                total_invested += monthly_contribution
            
            current_accumulated *= (1 + monthly_interest_rate)
            
            months.append(month)
            invested_capital.append(total_invested)
            accumulated_capital.append(current_accumulated)

        simulation_df = pd.DataFrame({
            "Mês": months,
            "Capital Investido": invested_capital,
            "Capital Acumulado": accumulated_capital
        })

        df_plot_sim = simulation_df.melt(id_vars=['Mês'], 
                                         value_vars=['Capital Investido', 'Capital Acumulado'],
                                         var_name='Tipo de Capital', 
                                         value_name='Valor (R$)')
        
        fig_sim = px.line(
            df_plot_sim,
            x="Mês",
            y="Valor (R$)",
            color="Tipo de Capital",
            title="Simulação de Crescimento do Investimento",
            labels={"Valor (R$)": "Valor (R$)", "Mês": "Meses Decorridos"},
            color_discrete_map={
                'Capital Investido': '#66BB6A', 
                'Capital Acumulado': '#29B6F6'
            }
        )
        fig_sim.update_layout(hovermode="x unified")
        st.plotly_chart(fig_sim, use_container_width=True)

        st.markdown("#### Resumo da Simulação")
        final_invested = invested_capital[-1] if invested_capital else 0
        final_accumulated = accumulated_capital[-1] if accumulated_capital else 0
        total_interest_earned = final_accumulated - final_invested
        
        st.success(f"Após **{investment_period_years} anos** (ou {total_months} meses):")
        st.markdown(f"- Capital Total Investido: **R$ {final_invested:,.2f}**")
        st.markdown(f"- Capital Total Acumulado: **R$ {final_accumulated:,.2f}**")
        st.markdown(f"- Juros Ganhos: **R$ {total_interest_earned:,.2f}**")
        st.info(f"O seu capital cresceu **{(final_accumulated / final_invested - 1) * 100:,.2f}%** no período, se {(annual_interest_rate_percent):.2f}% de juros anuais forem mantidos.")

st.markdown("---")


# --- Reserva para Viagens ---
st.subheader("Planejamento de Viagens")

st.info(f"Seu total atual reservado para viagens é: **R$ {st.session_state.travel_reserve:,.2f}**")

st.markdown("Use a seção 'Adicionar Nova Transação' na barra lateral para adicionar ou retirar fundos da sua reserva de viagem, escolhendo o tipo 'Reserva para Viagem'.")
st.markdown("Quando você adiciona à reserva, esse valor é subtraído do seu 'Caixa Atual', e quando você 'retira' para uma viagem (registrando como despesa de viagem), ele é computado como despesa.")

reserva_viagem_transacoes = transactions_df[transactions_df["Tipo"] == "Reserva para Viagem"]["Valor"].sum()
st.session_state.travel_reserve = reserva_viagem_transacoes


st.markdown("---")

# --- Contas a Pagar ---
st.subheader("Contas a Pagar")

if not bills_df.empty:
    st.markdown("### Gerenciar Contas")
    st.info("Para **editar** uma conta, clique diretamente na célula da tabela e digite. Para **apagar** uma conta, clique no número da linha à esquerda para selecioná-la e pressione `Delete` ou `Backspace`.")
    
    bills_df_display = bills_df.copy()
    bills_df_display['Data de Vencimento'] = bills_df_display['Data de Vencimento'].dt.strftime('%d/%m/%Y')

    edited_bills_df = st.data_editor(
        bills_df_display,
        column_config={
            "Pago": st.column_config.CheckboxColumn(
                "Pago?",
                help="Marque para indicar que a conta foi paga",
                default=False,
            )
        },
        key="bills_data_editor",
        hide_index=False,
        num_rows="dynamic",
    )
    
    if 'bills_data_editor' in st.session_state and (
        st.session_state.bills_data_editor.get('edited_rows') or
        st.session_state.bills_data_editor.get('added_rows') or
        st.session_state.bills_data_editor.get('deleted_rows')
    ):
        
        updated_bills_df = bills_df.copy()

        for idx, row_dict in st.session_state.bills_data_editor['edited_rows'].items():
            for col, val in row_dict.items():
                if col == "Data de Vencimento":
                    updated_bills_df.loc[idx, col] = pd.to_datetime(val, format='%d/%m/%Y', errors='coerce')
                elif col == "Valor":
                    updated_bills_df.loc[idx, col] = pd.to_numeric(val, errors='coerce')
                else:
                    updated_bills_df.loc[idx, col] = val
        
        for row_dict in st.session_state.bills_data_editor['added_rows']:
            new_row_data = {
                "Descrição": row_dict.get("Descrição", ""),
                "Valor": pd.to_numeric(row_dict.get("Valor", 0), errors='coerce'),
                "Data de Vencimento": pd.to_datetime(row_dict.get("Data de Vencimento"), format='%d/%m/%Y', errors='coerce'),
                "Pago": row_dict.get("Pago", False),
            }
            new_row_df = pd.DataFrame([new_row_data]).astype(updated_bills_df.dtypes.to_dict())
            updated_bills_df = pd.concat([updated_bills_df, new_row_df], ignore_index=True)

        deleted_indices = st.session_state.bills_data_editor['deleted_rows']
        updated_bills_df = updated_bills_df.drop(deleted_indices).reset_index(drop=True)

        updated_bills_df = updated_bills_df.dropna(subset=['Data de Vencimento', 'Valor'])

        save_bills(updated_bills_df)
        st.success("Contas atualizadas com sucesso!")
        st.rerun()


    st.markdown("### Contas Pendentes")
    contas_pendentes = bills_df[bills_df["Pago"] == False].sort_values(by="Data de Vencimento")
    if not contas_pendentes.empty:
        st.dataframe(
            contas_pendentes.style.format({"Valor": "R$ {:.2f}", "Data de Vencimento": lambda x: x.strftime("%d/%m/%Y")}),
            use_container_width=True,
            hide_index=True,
        )
        total_a_pagar = contas_pendentes["Valor"].sum()
        st.warning(f"Total de contas pendentes: **R$ {total_a_pagar:,.2f}**")
    else:
        st.info("Nenhuma conta pendente. Tudo em dia! 🎉")

else:
    st.info("Nenhuma conta a pagar registrada ainda. Use a barra lateral para adicionar.")


st.markdown("---")

# --- Histórico de Transações ---
st.header("Histórico Detalhado de Transações")

if not transactions_df.empty:
    st.subheader("Filtrar e Gerenciar Transações")
    st.info("Para **editar** uma transação, clique diretamente na célula da tabela e digite. Para **apagar** uma transação, clique no número da linha à esquerda para selecioná-la e pressione `Delete` ou `Backspace`.")

    existing_categories_from_df = [
        str(cat) for cat in transactions_df["Categoria"].unique() 
        if pd.notna(cat) and str(cat).strip() != "" and str(cat).strip().lower() != 'nan'
    ]
    
    filter_categories_options = ["Todas as Categorias"]
    for cat in existing_categories_from_df:
        if cat not in core_categories:
            filter_categories_options.append(cat)
    
    filter_categories_options.extend(core_categories)

    selected_filter_category = st.selectbox("Selecione uma Categoria para Filtrar", filter_categories_options, key="filter_category_selectbox")

    df_filtered = transactions_df.copy()
    if selected_filter_category != "Todas as Categorias":
        df_filtered = df_filtered[df_filtered["Categoria"] == selected_filter_category]
    
    edited_transactions_df = st.data_editor(
        df_filtered.style.format({"Valor": "R$ {:.2f}", "Data": lambda x: x.strftime("%d/%m/%Y")}),
        use_container_width=True,
        hide_index=False,
        num_rows="dynamic",
        key="transactions_data_editor",
    )

    if 'transactions_data_editor' in st.session_state and (
        st.session_state.transactions_data_editor.get('edited_rows') or
        st.session_state.transactions_data_editor.get('added_rows') or
        st.session_state.transactions_data_editor.get('deleted_rows')
    ):

        updated_transactions_df = transactions_df.copy()

        for idx, row_dict in st.session_state.transactions_data_editor['edited_rows'].items():
            for col, val in row_dict.items():
                if col == "Data":
                    updated_transactions_df.loc[idx, col] = pd.to_datetime(val, format='%d/%m/%Y', errors='coerce')
                elif col == "Valor":
                    updated_transactions_df.loc[idx, col] = pd.to_numeric(val, errors='coerce')
                else:
                    updated_transactions_df.loc[idx, col] = val
        
        for row_dict in st.session_state.transactions_data_editor['added_rows']:
            new_row_data = {
                "Data": pd.to_datetime(row_dict.get("Data"), format='%d/%m/%Y', errors='coerce'),
                "Tipo": row_dict.get("Tipo", ""),
                "Categoria": row_dict.get("Categoria", ""),
                "Valor": pd.to_numeric(row_dict.get("Valor", 0), errors='coerce'),
                "Descrição": row_dict.get("Descrição", ""),
            }
            new_row_df = pd.DataFrame([new_row_data]).astype(updated_transactions_df.dtypes.to_dict())
            updated_transactions_df = pd.concat([updated_transactions_df, new_row_df], ignore_index=True)

        deleted_indices = st.session_state.transactions_data_editor['deleted_rows']
        updated_transactions_df = updated_transactions_df.drop(deleted_indices).reset_index(drop=True)

        updated_transactions_df = updated_transactions_df.dropna(subset=['Data', 'Valor'])

        save_data(updated_transactions_df)
        st.success("Transações atualizadas com sucesso!")
        st.rerun()

    st.markdown("### Despesas por Categoria (Todas as Transações)")
    df_despesas_categorias = transactions_df[transactions_df["Tipo"] == "Despesa"]
    if not df_despesas_categorias.empty:
        fig_pie = px.pie(
            df_despesas_categorias,
            values="Valor",
            names="Categoria",
            title="Distribuição das Despesas por Categoria",
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Adicione despesas para ver a distribuição por categoria.")

else:
    st.info("Nenhuma transação registrada ainda. Use a barra lateral para adicionar receitas e despesas.")

# --- Footer ---
st.markdown("---")
st.markdown("Controle suas finanças, viva seus sonhos!")
