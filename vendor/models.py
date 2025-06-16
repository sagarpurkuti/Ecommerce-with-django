from django.db import models

# Create your models here.
class Advertisement(models.Model):
    ad_name = models.CharField(max_length=250, blank=True)
    image   = models.ImageField(upload_to='store/products/', max_length=255)

    def __str__(self):
        return self.ad_name

    
    class Meta:
        verbose_name = 'advertisement'
        verbose_name_plural = 'advertisements'