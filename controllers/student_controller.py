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
    
    # controllers/student_controller.py

    # GET /students/:id → afficher profil avec bouton reset
    def show(self, req, params, qs):
        student = self.model.find_by_id(params['id'])
        
        if not student:
            self.render(req, 'errors/404.html', {}, status=404)
            return
        
        # Récupérer les emprunts actifs de l'étudiant
        from models.borrow import BorrowModel
        borrow_model    = BorrowModel()
        active_borrows  = borrow_model.find_active_by_student(params['id'])
        
        self.render(req, 'students/show.html', {
            "page_active":    "students",
            "student":        student,
            "active_borrows": active_borrows,
        })

    # POST /students/:id/reset-password → réinitialiser le mot de passe
    def reset_password(self, req, params, qs):
        student = self.model.find_by_id(params['id'])
        
        if not student:
            self.render(req, 'errors/404.html', {}, status=404)
            return
        
        # Générer nouveau mot de passe
        new_password = self.model.reset_password(params['id'])
        
        # Envoyer par mail
        user = {
            "email":     student['email'],
            "firstname": student['firstname'],
            "lastname":  student['lastname'],
        }
        sent = mail_service.send_password(user, new_password)
        
        if sent:
            # Rediriger avec message de succès
            self.redirect(req, f"/students/{params['id']}?reset=success")
        else:
            self.redirect(req, f"/students/{params['id']}?reset=error")