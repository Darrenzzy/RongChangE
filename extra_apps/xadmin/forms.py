import base64
import warnings
import logging

from django import forms

from django.contrib.auth import authenticate, user_logged_out, load_backend, user_logged_in
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LogoutView, LoginView
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.middleware.csrf import rotate_token
from django.utils.crypto import constant_time_compare
from django.utils.decorators import method_decorator
from django.utils.deprecation import RemovedInDjango50Warning
from django.conf import settings

from django.utils.translation import gettext_lazy as ugettext_lazy, gettext as _

from django.contrib.auth import get_user_model

from xadmin.patch_tools import never_cache
from xadmin.rsa_for_js_encrypt import RsaClient

from xadmin.util import create_event_log

ERROR_MESSAGE = ugettext_lazy("Please enter the correct username and password "
                              "for a staff account. Note that both fields are case-sensitive.")
log = logging.getLogger(__name__)


def get_ip_address(request):
    try:
        ip_addr = request.META['HTTP_X_FORWARDED_FOR'] if request.META['HTTP_X_FORWARDED_FOR'] else \
            request.META['REMOTE_ADDR']
    except Exception as e:
        ip_addr = request.META['REMOTE_ADDR']
    return ip_addr


class AdminAuthenticationForm(AuthenticationForm):
    """
    A custom authentication form used in the admin app.

    """
    this_is_the_login_form = forms.BooleanField(
        widget=forms.HiddenInput, initial=1,
        error_messages={'required': ugettext_lazy("Please log in again, because your session has expired.")})

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        message = ERROR_MESSAGE

        if not username or not password:
            raise forms.ValidationError(message)

        try:
            test = RsaClient()
            username = test.decrypt(username)
            password = test.decrypt(password)
        except Exception as _:
            raise forms.ValidationError("网络环境异常，请重试或联系管理员~")

        ip_addr = get_ip_address(self.request)

        self.user_cache = authenticate(username=username, password=password)
        if self.user_cache is None:
            if u'@' in username:
                User = get_user_model()
                # Mistakenly entered e-mail address instead of username? Look it up.
                try:
                    self.user_cache = User.objects.get(email=username)
                except (User.DoesNotExist, User.MultipleObjectsReturned):
                    # Nothing to do here, moving along.
                    pass
                else:
                    if self.user_cache.check_password(password):
                        message = _("Your e-mail address is not your username."
                                    " Try '%s' instead.") % self.user_cache.username
            raise forms.ValidationError(message)
        elif not self.user_cache.is_active or not self.user_cache.is_staff:
            raise forms.ValidationError(message)

        if not self.user_cache:
            raise forms.ValidationError(message)

        if self.user_cache:
            create_event_log(
                user=self.user_cache,
                flag="login",
                ip_addr=ip_addr,
                message=f"[ {self.user_cache.username} ] 登入成功. 登入设备 {self.request.META.get('HTTP_USER_AGENT', '')}.",
                app_label=None,
                model_name=None,
                obj=None,
                object_repr=None,
            )

        return self.cleaned_data


def copy_logout(request):
    """
    Remove the authenticated user's ID from the request and flush their session
    data.
    """

    ip_addr = get_ip_address(request)

    # Dispatch the signal before the user is logged out so the receivers have a
    # chance to find out *who* logged out.
    user = getattr(request, 'user', None)
    if not getattr(user, 'is_authenticated', True):
        user = None

    user_logged_out.send(sender=user.__class__, request=request, user=user)
    request.session.flush()

    if hasattr(request, 'user'):
        if user:
            '''
            # redis cache 限制同一账号只能在单设备下登入
            # 第一步：读取当前用户上次的session name
            session_lock_name = f"session:lock:{user.pk}"
            caches[settings.SESSION_CACHE_ALIAS].delete(session_lock_name)
            '''
            create_event_log(
                user=user,
                flag="logout",
                ip_addr=ip_addr,
                message=f"[ {user.username} ] 登出成功. 登出设备 {request.META.get('HTTP_USER_AGENT', '')}.",
                app_label=None,
                model_name=None,
                obj=None,
                object_repr=None,
            )

        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()


