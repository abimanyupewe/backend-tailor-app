from django.db import models
from users.models import TailorProfile
from location_field.models.plain import PlainLocationField

class TailorService(models.Model):
    tailor = models.ForeignKey(TailorProfile, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_duration_days = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.tailor.shop_name}"

class ShopLocation(models.Model):
    tailor = models.OneToOneField(TailorProfile, on_delete=models.CASCADE, related_name='location')
    address = models.TextField()
    city = models.CharField(max_length=255, blank=True, null=True)
    location = PlainLocationField(based_fields=['city'], zoom=13, default='-7.9666204,112.6326321', blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if self.location:
            try:
                lat, lon = self.location.split(',')
                self.latitude = float(lat)
                self.longitude = float(lon)
            except ValueError:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Location: {self.tailor.shop_name}"

class TailorPost(models.Model):
    tailor = models.ForeignKey(TailorProfile, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='tailor_posts/')
    caption = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.tailor.shop_name} at {self.created_at}"
