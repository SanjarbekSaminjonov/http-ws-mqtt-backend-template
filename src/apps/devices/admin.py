from django import forms
from django.contrib import admin

from apps.devices.models import Device


class DeviceForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = Device
        fields = ["name", "username", "password", "password_hash", "salt"]
        readonly_fields = ["password_hash", "salt"]

    def save(self, commit=True):
        device: Device = super().save(commit=False)
        new_password = self.cleaned_data.get("password")
        if new_password:
            device.set_password(self.cleaned_data["password"])
            if commit:
                device.save()
        return device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "username")
    search_fields = ("name", "username")
    readonly_fields = ("password_hash", "salt")
    form = DeviceForm
