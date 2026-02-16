import json
from controllers.base_controller import BaseController
from models.book import BookModel
from models.borrow import BorrowModel
from models.user import UserModel

class DashboardController(BaseController):
    
    def __init__(self):
        self.borrow_model = BorrowModel()
        self.book_model   = BookModel()
        self.user_model   = UserModel()

    def index(self, req, params, qs):
        session = getattr(req, 'session', {})
        role    = session.get('role', '')
        user_id = session.get('user_id')

        # ── Dashboard admin / bookkeeper ───────────────────────────────────────
        if role in ['admin', 'bookkeeper']:

            # Stats graphique — convertir en JSON pour Chart.js
            stats       = self.borrow_model.stats_last_30_days()
            chart_labels = json.dumps([str(s['day']) for s in stats])
            chart_data   = json.dumps([s['total']    for s in stats])

            # self.render(req, 'dashboard.html', {
            #     "page_active":  "home",
            #     "nb_books":     self.book_model.count(),
            #     "nb_students":  self.user_model.count_students(),
            #     "nb_borrows":   self.borrow_model.count_active(),
            #     "late_borrows": self.borrow_model.find_late_return(),
            # })

            self.render(req, 'dashboard.html', {
                "page_active":       "accueil",
                "nb_books":          self.book_model.count(),
                "nb_students":       self.user_model.count_students(),
                "nb_borrows":        self.borrow_model.count_active(),
                "nb_late":           self.borrow_model.count_late(),
                "nb_available":      self.book_model.count_available(),
                "late_borrows":      self.borrow_model.find_late_return(),
                "recent_books":      self.book_model.find_recent(),
                "recent_students":   self.user_model.find_recent_students(),
                "today_borrows":     self.borrow_model.find_today(),
                "chart_labels":      chart_labels,
                "chart_data":        chart_data,
            })

        # ── Dashboard étudiant ─────────────────────────────────────────────────
        else:
            active_borrows  = self.borrow_model.find_active_by_student(user_id)
            borrow_history  = self.borrow_model.find_history_by_student(user_id)
            self.render(req, 'dashboard_student.html', {
                "page_active":     "home",
                "active_borrows":  active_borrows,
                "borrow_history":  borrow_history,
                "nb_active":       len(active_borrows),
                "nb_history":      len(borrow_history),
            })

    # def index(self, req, params, query_string):
    #     self.render(req, 'dashboard.html',
    #         {
    #             'title': 'Dashboard',
    #             "page_active": "home",
    #         })

    def get(self):
        # Récupérer les données nécessaires pour le dashboard
        data = {
            'title': 'Dashboard',
            'user': 'John Doe',
            'stats': {
                'visits': 1234,
                'sales': 567,
                'revenue': 8900
            }
        }
        # Rendre la vue du dashboard avec les données
        self.render('dashboard.html', data)