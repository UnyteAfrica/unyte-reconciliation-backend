from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff set to True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser set to True")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    reference_id = models.CharField(max_length=50, null=False, blank=False, help_text="Reference id for new user")
    is_active = models.BooleanField(
        default=True, help_text="Set to know active users on the platform. Instead of deleting a user, " "set to False"
    )
    is_staff = models.BooleanField(default=False, help_text="Defined to know if a user is a staff")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date user was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date when any update is made to the user model")
    is_verified = models.BooleanField(default=False, help_text="Check to know whether an agent or insurer is verified")
    is_insurer = models.BooleanField(default=False, help_text="Check to see if user is of type insurer")
    is_agent = models.BooleanField(default=False, help_text="Check to see if user is of type agent")
    is_merchant = models.BooleanField(default=False, help_text="Check to see if user if type merchant")

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "USER"
        verbose_name_plural = "USERS"

    def __str__(self):
        return self.email
