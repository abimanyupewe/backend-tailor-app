from django.db import models
from users.models import TailorProfile

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
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    def __str__(self):
        return f"Location: {self.tailor.shop_name}"

class TailorPost(models.Model):
    tailor = models.ForeignKey(TailorProfile, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='tailor_posts/')
    caption = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.tailor.shop_name} at {self.created_at}"
