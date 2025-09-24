from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from .models import Material, UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()


@receiver(post_migrate)
def ensure_default_materials(sender, **kwargs):
    if sender.name != "core":
        return
    existing = set(Material.objects.values_list("name", flat=True))
    for material_name in Material.default_materials():
        if material_name not in existing:
            Material.objects.get_or_create(name=material_name)
