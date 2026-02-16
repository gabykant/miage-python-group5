import html
from controllers.base_controller import BaseController
from models.user import UserModel
from services.mail_service import MailService

mail_service = MailService()

class UserController(BaseController):

    def __init__(self):
        self.model = UserModel()

    # GET /users
    def index(self, req, params, qs):
        bookkeepers = self.model.find_bookkeepers()
        self.render(req, 'users/index.html', {
            "page_active": "users",
            "users":       bookkeepers,
            "total":       len(bookkeepers),
        })

    # GET /users/add
    def new(self, req, params, qs):
        self.render(req, 'users/add.html', {
            "page_active": "users",
            "user":        {},
            "erreurs":     [],
        })

    # POST /users
    def create(self, req, params, qs):
        data    = self.get_body(req)
        data    = {k: html.escape(v.strip()) for k, v in data.items()}

        # Validation manuelle — seulement les 4 champs requis
        erreurs = []
        if not data.get('firstname'): erreurs.append("Le prénom est requis.")
        if not data.get('lastname'):  erreurs.append("Le nom est requis.")
        if not data.get('email'):     erreurs.append("L'email est requis.")

        if not erreurs and self.model.email_exists(data.get('email', '')):
            erreurs.append("Cet email est déjà utilisé.")

        if erreurs:
            self.render(req, 'users/add.html', {
                "page_active": "users",
                "user":        data,
                "erreurs":     erreurs,
            })
            return

        # Créer le compte et envoyer le mot de passe par mail
        user, plain_password = self.model.create_bookkeeper(data)
        mail_service.send_password(user, plain_password)

        self.redirect(req, '/users')