# imported libraries
import yfinance as yf
import himid_core
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
import os
from mistralai import Mistral

try:
    import config
except ImportError:
    config = None

api_key = os.getenv("MISTRALAI_API_KEY") or (config.MISTRALAI_API_KEY if config else None)
if api_key:
    client = Mistral(api_key=api_key)
else:
    client = None

# Configuration Portfolio
# CW8.PA: ticker MSCI World on Euronext Paris
PORTEFEUILLE = {
    "AI.PA": (158.63, 3),
    "DCAM.PA": (5.59, 45),
    "ASML.AS": (1189.12, 1),
    "ASM.AS": (717.17, 1),
    "BESI.AS": (165.27, 1),
    "SU.PA": (249.49, 2),
    "RI.PA": (80.44, 5),
    "ITP.PA": (25.33, 10),
    "SAN.PA": (81.10, 3),
    "TTE.PA": (63.08, 3),
    "BNP.PA": (92.52, 2),
    "EDEN.PA": (17.83, 10),
    "CA.PA": (14.94, 10),
    "ACA.PA": (18.52, 6),
    "UBI.PA": (4.21, 25),
    "ALO.PA": (26.75, 4)
}


def analyser_actus(ticker, roi):
    if not client: return "Analyse IA indisponible."
    
    try:
        t = yf.Ticker(ticker)
        news = t.news
        titres = [n.get('title') or n.get('headline') for n in news[:3]] if news else []
        
        prompt = f"L'action {ticker} a varié de {roi:.2f}%. Actus: {titres}. Explique pourquoi en une phrase courte en français."

        # Appel à Mistral (Modèle Small ou NeMo, très efficaces)
        chat_response = client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        return chat_response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Note : Variation de {roi:.2f}% sur {ticker}."

def generer_rapport():
    corps_mail = f"Bonjour, \n\n Voici de le rapport Himid du {(datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')}\n\n"
    total_profit_global = 0

    for ticker, (prix_achat, qte) in PORTEFEUILLE.items():
        try:
            # 1. Retrieve prices
            t = yf.Ticker(ticker)
            prix_actuel = t.fast_info['last_price']
            # 2. Use .rs library for computations
            roi, profit = himid_core.compute_performance(prix_achat, prix_actuel, qte)
            total_profit_global += profit
            if abs(roi) > 0.01: # Analyse presque tout pour tester
                print(f"DEBUG: Analyse en cours pour {ticker}...")
                analyse = analyser_actus(ticker, roi)
                corps_mail += f"🧠 Analyse : {analyse}\n"
            
            # 3. Suitable format for a mail
            statut = "📈" if profit >= 0 else "📉"
            corps_mail += f"{statut} {ticker}:\n"
            corps_mail += f"   Actuel: {prix_actuel:.2f}€ | Achat: {prix_achat:.2f}€\n"
            corps_mail += f"   ROI: {roi:.2f}% | Gain: {profit:.2f}€\n\n"
            
        except Exception as e:
            corps_mail += f"⚠️ Erreur sur {ticker}: {e}\n\n"

    corps_mail += f"------------------------------\n"
    corps_mail += f"💰 PROFIT TOTAL : {total_profit_global:.2f}€\n"
    return corps_mail

def envoyer_mail(contenu):
    sender = os.getenv("EMAIL_SENDER") or (config.EMAIL_SENDER if config else None)
    password = os.getenv("EMAIL_PASSWORD") or (config.EMAIL_PASSWORD if config else None)
    receiver = os.getenv("EMAIL_RECEIVER") or (config.EMAIL_RECEIVER if config else None)

    if not sender or not password:
        print("❌ Erreur: Identifiants email manquants")
        return

    msg = EmailMessage()
    msg.set_content(contenu)
    msg['Subject'] = f"Himid - Rapport du {(datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')}"
    msg['From'] = sender
    msg['To'] = receiver

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

if __name__ == "__main__":
    print("🚀 Calcul en cours avec le moteur Rust...")
    rapport = generer_rapport()
    print(rapport)
    print("📧 Envoi du mail...")
    envoyer_mail(rapport)
    print("✅ Terminé !")