class CopyLogoutView(LogoutView):

    # RemovedInDjango50Warning: when the deprecation ends, move
    # @method_decorator(csrf_protect) from post() to dispatch().
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() == "get":
            warnings.warn(
                "Log out via GET requests is deprecated and will be removed in Django "
                "5.0. Use POST requests for logging out.",
                RemovedInDjango50Warning,
            )
        copy_logout(request)
        return super().dispatch(request, *args, **kwargs)


SESSION_KEY = '_auth_user_id'
BACKEND_SESSION_KEY = '_auth_user_backend'
HASH_SESSION_KEY = '_auth_user_hash'
REDIRECT_FIELD_NAME = 'next'


def _get_backends(return_tuples=False):
    backends = []
    for backend_path in settings.AUTHENTICATION_BACKENDS:
        backend = load_backend(backend_path)
        backends.append((backend, backend_path) if return_tuples else backend)
    if not backends:
        raise ImproperlyConfigured(
            'No authentication backends have been defined. Does '
            'AUTHENTICATION_BACKENDS contain anything?'
        )
    return backends


def _get_user_session_key(request):
    # This value in the session is always serialized to a string, so we need
    # to convert it back to Python whenever we access it.
    return get_user_model()._meta.pk.to_python(request.session[SESSION_KEY])


def update_auth_login(request, user, backend=None):
    """
    Persist a user id and a backend in the request. This way a user doesn't
    have to reauthenticate on every request. Note that data set during
    the anonymous session is retained when the user logs in.
    """
    session_auth_hash = ''
    if user is None:
        user = request.user
    if hasattr(user, 'get_session_auth_hash'):
        session_auth_hash = user.get_session_auth_hash()

    if SESSION_KEY in request.session:
        if _get_user_session_key(request) != user.pk or (
                session_auth_hash and
                not constant_time_compare(request.session.get(HASH_SESSION_KEY, ''), session_auth_hash)):
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
    else:
        request.session.cycle_key()

    try:
        backend = backend or user.backend
    except AttributeError:
        backends = _get_backends(return_tuples=True)
        if len(backends) == 1:
            _, backend = backends[0]
        else:
            raise ValueError(
                'You have multiple authentication backends configured and '
                'therefore must provide the `backend` argument or set the '
                '`backend` attribute on the user.'
            )
    else:
        if not isinstance(backend, str):
            raise TypeError('backend must be a dotted import path string (got %r).' % backend)
    '''
    # redis cache 限制同一账号只能在单设备下登入
    # 第二步：
    #   读取当前用户上次的session name，删除上次的记录，强迫登出
    
    session_lock_name = f"session:lock:{user.pk}"
    last_session_name = caches[settings.SESSION_CACHE_ALIAS].get(session_lock_name)
    if last_session_name:
        caches[settings.SESSION_CACHE_ALIAS].delete(last_session_name)
        if user:
            create_event_log(
                user=user,
                flag="logout",
                ip_addr=get_ip_address(request),
                message=f"[ {user.username} ] 被迫下线，已在其它设备登入成功. 登入设备 {request.META.get('HTTP_USER_AGENT', '')}.",
                app_label=None,
                model_name=None,
                obj=None,
                object_repr=None,
            )
    '''

    # abbottdefault:1:django.contrib.sessions.cache658s5b6nd1r5ybh92qwnv8hkv1glco9h
    #                 Fdjango.contrib.sessions.backends.cache658s5b6nd1r5ybh92qwnv8hkv1glco9h

    session_key = user._meta.pk.value_to_string(user)
    request.session[SESSION_KEY] = session_key
    request.session[BACKEND_SESSION_KEY] = backend
    request.session[HASH_SESSION_KEY] = session_auth_hash

    '''
    # redis cache 限制同一账号只能在单设备下登入
    # 第三步：
    #   缓存当前 session name
    session_name = f"django.contrib.sessions.cache{request.session._SessionBase__session_key}"
    caches[settings.SESSION_CACHE_ALIAS].set(session_lock_name, session_name, timeout=settings.SESSION_COOKIE_AGE)
    '''

    if hasattr(request, 'user'):
        request.user = user
    rotate_token(request)
    user_logged_in.send(sender=user.__class__, request=request, user=user)


class CopyloginView(LoginView):
    def form_valid(self, form):
        """Security check complete. Log the user in."""
        update_auth_login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())
