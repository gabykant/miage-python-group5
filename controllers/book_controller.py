
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