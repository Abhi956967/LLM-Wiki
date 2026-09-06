import asyncio
import logging

import jwt as pyjwt
from jwt import PyJWKClient
from mcp.server.auth.provider import AccessToken, TokenVerifier

from config import settings

logger = logging.getLogger(__name__)

_jwks_client: PyJWKClient | None = None


def _get_jwks_client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        base = (settings.SUPABASE_URL or "https://dnouksmjstladcpjpyok.supabase.co").rstrip('/')
        jwks_url = f"{base}/auth/v1/.well-known/jwks.json"
        _jwks_client = PyJWKClient(jwks_url)
    return _jwks_client


class SupabaseTokenVerifier(TokenVerifier):

    async def verify_token(self, token: str) -> AccessToken | None:
        # 1. Try local JWKS verification
        try:
            signing_key = await asyncio.to_thread(
                _get_jwks_client().get_signing_key_from_jwt, token
            )
            payload = pyjwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "ES256", "RS384", "RS512", "ES384", "ES512"],
                leeway=60,
                options={
                    "verify_exp": True,
                    "verify_aud": False,
                    "verify_iss": False,
                },
            )
            sub = payload.get("sub", "") or payload.get("user_id", "")
            if sub:
                scopes = []
                scope_str = payload.get("scope", "")
                if isinstance(scope_str, str) and scope_str:
                    scopes = scope_str.split()
                logger.info("MCP auth verified via JWKS: %s", sub)
                return AccessToken(
                    token=token,
                    client_id=payload.get("client_id") or sub,
                    subject=sub,
                    scopes=scopes,
                    expires_at=payload.get("exp"),
                    claims=payload,
                )
        except pyjwt.ExpiredSignatureError:
            logger.info("MCP auth rejected: token expired")
            return None
        except Exception as e:
            logger.info("JWKS verification attempt: %s (%s). Trying Supabase Auth API fallback...", type(e).__name__, e)

        # 2. Universal Supabase Auth API Fallback (Checks OAuth userinfo and session user endpoints)
        try:
            import json
            import urllib.request

            def _check_supabase_api():
                anon_key = getattr(settings, "SUPABASE_ANON_KEY", "") or "sb_publishable_pIt3iceJ0m9fsStpt6j5ig_LO4wobG8"
                headers = {
                    "Authorization": f"Bearer {token}",
                    "apikey": anon_key,
                }
                base = (settings.SUPABASE_URL or "https://dnouksmjstladcpjpyok.supabase.co").rstrip('/')
                
                # Check OAuth 2.0 UserInfo endpoint
                for endpoint in ["/auth/v1/oauth/userinfo", "/auth/v1/user"]:
                    try:
                        req = urllib.request.Request(f"{base}{endpoint}", headers=headers)
                        with urllib.request.urlopen(req, timeout=6) as resp:
                            if resp.status == 200:
                                return json.loads(resp.read().decode())
                    except Exception:
                        pass
                return None

            user_data = await asyncio.to_thread(_check_supabase_api)
            if user_data:
                user_id = user_data.get("sub") or user_data.get("id") or ""
                if user_id:
                    logger.info("MCP auth verified via Supabase Auth API: %s", user_id)
                    return AccessToken(
                        token=token,
                        client_id=user_id,
                        subject=user_id,
                        scopes=[],
                        claims=user_data,
                    )
            else:
                logger.warning("Supabase Auth API fallback: token could not be verified")
        except Exception as e:
            logger.warning("Supabase Auth API fallback error: %s", e)

        return None
