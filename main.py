# imported libraries
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn
import himid_core
import smtplib
from email.message import EmailMessage
import mimetypes
from datetime import datetime, timedelta
import os
from cor_matrix import *
#from mistralai import Mistral
from openai import OpenAI

# import config if run locally
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
PERIOD_CORMATRIX = ["1mo","12mo"]
PORTEFEUILLE = {
    "AI.PA": (165.95, 10),
    "ASML.AS": (1189.12, 1),
    "DCAM.PA": (5.49, 277),
    "ASM.AS": (717.17, 1),
    "PSP5.PA": (51.43,11),
    "SU.PA": (246.96, 3),
    "MC.PA": (540.32,1),
    "RI.PA": (80.44, 5),
    "ACA.PA": (18.30, 21),
    "STMPA.PA": (26.09,10),
    "EL.PA": (247.60,2),
    "ITP.PA": (25.33, 10),
    "FDJU.PA": (25.61, 10),
    "SAN.PA": (81.10, 3),
    "TTE.PA": (63.08, 3),
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
        titres = [n.get('title') or n.get('headline') for n in news[:3]] if news else []
        prompt = f"""
        Tu es un expert financier. Analyse la variation de {var_jour:.2f}% de l'action {ticker}.
        Voici les titres d'actualité récents : {titres}.

        INSTRUCTION : En te basant PRIORITAIREMENT sur ces titres (ou sur le contexte du secteur si les titres sont vides), explique la raison de ce mouvement en une seule phrase courte et percutante.
        Ne sois pas trop vague en disant que c'est des tendances de marché, soit factuel par rapport à
        un aspect clé qui a déclencher la variation du prix de l'action et qui cause la variation.
        Appuies toi au maximum sur les news récentes
        Si tu as vraiment aucune idée, ne fais pas de commentaire pour ce titre
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
            max_tokens=150
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
            if abs(var_jour) > 3.5:
                analyse = analyser_actus(ticker, var_jour) # On passe la variation du jour à l'IA

            # 3. Formatage du mail
            statut = "📈" if profit >= 0 else "📉"
            corps_mail += f"{statut} {ticker} :\n"
            corps_mail += f"  Variation du jour : {var_jour:.2f}%\n"
            corps_mail += f"  Prix du jour : {prix_actuel:.2f}€\n"
            corps_mail += f"  Quantité et PRU : {qte} à {prix_achat:.2f}€ l'unité\n"
            corps_mail += f"  En portefeuille: {qte*prix_actuel:.2f}€\n"
            corps_mail += f"  Performance Globale (ROI & Profit): {roi_global:.2f}% ({profit:.2f}€)\n"
            if analyse:
                corps_mail += f"🧠 Pourquoi ça bouge aujourd'hui ({var_jour:.2f}%) :\n {analyse}\n"
            corps_mail += "\n"
  
        except Exception as e:
            corps_mail += f"⚠️ Erreur sur {ticker}: {e}\n\n"
    image_paths = []
    for period in PERIOD_CORMATRIX:
        try:
            tickers_list = list(PORTEFEUILLE.keys())
            # Load CorMatrix
            path = load_heatmap(tickers_list, period, f"CorMatrix_{period}")[0]
            if path:
                image_paths.append(path)
        except Exception as e:
            print(f"⚠️ CorMatrix failed to build : {e}")
    pct_profit_global = 100 * total_profit_global / sum(prix * quantite for prix, quantite in PORTEFEUILLE.values())
    corps_mail += f"------------------------------\n"
    corps_mail += f"💰 PROFIT TOTAL : {total_profit_global:.2f}€\n"
    corps_mail += f"💰 PROFIT POURCENTAGE : {pct_profit_global:.2f}%\n"
    return corps_mail, image_paths

def envoyer_mail(contenu, image_paths=None):
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
    if image_paths:
        for path in image_paths:
            if path and os.path.exists(path):
                with open(path, 'rb') as f:
                    file_data = f.read()
                    ctype, encoding = mimetypes.guess_type(path)
                    if ctype is None or encoding is not None:
                        ctype = 'application/octet-stream'
                    maintype, subtype = ctype.split('/', 1)
                    
                    msg.add_attachment(
                        file_data,
                        maintype=maintype,
                        subtype=subtype,
                        filename=os.path.basename(path)
                    )

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

if __name__ == "__main__":
    print("🚀 Calcul en cours avec le moteur Rust...")
    rapport, paths_image = generer_rapport()
    print(rapport)
    print("📧 Envoi du mail...")
    envoyer_mail(rapport,paths_image)
    print("✅ Terminé !")