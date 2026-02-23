
import html
from controllers.base_controller import BaseController
from models.book import BookModel

class BookController(BaseController):

    def __init__(self):
        # super().__init__(request_handler)
        self.model = BookModel()

    def index(self, req, params, query_string):
        books = self.model.find_all()
        self.render(req, 'books/index.html',
            {
                'title': 'Books',
                "page_active": "books",
                "books": books
            })
        
    def get(self):
        # Récupérer les données nécessaires pour la page des livres
        data = {
            'title': 'Books',
            'books': [
                {'id': 1, 'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald'},
                {'id': 2, 'title': 'To Kill a Mockingbird', 'author': 'Harper Lee'},
                {'id': 3, 'title': '1984', 'author': 'George Orwell'},
            ]
        }
        # Rendre la vue des livres avec les données
        self.render('books/index.html', data)

    def add_form(self, req, params, query_string):
        self.render(req, 'books/add.html',
            {
                'title': 'Add Book',
                "page_active": "books",
            })

    def add_submit(self, req, params, query_string):
        body = self.get_body(req)
        title = body.get('title', [''])[0]
        author = body.get('author', [''])[0]

        # Ici, vous ajouteriez le livre à votre base de données
        print(f"Adding book: {title} by {author}")

        self.redirect(req, '/books')

    # GET /books/:id/edit
    def edit(self, req, params, qs):
        book = self.model.find_by_id(params['id'])
        
        if not book:
            self.render(req, 'errors/404.html', {}, status=404)
            return
        
        self.render(req, 'books/add.html', {
            "page_active": "livres",
            "book":        book,
            "action":      f"/books/{book['id']}",
            "titre":       f"Modifier — {book['title']}",
            "erreurs":     [],
        })

    # POST /books/:id — update
    def update(self, req, params, qs):
        data    = self.get_body(req)
        data    = {k: html.escape(v.strip()) for k, v in data.items()}
        
        book    = self.model.find_by_id(params['id'])
        if not book:
            self.render(req, 'errors/404.html', {}, status=404)
            return
        
        erreurs = self.model.validate(data)
        
        if erreurs:
            self.render(req, 'books/add.html', {
                "page_active": "livres",
                "book":        data,
                "action":      f"/books/{params['id']}",
                "titre":       "Modifier un livre",
                "erreurs":     erreurs,
            })
            return
        
        self.model.update(params['id'], data)
        self.redirect(req, '/books')

    # POST /books/:id/delete — supprimer
    def delete(self, req, params, qs):
        from models.borrow import BorrowModel
        borrow_model = BorrowModel()
        
        # Vérifier si le livre a des emprunts en cours
        active_count = borrow_model.count_active_by_book(params['id'])
        
        if active_count > 0:
            # Impossible de supprimer — emprunts en cours
            books  = self.model.find_all()
            genres = sorted(set(b['genre'] for b in books if b.get('genre')))
            
            self.render(req, 'books/index.html', {
                "page_active": "livres",
                "books":       books,
                "genres":      genres,
                "total":       len(books),
                "erreur":      f"Impossible de supprimer ce livre : {active_count} exemplaire(s) en cours d'emprunt.",
            })
            return
        
        self.model.delete(params['id'])
        self.redirect(req, '/books')