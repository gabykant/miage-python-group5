"""
database.py — Connexion MySQL (singleton)
Utilise mysql-connector-python.
Installation : pip install mysql-connector-python
"""
import mysql.connector
from mysql.connector import Error

class Database:
    """
    Singleton : une seule connexion partagée dans toute l'application.
    """
    _instance = None

    # ── Config ─────────────────────────────────────────────────────────────────
    CONFIG = {
        'host':     'localhost',
        'port':     3306,
        'database': 'python_miage',
        'user':     'root',
        'password': 'root',
        'charset':  'utf8mb4',
        'autocommit': False,
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connexion = None
        return cls._instance

    # ── Connexion ──────────────────────────────────────────────────────────────

    def connect(self):
        """Ouvre la connexion si elle n'est pas déjà ouverte."""
        try:
            if self._connexion is None or not self._connexion.is_connected():
                self._connexion = mysql.connector.connect(**self.CONFIG)
                print("  [DB] Connexion MySQL établie.")
        except Error as e:
            print(f"  [DB] Erreur de connexion : {e}")
            raise

    def get_connection(self):
        self.connect()
        return self._connexion

    def close(self):
        if self._connexion and self._connexion.is_connected():
            self._connexion.close()
            print("  [DB] Connexion MySQL fermée.")

    # ── Exécution de requêtes ──────────────────────────────────────────────────

    def execute(self, query, params=None):
        """
        Exécute INSERT / UPDATE / DELETE.
        Retourne le lastrowid.
        """
        conn   = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.lastrowid
        except Error as e:
            conn.rollback()
            print(f"  [DB] Erreur execute : {e}")
            raise
        finally:
            cursor.close()

    def fetch_one(self, query, params=None):
        """
        Exécute un SELECT et retourne une ligne sous forme de dict.
        """
        conn   = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except Error as e:
            print(f"  [DB] Erreur fetch_one : {e}")
            raise
        finally:
            cursor.close()

    def fetch_all(self, query, params=None):
        """
        Exécute un SELECT et retourne toutes les lignes sous forme de liste de dicts.
        """
        conn   = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Error as e:
            print(f"  [DB] Erreur fetch_all : {e}")
            raise
        finally:
            cursor.close()

# ── Instance globale ───────────────────────────────────────────────────────────
db = Database()