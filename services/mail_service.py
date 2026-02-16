"""
services/mail_service.py — Envoi d'emails via SMTP
Utilisé pour relancer les étudiants avant la date limite.
"""

from dotenv import load_dotenv
from mailjet_rest import Client
import os

load_dotenv()

class MailService:

    def __init__(self):
        self.email  = os.getenv('MAIL_FROM')
        self.name   = os.getenv('MAIL_NAME')
        self.client = Client(
            auth=(os.getenv('MAILJET_API_KEY'), os.getenv('MAILJET_API_SECRET')),
            version='v3.1'
        )

    def send(self, to_email: str, subject: str, body_html: str):
        """Envoie un email HTML."""
        try:
            data = {
                'Messages': [
                    {
                        'From': {
                            'Email': self.email,
                            'Name': self.name
                        },
                        'To': [
                            {
                                'Email': to_email,
                            }
                        ],
                        'Subject': subject,
                        'HTMLPart': body_html
                    }
                ]
            }

            result = self.client.send.create(data=data)

            if result.status_code == 200:
                print(f"  [MAIL] Email envoyé à {to_email}")
                return True
            else:
                print(f"  [MAIL] Erreur Mailjet {result.status_code} : {result.json()}")
                return False

        except Exception as e:
            print(f"  [MAIL] Exception : {e}")
            return False

    def send_reminder(self, borrow: dict):
        """Envoie un email de rappel pour un emprunt qui expire dans 2 jours."""
        subject = f"Rappel : retour du livre \"{borrow['book_title']}\" dans 2 jours"
        body    = f"""
        <div style="font-family:sans-serif; max-width:600px; margin:0 auto;">
            <div style="background:#1a3a5c; color:#fff; padding:1.5rem; border-radius:8px 8px 0 0;">
                <h2>📚 Bibliothèque Universitaire</h2>
            </div>
            <div style="padding:1.5rem; border:1px solid #e2e8f0; border-radius:0 0 8px 8px;">
                <p>Bonjour <strong>{borrow['firstname']} {borrow['lastname']}</strong>,</p>
                <p>Nous vous rappelons que le livre suivant doit être retourné
                   <strong>dans 2 jours</strong> :</p>
                <div style="background:#f4f6f9; padding:1rem; border-radius:6px;
                            border-left:4px solid #2563eb; margin:1rem 0;">
                    <strong>{borrow['book_title']}</strong><br>
                    Date limite : <strong>{borrow['due_date']}</strong>
                </div>
                <p>Merci de retourner ce livre avant la date limite pour éviter
                   des pénalités.</p>
                <p style="color:#64748b; font-size:.85rem;">
                    Bibliothèque Universitaire — Service des emprunts
                </p>
            </div>
        </div>
        """
        return self.send(borrow['email'], subject, body)

    def send_password(self, user: dict, plain_password: str):
        """Envoie le mot de passe généré à l'étudiant après création de son compte."""
        subject = "Vos identifiants de connexion — Bibliothèque Universitaire"
        body    = f"""
        <div style="font-family:sans-serif; max-width:600px; margin:0 auto;">
            <div style="background:#1a3a5c; color:#fff; padding:1.5rem; border-radius:8px 8px 0 0;">
                <h2>Bibliothèque Université de Douala</h2>
            </div>
            <div style="padding:1.5rem; border:1px solid #e2e8f0; border-radius:0 0 8px 8px;">
                <p>Bonjour <strong>{user['firstname']} {user['lastname']}</strong>,</p>
                <p>Votre compte a été créé avec succès. Voici vos identifiants :</p>
                <div style="background:#f4f6f9; padding:1rem; border-radius:6px;
                            border-left:4px solid #2563eb; margin:1rem 0;">
                    <p><strong>Email :</strong> {user['email']}</p>
                    <p><strong>Mot de passe :</strong>
                        <code style="font-size:1.1rem;">{plain_password}</code>
                    </p>
                </div>
                <p style="color:#64748b; font-size:.85rem;">
                    Bibliothèque Université de Douala - Service des enregistrements
                </p>
            </div>
        </div>
        """
        return self.send(user['email'], subject, body)

# ── Instance globale ──────────────────────────────────────────────────────────
mail_service = MailService()