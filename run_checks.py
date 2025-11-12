import ast
import os
import sys
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError

ROOT = os.path.abspath(os.path.dirname(__file__))

def compile_python_files():
    print('Compiling Python files...')
    errors = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # skip venv
        if '.venv' in dirpath:
            continue
        for fn in filenames:
            if fn.endswith('.py'):
                path = os.path.join(dirpath, fn)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        src = f.read()
                    ast.parse(src, filename=path)
                except Exception as e:
                    errors.append((path, repr(e)))
    if errors:
        print('Python compile errors found:')
        for p, e in errors:
            print(p, e)
    else:
        print('No Python syntax errors')
    return errors

def check_templates():
    print('\nChecking Jinja2 templates...')
    templates_dir = os.path.join(ROOT, 'templates')
    if not os.path.isdir(templates_dir):
        print('No templates directory found')
        return []
    env = Environment(loader=FileSystemLoader(templates_dir))
    errors = []
    for fn in os.listdir(templates_dir):
        if fn.endswith('.html'):
            try:
                env.get_template(fn)
            except TemplateSyntaxError as e:
                errors.append((fn, str(e)))
            except Exception as e:
                errors.append((fn, repr(e)))
    if errors:
        print('Template errors:')
        for fn, e in errors:
            print(fn, e)
    else:
        print('No template syntax errors')
    return errors

def find_duplicate_routes(app_module_path='app.py'):
    print('\nScanning for duplicate @app.route definitions...')
    path = os.path.join(ROOT, app_module_path)
    if not os.path.exists(path):
        print('No app.py found to scan')
        return []
    routes = {}
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read().splitlines()
    for i, line in enumerate(src):
        line_strip = line.strip()
        if line_strip.startswith('@app.route'):
            # extract between parentheses
            try:
                start = line_strip.index('(')
                end = line_strip.rindex(')')
                inner = line_strip[start+1:end]
                key = inner.strip()
            except Exception:
                key = line_strip
            routes.setdefault(key, []).append(i+1)
    dups = {k: v for k, v in routes.items() if len(v) > 1}
    if dups:
        print('Duplicate route decorators found:')
        for k, lines in dups.items():
            print(k, 'lines:', lines)
    else:
        print('No duplicate @app.route decorators found in app.py')
    return dups

def main():
    py_errors = compile_python_files()
    tmpl_errors = check_templates()
    dup = find_duplicate_routes()
    if py_errors or tmpl_errors or dup:
        print('\nIssues found. Please review the output above and fix errors.')
        sys.exit(2)
    print('\nAll checks passed')

if __name__ == '__main__':
    main()
