from jinja2 import Environment, FileSystemLoader
import os

class TemplateEngine:

    def __init__(self, templates_dir='templates'):
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=True   # ← protection XSS automatique
        )

    def render(self, template_name, context=None):
        template = self.env.get_template(template_name)
        return template.render(context or {})