"""
Regular Web Application (Auth0 "ai-chat-webapp").
Implements Authorization Code + PKCE via Authlib and shows the decoded
access/ID token so you can screenshot the claims (aud, iss, exp, scope).
"""
import os
import jwt as pyjwt
from flask import Flask, redirect, url_for, session, jsonify, render_template_string
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]

oauth = OAuth(app)
auth0 = oauth.register(
    "auth0",
    client_id=os.environ["AUTH0_CLIENT_ID"],
    client_secret=os.environ["AUTH0_CLIENT_SECRET"],
    client_kwargs={
        "scope": "openid profile email read:ai-data",
        "code_challenge_method": "S256",  # <-- this is what turns the flow into PKCE
    },
    server_metadata_url=f'https://{os.environ["AUTH0_DOMAIN"]}/.well-known/openid-configuration',
)

HOME_HTML = """
<h2>Auth0 PKCE Demo</h2>
{% if token %}
  <p>Logged in.</p>
  <h3>Access token (decoded, unverified locally — verify at jwt.io)</h3>
  <pre>{{ access_claims }}</pre>
  <h3>ID token claims</h3>
  <pre>{{ id_claims }}</pre>
  <p>Raw access token (paste this at jwt.io):</p>
  <textarea rows="6" cols="100">{{ raw_access_token }}</textarea>
  <p><a href="/logout">Logout</a> | <a href="/call-admin">Try admin-scoped endpoint (expect 403)</a></p>
{% else %}
  <a href="/login">Log in with Auth0</a>
{% endif %}
"""


@app.route("/")
def home():
    token = session.get("user_token")
    if not token:
        return render_template_string(HOME_HTML, token=None)
    access_claims = pyjwt.decode(token["access_token"], options={"verify_signature": False})
    id_claims = pyjwt.decode(token["id_token"], options={"verify_signature": False})
    return render_template_string(
        HOME_HTML,
        token=token,
        access_claims=access_claims,
        id_claims=id_claims,
        raw_access_token=token["access_token"],
    )


@app.route("/login")
def login():
    return auth0.authorize_redirect(
        redirect_uri=os.environ["AUTH0_CALLBACK_URL"],
        audience=os.environ["AUTH0_AUDIENCE"],
    )


@app.route("/callback")
def callback():
    token = auth0.authorize_access_token()
    session["user_token"] = token
    return redirect(url_for("home"))


@app.route("/call-admin")
def call_admin():
    """Calls the resource server's admin-only endpoint with the user's
    (non-admin) access token to demonstrate the 403 rejection."""
    import requests
    token = session.get("user_token")
    if not token:
        return redirect(url_for("home"))
    r = requests.get(
        "http://localhost:5000/admin",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    return jsonify({"status_code": r.status_code, "body": r.json()})


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        f'https://{os.environ["AUTH0_DOMAIN"]}/v2/logout?'
        f'client_id={os.environ["AUTH0_CLIENT_ID"]}&returnTo=http://localhost:3000'
    )


if __name__ == "__main__":
    app.run(port=3000, debug=True)