from app import create_app
from utils.db import db
from flask_mail import Mail
from urllib.parse import urlencode

app = create_app()
mail = Mail(app)

def setup_jinja2(app):
    env = app.jinja_env
    def _safe_getattr(obj, attr):
        if not hasattr(obj, attr):
            return None
        return getattr(obj, attr)
    env.filters['safe_getattr'] = _safe_getattr
    
    def urlencode_filter(s):
        if isinstance(s, dict):
            return urlencode(s)
        elif hasattr(s, 'to_dict'):
            return urlencode(s.to_dict(flat=False))
        return s
    env.filters['urlencode_filter'] = urlencode_filter
    
    def money_format(amount,locale=False,symbol=False,grouping=False):
        from utils.methods.engine import newMoney
        money = newMoney(int(amount * 100 )).format(locale,symbol,grouping)
        return money
    env.filters['money_format'] = money_format

setup_jinja2(app)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5000, use_reloader=False)
