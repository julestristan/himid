# imported libraries
import yfinance as yf
import himid_core
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
import os
#from mistralai import Mistral
from openai import OpenAI

try:
    import config
except ImportError:
    config = None

api_key = os.getenv("OPENAI_API_KEY") or (config.OPENAI_API_KEY if config else None)
client = OpenAI(api_key=api_key) if api_key else None

''' For MISTRALAI
api_key = os.getenv("MISTRALAI_API_KEY") or (config.MISTRALAI_API_KEY if config else None)
if api_key:
    client = Mistral(api_key=api_key)
else:
    client = None
'''


# Configuration Portfolio
PORTEFEUILLE = {
    "AI.PA": (165.95, 10),
    "ASML.AS": (1189.12, 1),
    "DCAM.PA": (5.53, 145),
    "ASM.AS": (717.17, 1),
    "PSP5.PA": (51.43,11),
    "SU.PA": (249.49, 2),
    "MC.PA": (540.32,1),
    "RI.PA": (80.44, 5),
    "ACA.PA": (18.30, 21),
    "STMPA.PA": (26.09,10),
    "EL.PA": (258.40,1),
    "ITP.PA": (25.33, 10),
    "SAN.PA": (81.10, 3),
    "TTE.PA": (63.08, 3),
    "BNP.PA": (92.52, 2),
    "DSY.PA": (18.13, 10),
    "EDEN.PA": (17.83, 10),
    "BESI.AS": (165.27, 1),
    "ABCA.PA": (5.54, 30),
    "CA.PA": (14.94, 10),
    "ALO.PA": (26.75, 4),
    "UBI.PA": (4.21, 25)
}


def analyser_actus(ticker, var_jour):
    if not client: return "Analyse IA indisponible."
    
    try:
        t = yf.Ticker(ticker)
        news = t.news
        titres = [n.get('title') or n.get('headline') for n in news[:5]] if news else []
        prompt = f"""
        Tu es un expert financier. Analyse la variation de {var_jour:.2f}% de l'action {ticker}.
        Voici les titres d'actualité récents : {titres}.

        INSTRUCTION : En te basant PRIORITAIREMENT sur ces titres (ou sur le contexte du secteur si les titres sont vides), explique la raison de ce mouvement en une seule phrase courte et percutante. 
        Ne dis PAS que tu n'as pas d'infos en temps réel, utilise les données fournies ci-dessus.
        """        
        '''
        # Appel à Mistral (Modèle Small ou NeMo, très efficaces)
        chat_response = client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        return chat_response.choices[0].message.content.strip()
        '''
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Note : Variation de {var_jour:.2f}% sur {ticker}."

def generer_rapport():
    corps_mail = f"Bonjour, \n\n Voici de le rapport Himid du {(datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')}\n\n"
    total_profit_global = 0

    for ticker, (prix_achat, qte) in PORTEFEUILLE.items():
        try:
            t = yf.Ticker(ticker)
            # 1. Performance Globale (Ton moteur Rust)
            prix_actuel = t.fast_info['last_price']
            roi_global, profit = himid_core.compute_performance(prix_achat, prix_actuel, qte)
            
            # 2. Performance du jour (Pour l'IA)
            # On récupère le % de variation sur la séance
            var_jour = t.info.get('regularMarketChangePercent', 0)
            total_profit_global += profit
            # On n'appelle l'IA que si l'action a bougé AUJOURD'HUI (> 1.5%)
            # car c'est ça que l'actualité explique.
            analyse = ""
            if abs(var_jour) > 1.5:
                analyse = analyser_actus(ticker, var_jour) # On passe la variation du jour à l'IA

            # 3. Formatage du mail
            statut = "📈" if profit >= 0 else "📉"
            corps_mail += f"{statut} {ticker} :\n"
            corps_mail += f"  Variation du jour : {var_jour:.2f}%\n"
            corps_mail += f"  Performance Globale (ROI & Profit): {roi_global:.2f}% ({profit:.2f}€)\n"
            if analyse:
                corps_mail += f"   🧠 Pourquoi ça bouge aujourd'hui ({var_jour:.2f}%) :\n {analyse}\n"
            corps_mail += "\n"
            
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