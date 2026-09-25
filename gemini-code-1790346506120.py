import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione della pagina Streamlit
st.set_page_config(
    page_title="EOS Secondo Natura - Gestione Insoluti",
    page_icon="🌿",
    layout="wide"
)

# --- GESTIONE AUTENTICAZIONE ---
def check_login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<h2 style='text-align: center; color: #2E7D32;'>🌿 EOS Secondo Natura</h2>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center;'>Portale Gestione Crediti e Insoluti Forza Vendite</h4>", unsafe_allow_html=True)
        st.write("---")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                st.subheader("Accedi al Sistema")
                username = st.text_input("Utente")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Accedi")

                if submit:
                    if username == "Matteo" and password == "Menegazzo":
                        st.session_state.authenticated = True
                        st.success("Autenticazione riuscita!")
                        st.rerun()
                    else:
                        st.error("Username o Password errati.")
        return False
    return True

# --- INIZIALIZZAZIONE DATABASE IN MEMORIA ---
def init_data():
    if "orders_db" not in st.session_state:
        # Dati demo iniziali per EOS Secondo Natura
        st.session_state.orders_db = pd.DataFrame([
            {
                "ID Ordine": "ORD-2026-001",
                "Farmacia / Cliente": "Farmacia San Lorenzo",
                "Agente": "Matteo Menegazzo",
                "Data Fattura": "2026-07-15",
                "Importo (€)": 1450.00,
                "Scadenza": "2026-08-30",
                "Stato Pagamento": "Insoluto",
                "Note": "Sollecito inviato il 10/09"
            },
            {
                "ID Ordine": "ORD-2026-002",
                "Farmacia / Cliente": "Farmacia Centrale Padova",
                "Agente": "Matteo Menegazzo",
                "Data Fattura": "2026-08-01",
                "Importo (€)": 890.50,
                "Scadenza": "2026-09-15",
                "Stato Pagamento": "Insoluto",
                "Note": "Promesso bonifico fine mese"
            },
            {
                "ID Ordine": "ORD-2026-003",
                "Farmacia / Cliente": "Parafarmacia Natura & Salute",
                "Agente": "Giovanni Rossi",
                "Data Fattura": "2026-06-20",
                "Importo (€)": 2100.00,
                "Scadenza": "2026-07-31",
                "Stato Pagamento": "Pagato",
                "Note": "Incassato il 05/08"
            }
        ])

