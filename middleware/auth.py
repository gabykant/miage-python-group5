"""
middleware/auth.py — Middleware d'authentification
Intercepte chaque requête AVANT le controller.
Si aucune session valide → redirect /login.
"""

from session import session_manager

# Routes accessibles sans être connecté
PUBLIC_ROUTES = ['/login', '/static']

# Routes réservées à certains rôles
PROTECTED_ROUTES = {
    '/books/add':   ['admin', 'bookkeeper'],
    '/students': ['admin', 'bookkeeper'],
    '/students/add': ['admin', 'bookkeeper'],
    '/students/edit': ['admin', 'bookkeeper'],
    '/students/delete': ['admin', 'bookkeeper'],
    '/users':   ['admin'],
}

def auth_required(handler_func):
    """
    Décorateur appliqué à chaque handler de controller.
    Vérifie la session avant d'exécuter le controller.
    """
    def wrapper(controller_instance, req, params, qs):
        session = session_manager.get(req)
        if not session:
            _redirect_login(req)
            return
        # Injecte la session dans la requête pour que le controller y accède
        req.session = session
        return handler_func(controller_instance, req, params, qs)
    return wrapper


def check_auth(req, path: str) -> bool:
    """
    Vérifie si la requête a une session valide.
    Utilisé dans main.py pour protéger TOUTES les routes d'un coup.
    Retourne True si la requête peut continuer, False si redirigée.
    """

    if path.startswith('/login'):
        session = session_manager.get(req)
        if session:
            _redirect_dashboard(req)
            return False
        return True  # pas de session → laisse accéder au login
    
    # Les routes publiques passent toujours
    for public in PUBLIC_ROUTES:
        if path.startswith(public):
            return True

    # Vérifier la session
    session = session_manager.get(req)
    if session:
        req.session = session   # disponible dans tous les controllers
        return True
    
    # Vérification des rôles pour les routes protégées
    for route, roles in PROTECTED_ROUTES.items():
        if path.startswith(route):
            if session and session['role'] in roles:
                return True
            else:
                _redirect_forbidden(req)  # Pas le bon rôle → redirect dashboard
                return False

    # Pas de session → redirect login
    _redirect_login(req)
    return False


def _redirect_login(req):
    req.send_response(302)
    req.send_header('Location', '/login')
    req.send_header('Content-Length', '0')
    req.end_headers()

def _redirect_dashboard(req):
    req.send_response(302)
    req.send_header('Location', '/')
    req.send_header('Content-Length', '0')
    req.end_headers()

def _redirect_forbidden(req):
    req.send_response(302)
    req.send_header('Location', '/forbidden')
    req.send_header('Content-Length', '0')
    req.end_headers()