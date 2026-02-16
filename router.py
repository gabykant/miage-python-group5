
class Router:

    def __init__(self):
        # Liste de tuples (method, pattern, handler)
        self.routes = []

    def add_route(self, method, pattern, handler):
        self.routes.append((method.upper(), pattern, handler))

    def resolve(self, method, path):
        """
        Cherche le handler correspondant à (method, path).
        Retourne (handler, params) ou (None, {}).
        """
        for route_method, pattern, handler in self.routes:
            if route_method != method.upper():
                continue
            params = self._match(pattern, path)
            if params is not None:
                return handler, params
        return None, {}
    
    def _match(self, pattern, path):
        """
        Compare un pattern et un path segment par segment.
        /livres/:id  vs  /livres/42  →  {"id": "42"}
        /livres      vs  /livres     →  {}
        /livres      vs  /etudiants  →  None
        """
        p_parts = pattern.rstrip('/').split('/')
        r_parts = path.rstrip('/').split('/')

        if len(p_parts) != len(r_parts):
            return None

        params = {}
        for p, r in zip(p_parts, r_parts):
            if p.startswith(':'):
                params[p[1:]] = r       # segment dynamique
            elif p != r:
                return None             # segment fixe différent
        return params
    