import reversion
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100, verbose_name=_("First name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last name"))
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    date_of_birth = models.DateField(blank=True, null=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        # The user is identified by their email address
        return u"%s %s" % (self.first_name, self.last_name)

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __unicode__(self):  # __unicode__ on Python 2
        return u"%s" % self.first_name

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")


        # def has_perm(self, perm, obj=None):
        #     "Does the user have a specific permission?"
        #     # Simplest possible answer: Yes, always
        #     return True
        #
        # def has_module_perms(self, app_label):
        #     "Does the user have permissions to view the app `app_label`?"
        #     # Simplest possible answer: Yes, always
        #     return True

        # @property
        # def is_staff(self):
        #     "Is the user a member of staff?"
        #     # Simplest possible answer: All admins are staff
        #     return self.is_admin


@reversion.register
class Document(models.Model):
    name = models.CharField(max_length=70)
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name="created_by")
    type = models.CharField(max_length=50)
    keywords = models.TextField()
    description = models.TextField(default='some description')
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name="working_user")
    creation_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    path = models.FileField(upload_to='media')
    folder = models.ForeignKey('Folder', on_delete=models.CASCADE, null=True)

    # version = models.ForeignKey('Version', on_delete=models.SET_NULL,null=True, related_name="version_id")

    def get_absolute_url(self):
        return reverse('DMS:detail', kwargs={'pk': self.pk})

        # def files(self):
        #     return u'<a href="%s%s" target="_blank">' % (settings.MEDIA_URL, self.files)

    def __str__(self):
        return self.name + '-' + self.type

    # class Meta:
    #     permissions = (
    #         ('view_task', 'View task'),
    #     )

class Version(models.Model):
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True)
    time = models.DateTimeField()
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name="active_user")


class Folder(models.Model):
    name = models.CharField(max_length=100)

    root = models.CharField(max_length=50)

    def get_name(self):
        return "{}".format(self.name)
        # child = models.CharField(max_lenght = 20)

        # def get_absolute_url(self):
        # return reverse('DMS:folder-details', kwargs={'pk': self.pk})

    def get_absolute_url(self):
        return reverse('DMS:folder-details', kwargs={'pk': self.pk})
