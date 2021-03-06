# -*- coding: utf-8 -*-

import uuid
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.translation import ugettext as _

from apps.authentication.forms import (LoginForm, RegisterForm, RecoveryForm, ChangePasswordForm)
from apps.authentication.models import RegisterToken
from apps.misc.forms import InlineSpanErrorList
from apps.userprofile.models import UserProfile
from apps.lan.models import LAN, Attendee


@sensitive_post_parameters()
def login(request):
    redirect_url = request.REQUEST.get('next', '')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.login(request):
            messages.success(request, _(u'You have successfully logged in.'))
            if redirect_url:
                return HttpResponseRedirect(redirect_url)
            return HttpResponseRedirect('/')
        else: form = LoginForm(request.POST, auto_id=True, error_class=InlineSpanErrorList)
    else:
        form = LoginForm()

    response_dict = { 'form' : form, 'next' : redirect_url}
    return render(request, 'auth/login.html', response_dict)


def logout(request):
    auth.logout(request)
    messages.success(request, _(u'You have successfully logged out.'))
    return HttpResponseRedirect('/')


@sensitive_post_parameters()
def register(request):
    if request.user.is_authenticated():
        messages.error(request, _(u'You cannot be logged in when registering.'))
        return HttpResponseRedirect('/')
    else:
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                cleaned = form.cleaned_data

                # Create user
                user = User(
                    username=cleaned['desired_username'],
                    first_name=cleaned['first_name'],
                    last_name=cleaned['last_name'],
                    email=cleaned['email'],
                )
                user.set_password(cleaned['password'])
                user.is_active = False
                user.save()

                # Create userprofile
                up = UserProfile(
                    user=user,
                    nick=cleaned['desired_username'],
                    date_of_birth=cleaned['date_of_birth'],
                    zip_code=cleaned['zip_code'],
                    address=cleaned['address'],
                    phone=cleaned['phone'],
                )
                up.save()

                # Create the registration token
                token = uuid.uuid4().hex
                rt = RegisterToken(user=user, token=token)
                rt.save()

                email_message = create_verify_message(request.META['HTTP_HOST'], token)

                send_mail(_(u'Verify your account'), email_message, settings.STUDLAN_FROM_MAIL, [user.email,], fail_silently=False)

                messages.success(request, _(u'Registration successful. Check your email for verification instructions.'))

                return HttpResponseRedirect('/')
            else:
                form = RegisterForm(request.POST, auto_id=True, error_class=InlineSpanErrorList)
        else:
            form = RegisterForm()

        return render(request, 'auth/register.html', {'form': form, })


@sensitive_post_parameters()
@staff_member_required
def direct_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data
            lan = LAN.objects.filter(end_date__gte=datetime.now())[0]

            if not lan:
                messages.error(request, u'No upcoming LAN was found.')
                return HttpResponseRedirect('/auth/direct_register')

            # Create user
            user = User(
               username=cleaned['desired_username'],
               first_name=cleaned['first_name'],
               last_name=cleaned['last_name'],
               email=cleaned['email'],
            )
            user.set_password(cleaned['password'])
            user.is_active = True
            user.save()

            # Create userprofile
            up = UserProfile(
                user=user,
                nick=cleaned['desired_username'],
                date_of_birth=cleaned['date_of_birth'],
                zip_code=cleaned['zip_code'],
                address=cleaned['address'],
                phone=cleaned['phone'],
            )
            up.save()

            attendee = Attendee(lan=lan, user=user)
            attendee.save()

            messages.success(request, _(u'Registration successful.'))

            return HttpResponseRedirect('/auth/direct_register')
        else:
            form = RegisterForm(request.POST, auto_id=True, error_class=InlineSpanErrorList)
    else:
        form = RegisterForm()
        lan = LAN.objects.filter(end_date__gte=datetime.now())[0]

    return render(request, 'auth/direct_register.html', {'form': form, 'lan': lan})


def verify(request, token):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    else:
        rt = get_object_or_404(RegisterToken, token=token)

        if rt.is_valid:
            user = getattr(rt, 'user')

            user.is_active = True
            user.save()
            rt.delete()

            messages.success(request, _(u"User ") + user.username + _(u" successfully activated. You can now log in."))

            return redirect('auth_login')
        else:
            messages.error(request, _(u"The token has expired. Please use the password recovery to get a new token."))
            return HttpResponseRedirect('/')


@sensitive_post_parameters()
def recover(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    else:
        if request.method == 'POST':
            form = RecoveryForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                users = User.objects.filter(email=email)

                if len(users) == 0:
                    messages.error(request, _(u"That email is not registered."))
                    return HttpResponseRedirect('/')

                user = users[0]
                user.save()

                # Create the registration token
                token = uuid.uuid4().hex
                rt = RegisterToken(user=user, token=token)
                rt.save()

                email_message = create_password_recovery_message(email, user.username, request.META['HTTP_HOST'], token)

                send_mail(_(u'Account recovery'), email_message, settings.STUDLAN_FROM_MAIL, [email,])

                messages.success(request, _('A recovery link has been sent to ') + email)

                return HttpResponseRedirect('/')
            else:
                form = RecoveryForm(request.POST, auto_id=True, error_class=InlineSpanErrorList)
        else:
            form = RecoveryForm()

        return render(request, 'auth/recover.html', {'form': form})


@sensitive_post_parameters()
def set_password(request, token=None):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    else:
        rt = get_object_or_404(RegisterToken, token=token)

        if rt.is_valid:
            if request.method == 'POST':
                form = ChangePasswordForm(request.POST, auto_id=True, error_class=InlineSpanErrorList)
                if form.is_valid():
                    user = getattr(rt, 'user')

                    user.is_active = True
                    user.set_password(form.cleaned_data['new_password'])
                    user.save()

                    rt.delete()

                    messages.success(request, _(u"User ") + unicode(user) + _(u" successfully had it's password changed. You can now log in."))

                    return HttpResponseRedirect('/')
            else:

                form = ChangePasswordForm()

                messages.success(request, _(u"Token accepted. Please insert your new password."))

            return render(request, 'auth/set_password.html', {'form': form, 'token': token})

        else:
            messages.error(request, _(u"The token has expired. Please use the password recovery to get a new token."))
            return HttpResponseRedirect('/')


def create_verify_message(host, token):
    message = _(u"You have registered an account at ") + host
    message += _(u"\nTo use the account you need to verify it. You can do this by visiting the link below.\n\n")

    message += "http://%s/auth/verify/%s/" %  (host, token)

    message += _(u"""
\nNote that tokens have a valid lifetime of 24 hours. If you do not use this
link within 24 hours, it will be invalid, and you will need to use the password
recovery option again to get your account verified.""")

    return message


def create_password_recovery_message(email, username, host, token):

    message = _(u"You have requested a password recovery for the account bound to ") + email

    message += "\n\n" + _(u"Username") + ": " + username + "\n\n"

    message += _(u"If you did not ask for this password recovery, please ignore this email.")

    message += _(u"\n\nOtherwise, click the link below to reset your password:\n")
    message += "http://%s/auth/set_password/%s/" % (host, token)

    message += _(u"""
\nNote that tokens have a valid lifetime of 24 hours. If you do not use this
link within 24 hours, it will be invalid, and you will need to use the password
recovery option again to get your account verified.""")

    return message