# --- APPLICAZIONE PRINCIPALE ---
if check_login():
    init_data()

    # Header Aziendale
    st.title("🌿 EOS Secondo Natura")
    st.caption("Supporto Rete Vendita — Monitoraggio Ordini e Stato Incassi")

    # Sidebar per azioni utente
    with st.sidebar:
        st.write("👤 **Utente collegato:** Matteo")
        st.write("💼 **Ruolo:** Agente / Commerciale")
        st.write("---")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

    # KPI Summary Cards
    df = st.session_state.orders_db
    total_insoluto = df[df["Stato Pagamento"] == "Insoluto"]["Importo (€)"].sum()
    count_insoluti = len(df[df["Stato Pagamento"] == "Insoluto"])
    total_incassato = df[df["Stato Pagamento"] == "Pagato"]["Importo (€)"].sum()

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Totale Scaduto / Insoluto", f"€ {total_insoluto:,.2f}", delta=f"{count_insoluti} ordini pendenti", delta_color="inverse")
    kpi2.metric("Totale Incassato", f"€ {total_incassato:,.2f}")
    kpi3.metric("Totale Pratiche Gestite", len(df))

    st.write("---")

    # Tabs di Navigazione
    tab_consulta, tab_inserimento, tab_aggiorna = st.tabs([
        "📋 Consulta Ordini e Insoluti", 
        "➕ Inserisci Nuovo Ordine / Insoluto", 
        "🔄 Aggiorna Stato Pagamento"
    ])

    # --- TAB 1: CONSULTAZIONE E FILTRI ---
    with tab_consulta:
        st.subheader("Elenco Ordini e Stato Crediti")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_stato = st.multiselect(
                "Filtra per Stato Pagamento:",
                options=["Insoluto", "Pagato"],
                default=["Insoluto"]
            )
        with col_f2:
            search_cliente = st.text_input("Cerca Farmacia o Cliente:")

        # Applicazione Filtri
        df_filtered = df[df["Stato Pagamento"].isin(filtro_stato)]
        if search_cliente:
            df_filtered = df_filtered[df_filtered["Farmacia / Cliente"].str.contains(search_cliente, case=False, na=False)]

        # Evidenziazione colore per gli insoluti
        def highlight_insoluti(val):
            color = '#FFCDD2' if val == 'Insoluto' else '#C8E6C9'
            return f'background-color: {color}'

        st.dataframe(
            df_filtered.style.map(highlight_insoluti, subset=['Stato Pagamento']),
            use_container_width=True,
            hide_index=True
        )

    # --- TAB 2: INSERIMENTO NUOVO INSOLUTO ---
    with tab_inserimento:
        st.subheader("Registra un Nuovo Ordine Insoluto")
        
        with st.form("new_order_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                id_ord = st.text_input("ID Ordine / Fattura", value=f"ORD-2026-0{len(df)+1:02d}")
                cliente = st.text_input("Ragione Sociale Farmacia / Cliente *")
                agente = st.text_input("Agente di Riferimento", value="Matteo Menegazzo")
                importo = st.number_input("Importo (€) *", min_value=0.0, step=50.0, format="%.2f")
            
            with col_b:
                data_fat = st.date_input("Data Fattura", datetime.today())
                scadenza = st.date_input("Data Scadenza Pagamento", datetime.today())
                stato = st.selectbox("Stato Iniziale", ["Insoluto", "Pagato"])
                note = st.text_area("Note / Solleciti effettuati", placeholder="Es. Inviata mail di richiamo...")

            submit_new = st.form_submit_button("💾 Salva Ordine")

            if submit_new:
                if not cliente or importo <= 0:
                    st.error("Compilare i campi obbligatori (Cliente e Importo).")
                else:
                    new_row = {
                        "ID Ordine": id_ord,
                        "Farmacia / Cliente": cliente,
                        "Agente": agente,
                        "Data Fattura": str(data_fat),
                        "Importo (€)": importo,
                        "Scadenza": str(scadenza),
                        "Stato Pagamento": stato,
                        "Note": note
                    }
                    st.session_state.orders_db = pd.concat([st.session_state.orders_db, pd.DataFrame([new_row])], ignore_index=True)
                    st.success(f"Ordine {id_ord} registrato con successo!")
                    st.rerun()

    # --- TAB 3: AGGIORNAMENTO STATO (PAGATO/INSOLUTO) ---
    with tab_aggiorna:
        st.subheader("Aggiorna Posizione Credito Cliente")
        
        # Selezione dell'ordine da modificare
        ordini_list = st.session_state.orders_db["ID Ordine"].tolist()
        if ordini_list:
            selected_id = st.selectbox("Seleziona l'ID Ordine da aggiornare:", ordini_list)
            
            # Recupero dati attuali
            idx = st.session_state.orders_db[st.session_state.orders_db["ID Ordine"] == selected_id].index[0]
            current_row = st.session_state.orders_db.loc[idx]

            st.info(f"**Cliente:** {current_row['Farmacia / Cliente']} | **Importo:** € {current_row['Importo (€)']:.2f} | **Stato Attuale:** {current_row['Stato Pagamento']}")

            col_edit1, col_edit2 = st.columns(2)
            with col_edit1:
                nuovo_stato = st.selectbox("Nuovo Stato:", ["Pagato", "Insoluto"], index=0 if current_row["Stato Pagamento"] == "Pagato" else 1)
            with col_edit2:
                nuove_note = st.text_area("Aggiorna Note:", value=current_row["Note"])

            if st.button("✅ Conferma Aggiornamento"):
                st.session_state.orders_db.at[idx, "Stato Pagamento"] = nuovo_stato
                st.session_state.orders_db.at[idx, "Note"] = nuove_note
                st.success(f"Ordine {selected_id} aggiornato a '{nuovo_stato}'!")
                st.rerun()