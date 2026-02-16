"""
controllers/base_controller.py — Controller de base
Fournit les helpers : send_html, redirect, get_body, get_query_params
Tous les controllers héritent de cette classe.
"""

from template_engine2 import TemplateEngine
from urllib.parse import parse_qs
import json

engine = TemplateEngine(templates_dir='templates')


class BaseController:

    # ── Rendu HTML ─────────────────────────────────────────────────────────────

    def render(self, req, template, context=None, status=200):
        """Rend un template et envoie la réponse HTML."""
        ctx = context or {}
        # Injecter automatiquement les infos de session dans tous les templates
        session = getattr(req, 'session', {})
        role = session.get('role', '')
        ctx.setdefault('user_fullname',  session.get('firstname', '') + ' ' + session.get('lastname', ''))
        ctx.setdefault('user_role', session.get('role', ''))
        ctx.setdefault('user_id',   session.get('user_id', ''))
        # Variable calculée : is_staff = True si admin ou bookkeeper, False sinon (pour afficher les liens d'admin dans la navbar)
        # Variable calculée : is_admin = True si admin, False sinon (pour afficher les liens d'admin dans la navbar)
        ctx.setdefault('is_staff', role in ['admin', 'bookkeeper'])
        ctx.setdefault('is_admin', role == 'admin')
        html = engine.render(template, ctx)
        self._send_html(req, status, html)

    # ── Réponses HTTP ──────────────────────────────────────────────────────────

    def _send_html(self, req, status, html):
        body = html.encode('utf-8')
        req.send_response(status)
        req.send_header('Content-Type', 'text/html; charset=utf-8')
        req.send_header('Content-Length', len(body))
        req.end_headers()
        req.wfile.write(body)

    def redirect(self, req, location):
        """Redirection HTTP 302."""
        req.send_response(302)
        req.send_header('Location', location)
        req.send_header('Content-Length', '0')
        req.end_headers()

    def send_json(self, req, status, data):
        """Réponse JSON (utile pour les appels AJAX)."""
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        req.send_response(status)
        req.send_header('Content-Type', 'application/json; charset=utf-8')
        req.send_header('Content-Length', len(body))
        req.end_headers()
        req.wfile.write(body)

    # ── Lecture du corps de requête ────────────────────────────────────────────

    def get_body(self, req):
        """
        Lit et parse le body d'une requête POST (formulaire HTML).
        Retourne un dict {champ: valeur}.
        """
        length = int(req.headers.get('Content-Length', 0))
        if length == 0:
            return {}
        raw = req.rfile.read(length).decode('utf-8')
        parsed = parse_qs(raw)
        # parse_qs retourne {key: [val]} → on simplifie en {key: val}
        return {k: v[0] for k, v in parsed.items()}

    def get_query_params(self, query_string):
        """Parse les query params d'une URL (?page=1&q=python)."""
        if not query_string:
            return {}
        parsed = parse_qs(query_string)
        return {k: v[0] for k, v in parsed.items()}