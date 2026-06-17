from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from .user import User


class Profile(models.Model):
    user= models.OneToOneField(User,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email
    

@receiver(post_save,sender=User)
def create_user_profile(sender,instance,created,**kwargs):
    if created:
        Profile.objects.create(user=instance)
