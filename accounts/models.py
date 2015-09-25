from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _


class ParanoidUserManager(BaseUserManager):
    def create_user(self, email, password=None, first_name='', last_name=''):
        """
        Creates and saves a User with the given email, first_name, last_name
        and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            first_name = first_name,
            last_name  = last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email, first_name, last_name, password):
        """
        Creates and saves a superuser with the given email, first_name
        last_name and password.
        """
        user = self.create_user(
            email,
            password=password,
            first_name = first_name,
            last_name = lasst_name
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class ParanoidUser(AbstractBaseUser):
    """
    Users within the Paranoid system are represented by this model.
    Only email is required. Other fields are optional.
    """
    email = models.EmailField(
        _('email address'),
        max_length=255,
        primary_key=True,

    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = ParanoidUserManager()

    USERNAME_FIELD = 'email'
    REQUIRESD_FIELDS = ['email']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simple possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simple possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simple possible answer: All admins are staff
        return self.is_admin
