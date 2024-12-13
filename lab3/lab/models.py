from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = (
        ('electronics', 'Electronics'),
        ('furniture', 'Furniture'),
        ('clothing', 'Clothing'),
        ('toys', 'Toys'),
        ('books', 'Books'),
        ('sports', 'Sports')
    )

    name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    category = models.CharField(max_length=20, null=True, choices=CATEGORY_CHOICES)
    stock_quantity = models.IntegerField(null=True)
    tags = models.CharField(max_length=255, null=True)


class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
