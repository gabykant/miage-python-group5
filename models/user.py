import string
import secrets
from models.base_model import BaseModel
from models.database import Database
import bcrypt

db = Database()

class UserModel(BaseModel):
    table           = 'users'
    fields          = ['firstname', 'lastname', 'email', 'password', 'role',
                       'matricule', 'field_study', 'phone_number', 'speciality', 'level']
    required_fields = ['firstname', 'lastname', 'email', 'matricule']

    def find_students(self):
        """Retourne uniquement les étudiants."""
        return db.fetch_all(
            "SELECT * FROM users WHERE role = 'student' ORDER BY lastname"
        )

    def email_exists(self, email, exclude_id=None):
        sql    = "SELECT id FROM users WHERE email = %s"
        params = [email]
        if exclude_id:
            sql += " AND id != %s"
            params.append(exclude_id)
        return db.fetch_one(sql, params) is not None

    def create_student(self, data: dict):
        """Crée un étudiant avec mot de passe hashé."""
        plain_password   = self.generate_password()
        hashed           = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
        data['password'] = hashed.decode('utf-8')
        data['role']     = 'student'
        new_id = self.create(data)
        data['id'] = new_id
        return data, plain_password
    
    def generate_password(self, length=6) -> str:
        """Génère un mot de passe aléatoire sécurisé."""
        alphabet = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def count_students(self) -> int:
        result = db.fetch_one(
            "SELECT COUNT(*) as total FROM users WHERE role = 'student'"
        )
        return result['total'] if result else 0
    
    def find_bookkeepers(self):
        """Retourne uniquement les bookkeepers."""
        return db.fetch_all(
            "SELECT * FROM users WHERE role = 'bookkeeper' ORDER BY lastname"
        )
    
    def create_bookkeeper(self, data: dict) -> tuple:
        """Crée un bookkeeper avec mot de passe généré automatiquement."""
        plain_password   = self.generate_password()
        hashed           = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
        data['password'] = hashed.decode('utf-8')
        data['role']     = 'bookkeeper'

        new_id     = self.create(data)
        data['id'] = new_id

        return data, plain_password
    
    def find_recent_students(self, limit=5):
        """Derniers étudiants inscrits."""
        return db.fetch_all("""
            SELECT * FROM users
            WHERE role = 'student'
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))