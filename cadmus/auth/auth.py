#!/usr/bin/env python
# encoding: utf-8
"""
requires_auth

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import re
from functools import wraps

import requests
import six
from flask import g
from flask import request

from jose import jwt
from jose.exceptions import ExpiredSignatureError

logger = logging.getLogger(__name__)

ALGORITHMS = ["RS256"]


class Auth(object):

    def __init__(self,
                 issuer,
                 api_audience,
                 jwks_url,
                 algorithms=ALGORITHMS):
        self._issuer = issuer
        self._api_audience = api_audience
        self._jwks_url = jwks_url
        self._signing_jwks = self._get_signing_jwks(jwks_url)
        self._algorithms = algorithms
        self._user_loader = None

    def _load_auth0_jwks(self, url):
        try:
            r = requests.get(url)
            if r.ok:
                return r.json()['keys']
        except Exception as e:
            logger.warn('Load AUTH0 jwks: %s', e)
            pass

        return {}

    load_jwks = _load_auth0_jwks

    # TODO(thuync): should cache in a period of time
    def _get_signing_jwks(self, url=None):
        keys = self.load_jwks(url)
        return {
            key['kid']: key for key in keys if key['use'] == 'sig'
        }

    def _get_auth_token(self, header_name='Authorization'):
        auth_header = request.headers.get(header_name)
        if not auth_header:
            raise jwt.JWTError('Authorization header missing')

        parts = auth_header.split()
        if len(parts) != 2:
            raise jwt.JWTError('Authorization header must be Bearer header')

        token_type, token_value = parts
        if token_type.lower() != 'bearer':
            raise jwt.JWTError('Authorization header must be Bearer header')

        return token_value

    def _decode_jwt_token(self, token, key):
        return jwt.decode(
            token,
            key,
            algorithms=self._algorithms,
            audience=self._api_audience,
            issuer=self._issuer
            # issuer='https://%s/' % AUTH0_DOMAIN
        )

    def _get_token_payload(self):
        token = self._get_auth_token()
        try:
            unverified_header = jwt.get_unverified_header(token)
            key = self._signing_jwks.get(unverified_header.get('kid'))
            return self._decode_jwt_token(token, key)
        except (ExpiredSignatureError, ):
            raise ExpiredSignatureError('Access token has expired')
        except Exception:
            raise jwt.JWTError('Unable to find appropriate key')

    def user_loader(self, f):
        self._user_loader = f
        return f

    def _load_user(self, user_id):
        user = None
        if self._user_loader:
            user = self._user_loader(user_id)

        if not user:
            raise NotFoundError('User not exists: %s' % user_id)

        return user

    def require_auth(self, f):

        @wraps(f)
        def decorated(*args, **kwargs):
            payload = self._get_token_payload()
            # user_id = payload.get('user_id') or payload.get('sub')
            # g.user = self._load_user(user_id)

            return f(*args, **kwargs)

        return decorated

    def _verify_scope(self, payload, required_scope_set):
        if not payload or not payload.get('scope'):
            raise ScopeError('No scope is provided')

        scope_list = re.split(r'\s+', payload['scope'].strip())
        scope_set = set(scope_list)
        missing_scope_set = required_scope_set - scope_set
        if missing_scope_set:
            raise ScopeError('Scope is missed: %s', missing_scope_set)

    def require_scope(self, required_scope):
        """
        Args:
            required_scope (str|list): Required scope
        """
        if isinstance(required_scope, six.string_types):
            required_scope = required_scope.strip().split()
        required_scope_set = set(required_scope)

        def _require_scope(f):

            def decorated(*args, **kwargs):
                payload = self._get_token_payload()
                user_id = payload.get('user_id') or payload.get('sub')
                g.user = self._load_user(user_id)

                self._verify_scope(payload, required_scope_set)

                return f(*args, **kwargs)

            return decorated

        return _require_scope


class ScopeError(jwt.JWTError):
    pass


class NotFoundError(Exception):
    pass
