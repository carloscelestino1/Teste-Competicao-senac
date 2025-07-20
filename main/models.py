from django.db import models
    
class Event(models.Model):
    title = models.CharField(max_length=255)
    max_capacity = models.IntegerField()
    description = models.TextField()
    start_at = models.TimeField()
    date = models.DateField()
    status = models.CharField(max_length=50, default="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    User_cpf = models.CharField(max_length=50)
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)  # novo campo

    def __str__(self):
        return self.title


class EventAdress(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, null=True)
    uf = models.CharField(max_length=2)
    city = models.CharField(max_length=60)
    neighborhood = models.CharField(max_length=60)
    street = models.CharField(max_length=60)
    number = models.CharField(max_length=5)
    complement = models.CharField(max_length=50, null=True, blank=True)
    cep = models.CharField(max_length=9)

    def __str__(self):
        return f"{self.street}, {self.number} - {self.city}/{self.uf}"

    
from django.core.exceptions import ValidationError

class Sector(models.Model):
    STATUS_CHOICES = [
        ('available', 'Disponível'),
        ('reserved', 'Reservado'),
        ('unavailable', 'Indisponível'),
    ]

    title = models.CharField(max_length=60)
    max_capacity = models.IntegerField()
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='available'
    )
    Event_id = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.Event_id}_{self.title}"



class Ticket(models.Model):
    ticket_code = models.CharField(max_length=36)
    Event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    User_cpf = models.CharField(max_length=50)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.ticket_code

