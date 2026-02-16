"""
template_engine.py — Moteur de templates
Supporte :
  {{ variable }}          — affichage de variable
  {{ objet.attribut }}    — accès à un attribut / clé de dict
  {% extends "base.html" %}     — héritage de template
  {% block nom %}...{% endblock %}
  {% for item in liste %}...{% endfor %}
  {% if condition %}...{% endif %}
  {% include "partial.html" %}
"""

from ast import pattern
from multiprocessing import context
import re
import os


class TemplateEngine:

    def __init__(self, templates_dir=None):
        if templates_dir is None:
            # Toujours relatif à l'emplacement de template_engine.py
            base = os.path.dirname(os.path.abspath(__file__))
            self.templates_dir = os.path.join(base, 'templates')
        else:
            self.templates_dir = templates_dir

    # ── API publique ───────────────────────────────────────────────────────────

    def render(self, template_name, context=None):
        """Point d'entrée : charge et rend un template."""
        if context is None:
            context = {}
        content = self._load(template_name)
        content = self._process_extends(content, context)
        content = self._process_includes(content, context)
        content = self._process_blocks(content, context)
        content = self._render_loops(content, context)
        content = self._render_conditionals(content, context)
        content = self._render_variables(content, context)

        import re
        remaining = re.findall(r'\{%.*?%\}', content)
        if remaining:
            print(f"  [TEMPLATE] Balises non traitées : {remaining}")

        return content

    # ── Chargement ─────────────────────────────────────────────────────────────

    def _load(self, name):
        path = os.path.join(self.templates_dir, name)
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    # ── Héritage ───────────────────────────────────────────────────────────────

    def _process_extends(self, content, context):
        """Gère {% extends "layouts/base.html" %}"""
        match = re.search(r'\{%\s*extends\s+"([^"]+)"\s*%\}', content)
        if not match:
            return content

        parent_name = match.group(1)
        parent = self._load(parent_name)

        # Extraire les blocs de l'enfant
        child_blocks = self._extract_blocks(content)

        # Injecter les blocs de l'enfant dans le parent
        def replace_block(m):
            block_name = m.group(1)
            return child_blocks.get(block_name, m.group(2))

        result = re.sub(
            r'\{%\s*block\s+(\w+)\s*%\}(.*?)\{%\s*endblock\s*%\}',
            replace_block,
            parent,
            flags=re.DOTALL
        )
        return result

    def _extract_blocks(self, content):
        """Retourne un dict {nom_bloc: contenu} pour un template enfant."""
        blocks = {}
        for m in re.finditer(
            r'\{%\s*block\s+(\w+)\s*%\}(.*?)\{%\s*endblock\s*%\}',
            content, re.DOTALL
        ):
            blocks[m.group(1)] = m.group(2).strip()
        return blocks

    def _process_blocks(self, content, context):
        """Supprime les balises block restantes (template sans extends)."""
        return re.sub(
            r'\{%\s*block\s+\w+\s*%\}(.*?)\{%\s*endblock\s*%\}',
            r'\1',
            content,
            flags=re.DOTALL
        )

    # ── Includes ───────────────────────────────────────────────────────────────

    def _process_includes(self, content, context):
        """Gère {% include "partials/nav.html" %}"""
        def replacer(m):
            return self.render(m.group(1), context)
        return re.sub(
            r'\{%\s*include\s+"([^"]+)"\s*%\}',
            replacer,
            content
        )

    # ── Boucles ────────────────────────────────────────────────────────────────

    def _render_loops(self, content, context):
        """Gère {% for item in liste %}...{% endfor %}"""
        pattern = r'\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}(.*?)\{%\s*endfor\s*%\}'

        def replacer(m):
            item_name = m.group(1)
            list_name = m.group(2)
            block     = m.group(3)
            items = self._resolve(list_name, context) or []
            result = ''
            for i, item in enumerate(items):
                loop_ctx = {
                    **context,
                    item_name: item,
                    'loop_index': i + 1,
                    'loop_first': i == 0,
                    'loop_last':  i == len(items) - 1,
                }
                rendered = self._render_loops(block, loop_ctx)
                rendered = self._render_conditionals(rendered, loop_ctx)
                rendered = self._render_variables(rendered, loop_ctx)
                result += rendered
            return result

        return re.sub(pattern, replacer, content, flags=re.DOTALL)

    # ── Conditionnels ──────────────────────────────────────────────────────────

    def _render_conditionals(self, content, context):
        """
        Gère les {% if %} imbriqués en traitant de l'intérieur vers l'extérieur.
        """
        pattern = (
            r'\{%\s*if\s+'
            r'([\w.]+)'
            r'(?:\s*(==|!=)\s*([\w.]+))?'
            r'\s*%\}'
            r'(.*?)'
            r'(?:\{%\s*else\s*%\}(.*?))?'
            r'\{%\s*endif\s*%\}'
        )

        def replacer(m):
            variable   = m.group(1)
            operator   = m.group(2)   # == ou != ou None
            comparator = m.group(3)   # valeur comparée ou None
            if_block   = m.group(4)
            else_block = m.group(5) or ''

            value = self._resolve(variable, context)

            if operator is None:
                # {% if variable %} — vérifie si truthy
                result = bool(value)
            elif operator == '==':
                result = str(value) == str(comparator)
            elif operator == '!=':
                result = str(value) != str(comparator)
            else:
                result = False

            return if_block if result else else_block
        
        # ── Appliquer le regex en boucle jusqu'à ce qu'il n'y ait plus rien ───
        # Chaque passage traite les {% if %} les plus internes
        previous = None
        while previous != content:
            previous = content
            content  = re.sub(pattern, replacer, content, flags=re.DOTALL)

        return content
        # return re.sub(pattern, replacer, content, flags=re.DOTALL)

    # ── Variables ──────────────────────────────────────────────────────────────

    def _render_variables(self, content, context):
        """Gère {{ variable }} et {{ objet.attribut }}"""
        def replacer(m):
            key = m.group(1).strip()
            val = self._resolve(key, context)
            return str(val) if val is not None else ''
        return re.sub(r'\{\{\s*([\w.]+)\s*\}\}', replacer, content)

    # ── Résolution de variables ────────────────────────────────────────────────

    def _resolve(self, key, context):
        """
        Résout une clé simple ou pointée (objet.attribut).
        Supporte dict, objet avec attributs, et index de liste.
        """
        parts = key.split('.')
        val = context.get(parts[0])
        for part in parts[1:]:
            if val is None:
                break
            if isinstance(val, dict):
                val = val.get(part)
            else:
                val = getattr(val, part, None)
        return val