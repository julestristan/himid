import os

import streamlit as st

from src.cor_matrix import load_heatmap
from src.main import PORTEFEUILLE, client

st.set_page_config(page_title="Himid Dashboard", layout="wide")

# --- TITRE ---
st.title("🚀 Himid : How is my investment doing?")

# --- BARRE LATÉRALE (Le "Chatbot" et les réglages) ---
with st.sidebar:
    st.header("⚙️ Settings")
    period = st.selectbox("Période", ["1mo", "3mo", "6mo", "1y", "2y"])
    st.divider()
    st.header("AI Assistant")
    st.write("Click the button to analyze CorMatrix")
    analyze_button = st.button("Analyze CorMatrix")
    # Answer container
    chat_container = st.container()

tickers = list(PORTEFEUILLE.keys())

st.subheader(f"CorMatrix for given period: ({period})")

# Get data
path, df_corr = load_heatmap(tickers, period, f"st_heatmap_{period}.png")

if path and os.path.exists(path):
    st.image(path, use_container_width=True)

# AI Assistant to analyze diversification
if analyze_button and df_corr is not None:
    with chat_container, st.spinner("Analyzing..."):
        prompt = f"""
        Analyze this correlation matrix :
        {df_corr.round(2).to_string()}
        
        Within maximum 30 structured lines, give the strong and weak points
        of current diversification of the portfolio
        """
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
            )

            # --- AJOUT DU HIDE/SHOW ICI ---
            # L'argument expanded=True permet de l'ouvrir automatiquement à la génération
            with st.expander("📄 Toggle ON/OFF details", expanded=True):
                st.chat_message("assistant").write(
                    response.choices[0].message.content
                )

        except Exception as e: # noqa: BLE001
            st.error(f"Erreur : {e}")
