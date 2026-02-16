"""
session.py — Gestionnaire de sessions maison
Les sessions sont stockées en mémoire (dict).
Chaque session est identifiée par un cookie "session_id".
"""

import uuid
import time

# ── Stockage en mémoire ────────────────────────────────────────────────────────
# { session_id: { "user_id": 1, "nom": "Alice", "expires_at": 1234567890 } }
_sessions = {}

SESSION_DURATION = 3600   # 1 heure en secondes
COOKIE_NAME      = "session_id"


class SessionManager:

    # ── Créer une session ──────────────────────────────────────────────────────

    def create(self, data: dict) -> str:
        """
        Crée une nouvelle session avec les données utilisateur.
        Retourne le session_id à placer dans le cookie.
        """
        session_id = str(uuid.uuid4())
        _sessions[session_id] = {
            **data,
            "expires_at": time.time() + SESSION_DURATION
        }
        return session_id

    # ── Lire une session ───────────────────────────────────────────────────────

    def get(self, req) -> dict | None:
        """
        Lit la session depuis le cookie de la requête.
        Retourne le dict de session ou None si absente / expirée.
        """
        session_id = self._get_cookie(req, COOKIE_NAME)
        if not session_id:
            return None

        session = _sessions.get(session_id)
        if not session:
            return None

        # Session expirée ?
        if time.time() > session["expires_at"]:
            self.destroy(session_id)
            return None

        return session

    # ── Détruire une session ───────────────────────────────────────────────────

    def destroy(self, session_id: str):
        """Supprime la session (logout)."""
        _sessions.pop(session_id, None)

    def destroy_from_req(self, req):
        """Détruit la session de la requête courante."""
        session_id = self._get_cookie(req, COOKIE_NAME)
        if session_id:
            self.destroy(session_id)

    # ── Écrire le cookie dans la réponse ──────────────────────────────────────

    def set_cookie(self, req, session_id: str):
        """Écrit le cookie Set-Cookie dans la réponse HTTP."""
        req.send_header(
            'Set-Cookie',
            f"{COOKIE_NAME}={session_id}; HttpOnly; Path=/; Max-Age={SESSION_DURATION}"
        )

    def clear_cookie(self, req):
        """Efface le cookie côté navigateur."""
        req.send_header(
            'Set-Cookie',
            f"{COOKIE_NAME}=; HttpOnly; Path=/; Max-Age=0"
        )

    # ── Lecture du cookie depuis la requête ───────────────────────────────────

    def _get_cookie(self, req, name: str) -> str | None:
        """Parse l'en-tête Cookie et retourne la valeur du cookie demandé."""
        raw = req.headers.get('Cookie', '')
        for part in raw.split(';'):
            part = part.strip()
            if '=' in part:
                k, v = part.split('=', 1)
                if k.strip() == name:
                    return v.strip()
        return None


# ── Instance globale ───────────────────────────────────────────────────────────
session_manager = SessionManager()