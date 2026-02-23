from models.base_model import BaseModel
from models.database import Database

db = Database()

class BorrowModel(BaseModel):
    table           = 'borrows'
    fields          = ['user_id', 'book_id', 'borrowed_at', 'due_date', 'returned_at']
    required_fields = ['user_id', 'book_id']

    # ── Règle 1 : compter les emprunts actifs d'un étudiant ───────────────────

    def count_active_by_student(self, user_id) -> int:
        """Retourne le nombre d'emprunts en cours pour un étudiant."""
        result = db.fetch_one("""
            SELECT COUNT(*) as total FROM borrows
            WHERE user_id = %s AND returned_at IS NULL
        """, (user_id,))
        return result['total'] if result else 0

    def student_already_has_book(self, user_id, book_id) -> bool:
        """Vérifie si l'étudiant a déjà ce livre en emprunt."""
        return db.fetch_one("""
            SELECT id FROM borrows
            WHERE user_id = %s AND book_id = %s AND returned_at IS NULL
        """, (user_id, book_id)) is not None

    # ── Règle 3 : disponibilité d'un livre ────────────────────────────────────

    def count_active_by_book(self, book_id) -> int:
        """Retourne le nombre d'exemplaires actuellement empruntés."""
        result = db.fetch_one("""
            SELECT COUNT(*) as total FROM borrows
            WHERE book_id = %s AND returned_at IS NULL
        """, (book_id,))
        return result['total'] if result else 0

    # ── Création d'un emprunt ─────────────────────────────────────────────────

    def create_borrow(self, user_id, book_id) -> int:
        """Crée un emprunt avec due_date = aujourd'hui + 7 jours."""
        return db.execute("""
            INSERT INTO borrows (user_id, book_id, borrowed_at, due_date)
            VALUES (%s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 7 DAY))
        """, (user_id, book_id))

    # ── Retour d'un livre ─────────────────────────────────────────────────────

    def return_book(self, borrow_id):
        db.execute("""
            UPDATE borrows SET returned_at = CURDATE()
            WHERE id = %s AND returned_at IS NULL
        """, (borrow_id,))

    # ── Liste complète avec détails ───────────────────────────────────────────

    def find_all_with_details(self):
        return db.fetch_all("""
            SELECT b.*,
                   u.firstname, u.lastname, u.email, u.matricule,
                   bk.title AS book_title, bk.author AS book_author,
                   bk.copies AS book_copies,
                   DATEDIFF(b.due_date, CURDATE()) AS days_remaining,
                   DATEDIFF(CURDATE(), b.due_date) AS days_late
            FROM borrows b
            JOIN users u  ON u.id  = b.user_id
            JOIN books bk ON bk.id = b.book_id
            WHERE b.returned_at IS NULL
            ORDER BY b.due_date ASC
        """)

    def find_by_student(self, user_id):
        return db.fetch_all("""
            SELECT b.*,
                   bk.title AS book_title, bk.author AS book_author,
                   DATEDIFF(b.due_date, CURDATE()) AS days_remaining,
                   DATEDIFF(CURDATE(), b.due_date) AS days_late
            FROM borrows b
            JOIN books bk ON bk.id = b.book_id
            WHERE b.user_id = %s AND b.returned_at IS NULL
            ORDER BY b.due_date ASC
        """, (user_id,))

    # ── Règle 4 : étudiants à relancer (due_date dans 2 jours) ───────────────

    def find_due_in_two_days(self):
        """Retourne les emprunts dont la date limite est dans exactement 2 jours."""
        return db.fetch_all("""
            SELECT b.*,
                   u.firstname, u.lastname, u.email, u.matricule,
                   bk.title AS book_title
            FROM borrows b
            JOIN users u  ON u.id  = b.user_id
            JOIN books bk ON bk.id = b.book_id
            WHERE b.returned_at IS NULL
              AND DATEDIFF(b.due_date, CURDATE()) = 2
        """)
    
    def find_active_by_student(self, user_id):
        """Emprunts en cours d'un étudiant."""
        return db.fetch_all("""
            SELECT b.*,
                bk.title  AS book_title,
                bk.author AS book_author,
                DATEDIFF(b.due_date, CURDATE()) AS days_remaining,
                DATEDIFF(CURDATE(), b.due_date) AS days_late
            FROM borrows b
            JOIN books bk ON bk.id = b.book_id
            WHERE b.user_id = %s AND b.returned_at IS NULL
            ORDER BY b.due_date ASC
        """, (user_id,))

    def find_history_by_student(self, user_id):
        """Historique complet des emprunts d'un étudiant."""
        return db.fetch_all("""
            SELECT b.*,
                bk.title  AS book_title,
                bk.author AS book_author,
                DATEDIFF(b.returned_at, b.borrowed_at) AS days_kept
            FROM borrows b
            JOIN books bk ON bk.id = b.book_id
            WHERE b.user_id = %s AND b.returned_at IS NOT NULL
            ORDER BY b.returned_at DESC
        """, (user_id,))
    
    def count_active(self) -> int:
        result = db.fetch_one(
            "SELECT COUNT(*) as total FROM borrows WHERE returned_at IS NULL"
        )
        return result['total'] if result else 0
    
    def find_late_return(self):
        """Retourne les emprunts dont la date limite est dépassée."""
        return db.fetch_all("""
            SELECT b.*,
                u.firstname, u.lastname, u.email, u.matricule,
                bk.title  AS book_title,
                bk.author AS book_author,
                DATEDIFF(CURDATE(), b.due_date) AS days_late
            FROM borrows b
            JOIN users u  ON u.id  = b.user_id
            JOIN books bk ON bk.id = b.book_id
            WHERE b.returned_at IS NULL
            AND b.due_date < CURDATE()
            ORDER BY days_late DESC
        """)
    
    def find_recent(self, limit=5):
        """Derniers emprunts créés."""
        return db.fetch_all("""
            SELECT b.*,
                u.firstname, u.lastname,
                bk.title AS book_title
            FROM borrows b
            JOIN users u  ON u.id  = b.user_id
            JOIN books bk ON bk.id = b.book_id
            ORDER BY b.created_at DESC
            LIMIT %s
        """, (limit,))

    def find_today(self):
        """Emprunts créés aujourd'hui."""
        return db.fetch_all("""
            SELECT b.*,
                u.firstname, u.lastname,
                bk.title AS book_title
            FROM borrows b
            JOIN users u  ON u.id  = b.user_id
            JOIN books bk ON bk.id = b.book_id
            WHERE DATE(b.created_at) = CURDATE()
            ORDER BY b.created_at DESC
        """)

    def count_late(self) -> int:
        """Compte les emprunts en retard."""
        result = db.fetch_one("""
            SELECT COUNT(*) as total FROM borrows
            WHERE returned_at IS NULL AND due_date < CURDATE()
        """)
        return result['total'] if result else 0

    def stats_last_30_days(self):
        """Emprunts par jour sur les 30 derniers jours."""
        return db.fetch_all("""
            SELECT DATE(created_at) as day, COUNT(*) as total
            FROM borrows
            WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY DATE(created_at)
            ORDER BY day ASC
        """)
    
    def find_active_by_book(self, book_id):
        """Emprunts en cours pour un livre donné."""
        return db.fetch_all("""
            SELECT b.*,
                u.firstname, u.lastname, u.matricule,
                DATEDIFF(b.due_date, CURDATE()) AS days_remaining,
                DATEDIFF(CURDATE(), b.due_date) AS days_late
            FROM borrows b
            JOIN users u ON u.id = b.user_id
            WHERE b.book_id = %s AND b.returned_at IS NULL
            ORDER BY b.due_date ASC
        """, (book_id,))