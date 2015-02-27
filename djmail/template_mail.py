# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import logging
from collections import defaultdict
from contextlib import contextmanager
from django.conf import settings
from django.core import mail
from django.utils import translation
from django.utils.six import string_types
from django.template import loader, TemplateDoesNotExist
from functools import partial

from . import models
from . import exceptions as exc

log = logging.getLogger(__name__)


def _get_setting(name, default):
    return getattr(settings, name, default)


@contextmanager
def language(lang):
    old_language = translation.get_language()
    try:
        translation.activate(lang)
        yield
    finally:
        translation.activate(old_language)


class TemplateMail(object):

    name = None

    def __init__(self, name=None):
        self._email = None
        if name is not None:
            self.name = name
        self._body_template_name = _get_setting('DJMAIL_BODY_TEMPLATE_PROTOTYPE', 'emails/{name}-body.{ext}')
        self._subject_template_name = _get_setting('DJMAIL_SUBJECT_TEMPLATE_PROTOTYPE', 'emails/{name}-subject.txt')

    def _render_message_body_as_html(self, context):
        template_name = self._body_template_name.format(ext='html', name=self.name)
        try:
            return loader.render_to_string(template_name, context)
        except TemplateDoesNotExist as e:
            log.warning("Template '{0}' does not exists.".format(e))

    def _render_message_body_as_txt(self, context):
        template_name = self._body_template_name.format(ext='txt', name=self.name)
        try:
            return loader.render_to_string(template_name, context)
        except TemplateDoesNotExist as e:
            log.warning("Template '{0}' does not exists.".format(e))

    def _render_message_subject(self, context):
        template_name = self._subject_template_name.format(name=self.name)
        try:
            subject = loader.render_to_string(template_name, context)
        except TemplateDoesNotExist as e:
            raise exc.TemplateNotFound("Template '{0}' does not exists.".format(e))
        return ' '.join(subject.strip().split())

    def make_email_object(self, to, context, **kwargs):
        if not isinstance(to, (list, tuple)):
            to = [to]

        lang = context.get('lang', settings.LANGUAGE_CODE)
        with language(lang):
            body_html = self._render_message_body_as_html(context)
            body_txt = self._render_message_body_as_txt(context)

        if not body_txt and not body_html:
            raise exc.TemplateNotFound("Body of email message shouldn't be empty")

        if body_txt and body_html:
            email = mail.EmailMultiAlternatives(**kwargs)
            email.body = body_txt
            email.attach_alternative(body_html, 'text/html')
        elif not body_txt and body_html:
            email = mail.EmailMessage(**kwargs)
            email.content_subtype = 'html'
            email.body = body_html
        else:
            email = mail.EmailMessage(**kwargs)
            email.body = body_txt

        email.to = to
        email.subject = self._render_message_subject(context)

        return email

    def send(self, to, context, **kwargs):
        email = self.make_email_object(to, context, **kwargs)
        return email.send()


class InlineCSSTemplateMail(TemplateMail):

    def _render_message_body_as_html(self, context):
        html = super(InlineCSSTemplateMail, self)._render_message_body_as_html(context)
        if html:
            # Transform CSS into line style attributes
            import premailer
            return premailer.transform(html)
        return html


class MagicMailBuilder(object):

    def __init__(self, email_attr='email', lang_attr='lang', template_mail_cls=TemplateMail):
        self._email_attr = email_attr
        self._lang_attr = lang_attr
        self._template_mail_cls = template_mail_cls

    def __getattr__(self, name):

        def _dynamic_email_generator(to, context, priority=models.PRIORITY_STANDARD):
            lang = None

            if not isinstance(to, string_types):
                if not hasattr(to, self._email_attr):
                    raise AttributeError("'to' parameter does not have '{0}' attribute".format(self._email_attr))

                lang = getattr(to, self._lang_attr, None)
                to = getattr(to, self._email_attr)

            if lang is not None:
                context['lang'] = lang

            template_email = self._template_mail_cls(name=name)
            email_instance = template_email.make_email_object(to, context)
            email_instance.priority = priority
            return email_instance

        return _dynamic_email_generator


class MagicMailBuilderV2(object):

    def __init__(self, email_attr='email', lang_attr='lang', name_prototype='{name}',
                 template_mail_cls=InlineCSSTemplateMail):
        self._email_attr = email_attr
        self._lang_attr = lang_attr
        self._name_prototype = name_prototype
        self._template_mail_cls = template_mail_cls

    def _get_infos(self, recipient):
        if isinstance(recipient, string_types):
            return recipient, None
        return getattr(recipient, self._email_attr, None), getattr(recipient, self._lang_attr, None)

    def _email_generator(self, to, context, lang=None, name=None, priority=models.PRIORITY_STANDARD):
        if not isinstance(to, (list, tuple)):
            to = [to]
        lang = context.get('lang', lang)

        # regroup recipients by language
        to_by_lang = defaultdict(list)
        for counter, recipient in enumerate(to):
            address, lang_ = self._get_infos(recipient)
            if not address:
                raise AttributeError("Unable to retrieve e-mail address from 'to[{0}]={1}'".format(counter, recipient))
            to_by_lang[lang_ or lang].append(address)

        # create an email instance by language
        email_by_lang = {}
        for lang, to in to_by_lang.items():
            context.pop('lang', None)
            if lang is not None:
                context['lang'] = lang
            template_email = self._template_mail_cls(name=name)
            email = template_email.make_email_object(to, context)
            email.priority = priority
            email_by_lang[lang] = email
        return email_by_lang

    def __getattr__(self, name):
        return partial(self._email_generator, name=self._name_prototype.format(name=name))


def make_email(name, to, context=None, template_mail_cls=TemplateMail, **kwargs):
    """Helper for build email objects."""

    if context is None:
        context = {'to': to}
    instance = template_mail_cls(name)
    return instance.make_email_object(to, context, **kwargs)
