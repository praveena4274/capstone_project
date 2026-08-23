"""
Resource server ("/chat" API).
Validates Auth0-issued RS256 JWTs against the tenant's JWKS, checks
aud/iss/exp, and enforces scope-based access:
  - GET /chat   requires "read:ai-data"
  - GET /admin  requires "write:admin"  -> user tokens get 403 here
"""
import os
from functools import wraps

import jwt
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"]
API_AUDIENCE = os.environ["AUTH0_AUDIENCE"]
ISSUER = f"https://{AUTH0_DOMAIN}/"
JWKS_URL = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"

jwks_client = jwt.PyJWKClient(JWKS_URL)


class AuthError(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code


def get_token_from_header():
    auth = request.headers.get("Authorization", None)
    if not auth or not auth.startswith("Bearer "):
        raise AuthError("Missing or malformed Authorization header", 401)
    return auth.split(" ", 1)[1]


def verify_token():
    token = get_token_from_header()
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=API_AUDIENCE,
            issuer=ISSUER,
        )
    except jwt.ExpiredSignatureError:
        raise AuthError("Token expired", 401)
    except jwt.InvalidTokenError as e:
        raise AuthError(f"Invalid token: {e}", 401)
    return payload


def requires_scope(required_scope):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            payload = verify_token()
            token_scopes = payload.get("scope", "").split()
            if required_scope not in token_scopes:
                raise AuthError(
                    f"Insufficient scope: requires '{required_scope}'", 403
                )
            request.jwt_payload = payload
            return f(*args, **kwargs)
        return wrapper
    return decorator


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    return jsonify({"error": ex.message}), ex.status_code


@app.route("/chat", methods=["GET"])
@requires_scope("read:ai-data")
def chat():
    return jsonify({
        "message": "AI chat response OK",
        "caller_sub": request.jwt_payload.get("sub"),
    }), 200


@app.route("/admin", methods=["GET"])
@requires_scope("write:admin")
def admin():
    return jsonify({"message": "Admin action executed"}), 200


if __name__ == "__main__":
    app.run(port=int(os.environ.get("API_PORT", 5000)), debug=True)