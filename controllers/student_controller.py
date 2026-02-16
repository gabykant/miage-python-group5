import html
from controllers.base_controller import BaseController
from models.user import UserModel
from services.mail_service import MailService

mail_service = MailService()

class StudentController(BaseController):

    def __init__(self):
        self.model = UserModel()

    # GET /students
    def index(self, req, params, qs):
        students = self.model.find_students()
        self.render(req, 'students/index.html', {
            "page_active": "students",
            "students":    students,
            "total":       len(students),
        })

    # GET /students/new
    def student_form(self, req, params, qs):
        self.render(req, 'students/add.html', {
            "page_active": "students",
            "student":     {},
            "erreurs":     [],
        })

    # POST /students
    def create(self, req, params, qs):
        data    = self.get_body(req)

        # Échapper les entrées (XSS)
        data = {k: html.escape(v.strip()) for k, v in data.items()}

        erreurs = self.model.validate(data)

        if not erreurs and self.model.email_exists(data.get('email', '')):
            erreurs.append("Cet email est déjà utilisé.")

        if erreurs:
            self.render(req, 'students/add.html', {
                "page_active": "students",
                "student":     data,
                "erreurs":     erreurs,
            })
            return

        # ── Créer le compte et récupérer le mot de passe généré ───────────────────
        user, plain_password = self.model.create_student(data)

        # ── Envoyer le mot de passe par mail ──────────────────────────────────────
        sent = mail_service.send_password(user, plain_password)
        if not sent:
            # Compte créé mais mail échoué — on prévient sans bloquer
            self.render(req, 'students/add.html', {
                "page_active": "students",
                "student":     {},
                "erreurs":     [],
                "warning":     f"Compte créé mais l'envoi du mail à {user['email']} a échoué.",
            })
            return
        self.redirect(req, '/students')
        return