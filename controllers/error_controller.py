from controllers.base_controller import BaseController

class ErrorController(BaseController):

    def forbidden(self, req, params, qs):
        self.render(req, 'errors/forbidden.html', {
            "titre": "Accès refusé",
        }, status=403)