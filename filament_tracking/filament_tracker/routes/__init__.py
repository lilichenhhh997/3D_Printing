from .pages import bp as pages_bp
from .spools import bp as spools_bp
from .usages import bp as usages_bp
from .export import bp as export_bp


def register_routes(app):
    app.register_blueprint(pages_bp)
    app.register_blueprint(spools_bp)
    app.register_blueprint(usages_bp)
    app.register_blueprint(export_bp)
