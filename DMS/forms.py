from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from django.utils.http import int_to_base36

from .models import Folder, Document, CustomUser


class DocumentForm(forms.ModelForm):
    EXTENSIONS = (('jpg', 'jpg'),
                  ('pdf', 'pdf'),
                  ('png', 'png'),
                  ('docx', 'docx'),
                  ('pptx', 'pptx'),
                  ('xlsx', 'xlsx'),
                  )

    type = forms.ChoiceField(choices=EXTENSIONS)
    class Meta:
        model = Document
        fields = ['name', 'owner', 'type', 'keywords', 'description', 'path']


class FolderForm(forms.ModelForm):
    CHOICES = [[x.name, x.name] for x in Folder.objects.all()]

    CHOICES.insert(0, ['root', "Root Folder"])
    root = forms.ChoiceField(choices=CHOICES)

    class Meta:
        model = Folder
        fields = ['name', 'root']


class UserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'password']


class PassworResetForm(forms.Form):
    error_messages = {
        'unknown': ("That email address doesn't have an associated "
                    "user account. Are you sure you've registered?"),
        'unusable': ("The user account associated with this email "
                     "address cannot reset the password."),
    }

    def clean_email(self):
        """
        Validates that an active user exists with the given email address.
        """
        UserModel = get_user_model()
        email = self.cleaned_data["email"]
        self.users_cache = UserModel._default_manager.filter(email__iexact=email)
        if not len(self.users_cache):
            raise forms.ValidationError(self.error_messages['unknown'])
        if not any(user.is_active for user in self.users_cache):
            # none of the filtered users are active
            raise forms.ValidationError(self.error_messages['unknown'])
        return email

    def save(self, domain_override=None,
             subject_template_name='password_reset_subject.txt',
             email_template_name='password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        from django.core.mail import send_mail
        for user in self.users_cache:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': int_to_base36(user.pk),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
            subject = loader.render_to_string(subject_template_name, c)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            email = loader.render_to_string(email_template_name, c)
            send_mail(subject, email, from_email, [user.email])
