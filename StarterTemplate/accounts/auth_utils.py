"""
Custom authentication utilities for MongoEngine users
Based on Django's auth system but adapted for MongoDB
"""
from django.contrib.auth import get_backends as _get_backends
from django.contrib.auth import load_backend
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.middleware.csrf import rotate_token
from django.utils.crypto import constant_time_compare

SESSION_KEY = "_auth_user_id"
BACKEND_SESSION_KEY = "_auth_user_backend"
HASH_SESSION_KEY = "_auth_user_hash"


def _get_user_session_key(request):
    """
    Get the user session key. For MongoEngine, this is the string ObjectId.
    """
    return request.session[SESSION_KEY]


def login(request, user, backend=None):
    """
    Persist a user id and a backend in the request. This way a user doesn't
    have to reauthenticate on every request. Note that data set during
    the anonymous session is retained when the user logs in.
    
    This version is adapted for MongoEngine users with ObjectId primary keys.
    """
    session_auth_hash = ""
    if user is None:
        user = request.user
    
    # Get session auth hash if the user supports it
    if hasattr(user, "get_session_auth_hash"):
        session_auth_hash = user.get_session_auth_hash()

    # Check if we need to flush the session (different user)
    if SESSION_KEY in request.session:
        try:
            current_user_id = _get_user_session_key(request)
            # Convert MongoEngine ObjectId to string for comparison
            user_id_str = str(user.id) if hasattr(user, 'id') else str(user.pk)
            
            if current_user_id != user_id_str or (
                session_auth_hash
                and not constant_time_compare(
                    request.session.get(HASH_SESSION_KEY, ""), session_auth_hash
                )
            ):
                # To avoid reusing another user's session, create a new, empty
                # session if the existing session corresponds to a different
                # authenticated user.
                request.session.flush()
        except (KeyError, AttributeError):
            # If there's any issue, just cycle the key
            request.session.cycle_key()
    else:
        request.session.cycle_key()

    # Get the backend
    try:
        backend = backend or user.backend
    except AttributeError:
        backends = _get_backends(return_tuples=True)
        if len(backends) == 1:
            _, backend = backends[0]
        else:
            raise ValueError(
                "You have multiple authentication backends configured and "
                "therefore must provide the `backend` argument or set the "
                "`backend` attribute on the user."
            )
    else:
        if not isinstance(backend, str):
            raise TypeError(
                "backend must be a dotted import path string (got %r)." % backend
            )

    # Store user ID in session
    # For MongoEngine, we need to store the ObjectId as a string
    try:
        # Try to get the string representation of the user ID
        if hasattr(user, 'id'):
            # MongoEngine Document with ObjectId
            request.session[SESSION_KEY] = str(user.id)
        elif hasattr(user, 'pk'):
            # Generic primary key
            request.session[SESSION_KEY] = str(user.pk)
        else:
            # Fallback
            request.session[SESSION_KEY] = str(user)
    except Exception as e:
        # If all else fails, try to convert to string
        print(f"Warning: Could not store user ID properly: {e}")
        request.session[SESSION_KEY] = str(user.id if hasattr(user, 'id') else user.pk)

    # Store backend and hash
    request.session[BACKEND_SESSION_KEY] = backend
    request.session[HASH_SESSION_KEY] = session_auth_hash
    
    # Update request.user
    if hasattr(request, "user"):
        request.user = user
    
    # Rotate CSRF token
    rotate_token(request)
    
    # Send signal
    user_logged_in.send(sender=user.__class__, request=request, user=user)


def logout(request):
    """
    Remove the authenticated user's ID from the request and flush their session
    data.
    """
    # Dispatch the signal before the user is logged out so the receivers have a
    # chance to find out *who* logged out.
    user = getattr(request, "user", None)
    if not getattr(user, "is_authenticated", True):
        user = None
    user_logged_out.send(sender=user.__class__, request=request, user=user)
    request.session.flush()
    if hasattr(request, "user"):
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()


def get_user(request):
    """
    Return the user model instance associated with the given request session.
    If no user is retrieved, return an instance of `AnonymousUser`.
    
    This version is adapted for MongoEngine users.
    """
    from django.contrib.auth.models import AnonymousUser
    from django.conf import settings

    user = None
    try:
        user_id = _get_user_session_key(request)
        backend_path = request.session[BACKEND_SESSION_KEY]
    except KeyError:
        pass
    else:
        if backend_path in settings.AUTHENTICATION_BACKENDS:
            backend = load_backend(backend_path)
            # For MongoEngine, user_id is already a string
            user = backend.get_user(user_id)
            
            # Verify the session
            if hasattr(user, "get_session_auth_hash"):
                session_hash = request.session.get(HASH_SESSION_KEY)
                if not session_hash:
                    session_hash_verified = False
                else:
                    session_auth_hash = user.get_session_auth_hash()
                    session_hash_verified = constant_time_compare(
                        session_hash, session_auth_hash
                    )
                if not session_hash_verified:
                    # If the current secret does not verify the session, try
                    # with the fallback secrets and stop when a matching one is
                    # found.
                    if session_hash and hasattr(user, 'get_session_auth_fallback_hash'):
                        if any(
                            constant_time_compare(session_hash, fallback_auth_hash)
                            for fallback_auth_hash in user.get_session_auth_fallback_hash()
                        ):
                            request.session.cycle_key()
                            request.session[HASH_SESSION_KEY] = session_auth_hash
                        else:
                            request.session.flush()
                            user = None
                    else:
                        request.session.flush()
                        user = None

    return user or AnonymousUser()
