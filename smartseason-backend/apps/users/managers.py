"""Custom manager because we use email (not username) as login identifier."""
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create(self, email, password, **extra):
    if not email:
        raise ValueError("Email is required")

    email = self.normalize_email(email)

    full_name = extra.pop("full_name", None)
    role = extra.pop("role", "field_agent")

    user = self.model(
        email=email,
        full_name=full_name,
        role=role,
        **extra
    )

    user.set_password(password)
    user.save(using=self._db)
    return user
    
def create_user(self, email, password=None, **extra):
    extra.setdefault("role", "field_agent")
    extra.setdefault("is_staff", False)
    extra.setdefault("is_superuser", False)
    return self._create(email, password, **extra)
    def create_superuser(self, email, password=None, **extra):
        extra.update(is_staff=True, is_superuser=True, role="admin", is_active=True)
        return self._create(email, password, **extra)
