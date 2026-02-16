from models.base_model import BaseModel
from models.database import Database

db = Database()

class BookModel(BaseModel):
    table           = 'books'
    fields          = ['title', 'author', 'isbn', 'year', 'genre', 'copies']
    required_fields = ['title', 'author', 'isbn']

    def find_all(self, order_by='title'):
        return super().find_all(order_by=order_by)

    def search(self, term):
        sql = """
            SELECT * FROM books
            WHERE title LIKE %s OR author LIKE %s OR isbn LIKE %s OR genre LIKE %s
            ORDER BY title
        """
        like = f"%{term}%"
        return db.fetch_all(sql, (like, like, like, like))
    
    def count_available(self) -> int:
        """Nombre total d'exemplaires disponibles."""
        result = db.fetch_one("""
            SELECT SUM(b.copies) - COUNT(bo.id) as total
            FROM books b
            LEFT JOIN borrows bo ON bo.book_id = b.id AND bo.returned_at IS NULL
        """)
        return result['total'] if result and result['total'] else 0

    def find_recent(self, limit=5):
        """Derniers livres ajoutés."""
        return db.fetch_all("""
            SELECT * FROM books
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))