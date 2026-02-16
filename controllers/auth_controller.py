import hashlib
from pydoc import html

import bcrypt
from controllers.base_controller import BaseController
from session import session_manager
from models.database import db

class AuthController(BaseController):

    def login_form(self, req, params, qs):
        self.render(req, 'login.html', {
            "titre": "Connexion",
            "erreur": None,
        })

    def login_submit(self, req, params, qs):
        data     = self.get_body(req)

        # ── 1. Échapper les entrées utilisateur (protection XSS) ───────────────
        email    = html.escape(data.get('email',    '').strip())
        password = html.escape(data.get('password', '').strip())

        # ── 2. Validation basique ──────────────────────────────────────────────
        if not email or not password:
            self.render(req, 'login.html', {
                "error": "Adresse email et mot de passe requis.",
            })
            return
        
        # ── 3. Vérification en base ────────────────────────────────────────────
        user = self._check_credentials(email, password)

        if not user:
            # Message volontairement vague (ne pas indiquer lequel est faux)
            self.render(req, 'login.html', {
                "error": "Adresse email ou mot de passe incorrect.",
            })
            return
        # ── 4. Créer la session ────────────────────────────────────────────────
        session_id = session_manager.create({
            "user_id": user['id'],
            "firstname": user['firstname'],
            "lastname": user['lastname'],
            "email":   user['email'],
            "role":    user['role'],
        })

        # ── 5. Écrire le cookie et rediriger vers le dashboard ─────────────────
        req.send_response(302)
        req.send_header('Location', '/')
        session_manager.set_cookie(req, session_id)
        req.send_header('Content-Length', '0')
        req.end_headers()

    def logout(self, req, params, qs):
        session_manager.destroy_from_req(req)
        req.send_response(302)
        req.send_header('Location', '/login')
        session_manager.clear_cookie(req)
        req.send_header('Content-Length', '0')
        req.end_headers()

    def _check_credentials(self, email, password):
        """
        Recherche l'utilisateur par email puis compare le hash du mot de passe.
        La requête SQL utilise un paramètre %s → protection contre l'injection SQL.
        """
        user = db.fetch_one(
            "SELECT * FROM users WHERE email = %s ",
            (email,)   # ← paramètre bindé, jamais interpolé dans la requête
        )

        if not user:
            return None
        
        hash_en_base = user['password']

        if isinstance(hash_en_base, str):
            hash_en_base = hash_en_base.encode('utf-8')

        # Comparer le hash SHA-256 du mot de passe saisi
        # hash_saisi = hashlib.sha256(password.encode('utf-8')).hexdigest()
        if not bcrypt.checkpw(password.encode('utf-8'), hash_en_base):
            return None

        return user