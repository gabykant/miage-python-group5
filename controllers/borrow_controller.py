import html
from controllers.base_controller import BaseController
from models.borrow import BorrowModel
from models.book   import BookModel
from models.user   import UserModel

MAX_BORROWS = 3   # règle métier : max 3 emprunts par étudiant


class BorrowController(BaseController):

    def __init__(self):
        self.model        = BorrowModel()
        self.book_model   = BookModel()
        self.student_model = UserModel()

    # GET /borrows
    def index(self, req, params, qs):
        borrows  = self.model.find_all_with_details()
        students = self.student_model.find_students()
        books    = self.book_model.find_all()

        # Enrichir chaque livre avec ses exemplaires disponibles
        for book in books:
            borrowed       = self.model.count_active_by_book(book['id'])
            book['available'] = book['copies'] - borrowed

        self.render(req, 'borrows/index.html', {
            "page_active": "emprunts",
            "borrows":     borrows,
            "students":    students,
            "books":       [b for b in books if b['available'] > 0],
            "total":       len(borrows),
        })

    # POST /borrows
    def create(self, req, params, qs):
        data       = self.get_body(req)
        user_id    = html.escape(data.get('user_id',  '').strip())
        book_id    = html.escape(data.get('book_id',  '').strip())
        erreur     = None

        # ── Règle 1 : max 3 emprunts actifs ───────────────────────────────────
        active = self.model.count_active_by_student(user_id)
        if active >= MAX_BORROWS:
            erreur = f"Cet étudiant a déjà {MAX_BORROWS} emprunts en cours. Retour obligatoire avant nouvel emprunt."

        # ── Règle 1b : déjà ce livre en emprunt ───────────────────────────────
        elif self.model.student_already_has_book(user_id, book_id):
            erreur = "Cet étudiant a déjà emprunté ce livre."

        # ── Règle 3 : disponibilité du livre ──────────────────────────────────
        else:
            book    = self.book_model.find_by_id(book_id)
            borrowed = self.model.count_active_by_book(book_id)
            if not book:
                erreur = "Livre introuvable."
            elif borrowed >= book['copies']:
                erreur = f"Aucun exemplaire disponible pour \"{book['title']}\"."

        if erreur:
            borrows  = self.model.find_all_with_details()
            students = self.student_model.find_students()
            books    = self.book_model.find_all()
            for b in books:
                b['available'] = b['copies'] - self.model.count_active_by_book(b['id'])
            self.render(req, 'borrows/index.html', {
                "page_active": "emprunts",
                "borrows":     borrows,
                "students":    students,
                "books":       [b for b in books if b['available'] > 0],
                "total":       len(borrows),
                "erreur":      erreur,
            })
            return

        # ── Tout est OK → créer l'emprunt ─────────────────────────────────────
        self.model.create_borrow(user_id, book_id)
        self.redirect(req, '/borrows')

    # POST /borrows/:id/return
    def return_book(self, req, params, qs):
        self.model.return_book(params['id'])
        self.redirect(req, '/borrows')