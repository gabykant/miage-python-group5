from http.server import BaseHTTPRequestHandler, HTTPServer
import mimetypes
import os
from controllers.book_controller import BookController
from router import Router
from controllers.dashboard_controller import DashboardController
from controllers.auth_controller import AuthController
from controllers.student_controller import StudentController
from controllers.borrow_controller import BorrowController
from controllers.error_controller import ErrorController
from controllers.user_controller import UserController
from middleware.auth import check_auth

dashboard = DashboardController()
auth = AuthController()
book = BookController()
student = StudentController()
borrow = BorrowController()
errors = ErrorController()
users = UserController()

router = Router()

router.add_route('GET',  '/', dashboard.index)
router.add_route('GET',  '/login', auth.login_form)
router.add_route('POST', '/login', auth.login_submit)
router.add_route('POST', '/logout', auth.logout)
router.add_route('GET',  '/books', book.index)
router.add_route('GET',  '/books/add', book.add_form)
router.add_route('POST',  '/books/add', book.add_submit)
router.add_route('GET',  '/books/:id/edit', book.edit)
router.add_route('POST', '/books/:id', book.update)
router.add_route('POST', '/books/:id/delete', book.delete)
router.add_route('GET', '/books/:id', book.show)
router.add_route('GET',  '/students', student.index)
router.add_route('GET',  '/students/add', student.student_form)
router.add_route('POST',  '/students', student.create)
router.add_route('GET',  '/students/:id/edit', student.edit)
router.add_route('POST', '/students/:id', student.update)
router.add_route('POST', '/students/:id/delete', student.delete)
router.add_route('GET',  '/borrows', borrow.index)
router.add_route('POST',  '/borrows', borrow.create)
router.add_route('POST',  '/borrows/:id/return', borrow.return_book)
router.add_route('GET', '/forbidden', errors.forbidden)
router.add_route('GET', '/users', users.index)
router.add_route('GET',  '/users/add', users.new)
router.add_route('POST', '/users', users.create)
router.add_route('GET',  '/students/:id', student.show)
router.add_route('POST', '/students/:id/reset-password', student.reset_password)

HOST = '0.0.0.0'
PORT = int(os.environ.get("PORT", 8000))

class MainHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self._dispatch()

    def do_POST(self):
        self._dispatch()

    def _dispatch(self):
        # Séparer le path des query params (?page=1&q=python)
        path = self.path.split('?')[0]
        query_string = self.path.split('?')[1] if '?' in self.path else ''

        print(f"  >> {self.command} {path}") 

        if path.startswith('/assets/'):
            self._serve_static(path)
            return
        
        if not check_auth(self, path):
            return

        handler, params = router.resolve(self.command, path)

        if handler:
            handler(self, params, query_string)
        else:
            self._send_404()

    def _serve_static(self, path):
        # /assets/css/app.css  →  assets/css/app.css  (chemin local)
        file_path = path.lstrip('/')

        if not os.path.isfile(file_path):
            self.send_response(404)
            self.end_headers()
            return

        # Détecter le bon Content-Type (css, js, png, woff2...)
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or 'application/octet-stream'

        with open(file_path, 'rb') as f:
            content = f.read()

        self.send_response(200)
        self.send_header('Content-Type', mime_type)
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content)
        
    def _send_404(self):
        from template_engine2 import TemplateEngine
        engine = TemplateEngine()
        html = engine.render('errors/404.html', {"path": self.path})
        body = html.encode('utf-8')
        self.send_response(404)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Formater les logs serveur
        print(f"  [{self.command}] {self.path}  >>  {args[1]}")

if __name__ == '__main__':
    print(f"\n  Bibliothèque Université de Douala")
    server = HTTPServer((HOST, PORT), MainHandler)
    
    # print(f"Serveur démarré → http://localhost:{PORT}")
    # print(f"Ctrl+C pour arrêter\n")
    try:
        server.serve_forever()   # ← boucle d'écoute infinie
    except KeyboardInterrupt:
        print("\n  Serveur arrêté.")
        server.server_close()