"""
FILE: backend/app.py
PURPOSE: Flask application factory + security middleware.
Run from the project root:   python -m backend.app
"""
from flask import Flask, jsonify, request

from .config import Config, FRONTEND_DIR
from .models import database as db
from .routes.api import api
from .routes.pages import pages
from .utils.rate_limiter import RateLimiter
from .utils.security import apply_security_headers


def create_app(overrides=None) -> Flask:
    app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
    app.config.update(DATABASE_PATH=Config.DATABASE_PATH, MAX_CONTENT_LENGTH=Config.MAX_CONTENT_LENGTH,
                      RATE_LIMIT=Config.RATE_LIMIT_PER_MINUTE, WRITE_RATE_LIMIT=Config.WRITE_RATE_LIMIT_PER_MINUTE)
    app.config.update(overrides or {})
    limiter = RateLimiter()
    app.extensions["limiter"] = limiter

    db.init_db(app.config["DATABASE_PATH"])
    db.purge_older_than(Config.RETENTION_DAYS, app.config["DATABASE_PATH"])  # retention limitation

    app.register_blueprint(api)
    app.register_blueprint(pages)

    @app.before_request
    def rate_limit():
        # Keyed on IP only in memory; never written to disk or the database.
        ip = request.remote_addr or "unknown"
        writes = request.method in ("POST", "PUT", "DELETE", "PATCH")
        ok, retry = limiter.check(f"all:{ip}", app.config["RATE_LIMIT"])
        if ok and writes:
            ok, retry = limiter.check(f"write:{ip}", app.config["WRITE_RATE_LIMIT"])
        if not ok:
            resp = jsonify({"error": "rate_limited", "retry_after_seconds": retry})
            resp.status_code = 429
            resp.headers["Retry-After"] = str(retry)
            return resp

    @app.after_request
    def headers(resp):
        if "Content-Security-Policy" not in resp.headers:
            apply_security_headers(resp)
        if request.path.startswith("/api/"):
            resp.headers["Cache-Control"] = "no-store"
        return resp

    def _err(code, name):
        def handler(_e):
            return jsonify({"error": name}), code
        return handler

    for code, name in [(404, "not_found"), (405, "method_not_allowed"), (413, "payload_too_large"),
                       (500, "internal_error")]:
        app.register_error_handler(code, _err(code, name))
    return app


app = create_app()

if __name__ == "__main__":
    print(f"\n  Privacy Risk Assessment running at http://{Config.HOST}:{Config.PORT}\n")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
