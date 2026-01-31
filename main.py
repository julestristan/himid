import os
import yfinance as yf
import himid_core  # Ton module Rust compilé
import smtplib
from email.message import EmailMessage
from datetime import datetime
import config

# Configuration Portfolio
# CW8.PA est le ticker pour le MSCI World sur Euronext Paris
PORTEFEUILLE = {
    "BTC-USD": (30000.0, 0.05),
    "AAPL": (150.0, 10),
    "CW8.PA": (430.0, 5)
}

def generer_rapport():
    corps_mail = f"--- Rapport Himid - {datetime.now().strftime('%d/%m/%Y %H:%M')} ---\n\n"
    total_profit_global = 0

    for ticker, (prix_achat, qte) in PORTEFEUILLE.items():
        try:
            # 1. Récupérer le prix en temps réel
            t = yf.Ticker(ticker)
            prix_actuel = t.fast_info['last_price']
            
            # 2. Utiliser le moteur RUST pour le calcul
            roi, profit = himid_core.compute_performance(prix_achat, prix_actuel, qte)
            total_profit_global += profit
            
            # 3. Formater la ligne
            statut = "📈" if profit >= 0 else "📉"
            corps_mail += f"{statut} {ticker}:\n"
            corps_mail += f"   Actuel: {prix_actuel:.2f} | Achat: {prix_achat:.2f}\n"
            corps_mail += f"   ROI: {roi:.2f}% | Gain: {profit:.2f}$\n\n"
            
        except Exception as e:
            corps_mail += f"⚠️ Erreur sur {ticker}: {e}\n\n"

    corps_mail += f"------------------------------\n"
    corps_mail += f"💰 PROFIT TOTAL : {total_profit_global:.2f}$\n"
    return corps_mail

def envoyer_mail(contenu):
    msg = EmailMessage()
    msg.set_content(contenu)
    msg['Subject'] = f"📊 Himid : Ton point finance du jour"
    msg['From'] = config.EMAIL_SENDER
    msg['To'] = config.EMAIL_RECEIVER

    # Connexion sécurisée au serveur SMTP de Google
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(config.EMAIL_SENDER, config.EMAIL_PASSWORD)
        smtp.send_message(msg)

if __name__ == "__main__":
    print("🚀 Calcul en cours avec le moteur Rust...")
    rapport = generer_rapport()
    
    print(rapport) # Pour voir le résultat dans ton terminal
    
    print("📧 Envoi du mail...")
    envoyer_mail(rapport)
    print("✅ Terminé !")