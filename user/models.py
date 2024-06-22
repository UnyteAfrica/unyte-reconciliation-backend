from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff set to True')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser set to True')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=40,
                                  blank=True,
                                  null=True,
                                  help_text='User firstname')
    middle_name = models.CharField(max_length=40,
                                   blank=True,
                                   null=True,
                                   help_text='User middle name')
    last_name = models.CharField(max_length=40,
                                 blank=True,
                                 null=True,
                                 help_text='User lastname')
    is_active = models.BooleanField(default=True,
                                    help_text='Set to know active users on the platform. Instead of deleting a user, '
                                              'set to False')
    is_staff = models.BooleanField(default=False,
                                   help_text='Defined to know if a user is a staff')
    created_at = models.DateTimeField(auto_now_add=True,
                                      help_text='Date user was created')
    updated_at = models.DateTimeField(auto_now=True,
                                      help_text='Date when any update is made to the user model')
    gampID = models.EmailField(unique=True,
                               null=True,
                               blank=True,
                               help_text='GAMP ID for users associated with GAMP')
    is_verified = models.BooleanField(default=False,
                                      help_text='Check to know whether an agent or insurer is verified')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
