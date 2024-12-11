from django.db import models

# Create your models here.

from django.db import models

# Create your models here.

class Contact (models.Model):
    full_name=models.CharField(max_length=124)
    email=models.EmailField()
    message=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)


    def __str__(self) -> str:
        return self.email