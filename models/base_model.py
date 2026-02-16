"""
models/base_model.py — Model de base
Fournit les opérations CRUD communes à tous les models.
Chaque model fils définit : table, fields, required_fields.
"""

from models.database import Database

db = Database()

class BaseModel:

    table           = ''      # nom de la table MySQL
    fields          = []      # colonnes autorisées en écriture
    required_fields = []      # colonnes obligatoires

    # ── Lecture ────────────────────────────────────────────────────────────────

    def find_all(self, order_by=None):
        """Retourne tous les enregistrements."""
        sql = f"SELECT * FROM {self.table}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        return db.fetch_all(sql)

    def find_by_id(self, record_id):
        """Retourne un enregistrement par son ID."""
        sql = f"SELECT * FROM {self.table} WHERE id = %s"
        return db.fetch_one(sql, (record_id,))

    def find_where(self, conditions: dict, order_by=None):
        """
        Retourne les enregistrements correspondant aux conditions.
        Ex: find_where({"statut": "emprunte", "etudiant_id": 3})
        """
        clauses = ' AND '.join([f"{k} = %s" for k in conditions])
        values  = tuple(conditions.values())
        sql     = f"SELECT * FROM {self.table} WHERE {clauses}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        return db.fetch_all(sql, values)

    def search(self, column, term):
        """Recherche LIKE sur une colonne."""
        sql = f"SELECT * FROM {self.table} WHERE {column} LIKE %s"
        return db.fetch_all(sql, (f"%{term}%",))

    # ── Écriture ───────────────────────────────────────────────────────────────

    def create(self, data: dict):
        """
        Insère un nouvel enregistrement.
        Retourne l'ID inséré.
        """
        filtered = {k: v for k, v in data.items() if k in self.fields}
        columns  = ', '.join(filtered.keys())
        placeholders = ', '.join(['%s'] * len(filtered))
        sql = f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})"
        return db.execute(sql, tuple(filtered.values()))

    def update(self, record_id, data: dict):
        """Met à jour un enregistrement existant."""
        filtered = {k: v for k, v in data.items() if k in self.fields}
        if not filtered:
            return
        sets   = ', '.join([f"{k} = %s" for k in filtered])
        values = tuple(filtered.values()) + (record_id,)
        sql    = f"UPDATE {self.table} SET {sets} WHERE id = %s"
        db.execute(sql, values)

    def delete(self, record_id):
        """Supprime un enregistrement."""
        sql = f"DELETE FROM {self.table} WHERE id = %s"
        db.execute(sql, (record_id,))

    def count(self):
        """Compte le nombre total d'enregistrements."""
        result = db.fetch_one(f"SELECT COUNT(*) as total FROM {self.table}")
        return result['total'] if result else 0

    # ── Validation ─────────────────────────────────────────────────────────────

    def validate(self, data: dict):
        """
        Valide les champs requis.
        Retourne une liste d'erreurs (vide si tout est OK).
        """
        errors = []
        for field in self.required_fields:
            if not data.get(field, '').strip():
                errors.append(f"Le champ '{field}' est requis.")
        return errors