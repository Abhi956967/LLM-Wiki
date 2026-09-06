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
        jwks_url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
        _jwks_client = PyJWKClient(jwks_url)
    return _jwks_client


_EXPECTED_ISSUER = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1"


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
            import requests

            def _check_supabase_api():
                anon_key = getattr(settings, "SUPABASE_ANON_KEY", "") or "sb_publishable_pIt3iceJ0m9fsStpt6j5ig_LO4wobG8"
                headers = {
                    "Authorization": f"Bearer {token}",
                    "apikey": anon_key,
                }
                base = settings.SUPABASE_URL.rstrip('/')
                
                # Check OAuth 2.0 UserInfo endpoint (for tokens issued by Supabase OAuth Server)
                try:
                    r1 = requests.get(f"{base}/auth/v1/oauth/userinfo", headers=headers, timeout=6)
                    if r1.status_code == 200:
                        return r1
                except Exception:
                    pass

                # Check standard Supabase /user endpoint
                try:
                    r2 = requests.get(f"{base}/auth/v1/user", headers=headers, timeout=6)
                    return r2
                except Exception as ex:
                    return None

            res = await asyncio.to_thread(_check_supabase_api)
            if res and res.status_code == 200:
                user_data = res.json()
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
            elif res:
                logger.warning("Supabase Auth API rejected token: status %d %s", res.status_code, res.text[:200])
        except Exception as e:
            logger.warning("Supabase Auth API fallback failed: %s", e)

        return None
