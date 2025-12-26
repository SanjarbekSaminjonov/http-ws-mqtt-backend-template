import os
import hashlib
from django.db import models


class BaseDevice(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=256)
    salt = models.CharField(max_length=64)

    def set_password(self, raw_password):
        self.salt = os.urandom(32).hex()
        self.password_hash = hashlib.sha256(
            (raw_password + self.salt).encode()
        ).hexdigest()

    def check_password(self, raw_password):
        return (
            self.password_hash
            == hashlib.sha256((raw_password + self.salt).encode()).hexdigest()
        )

    class Meta:
        abstract = True


class Device(BaseDevice):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name
