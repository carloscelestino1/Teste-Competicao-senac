from django.db import models

class User (models.Model):
    cpf = models.CharField(max_length=14, primary_key=True)
    username = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    role = models.CharField(default="Client")
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
    
class Event (models.Model):
    title = models.CharField(max_length=255)
    max_capacity = models.IntegerField()
    description = models.TextField()
    start_at = models.TimeField()
    date = models.DateField()
    status = models.CharField(max_length=50, default="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    User_cpf = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class EventAdress (models.Model):
    Event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    uf = models.CharField(max_length=2)
    city = models.CharField(max_length=60)
    neighborhood = models.CharField(max_length=60)
    street = models.CharField(max_length=60)
    number = models.CharField(max_length=5)
    complement = models.CharField(max_length=50, null=True, blank=True)
    cep = models.CharField(max_length=9)

    def __str__(self):
        id = str(self.Event_id)
        return id
    
class Sector (models.Model):
    title = models.CharField(max_length=60)
    max_capacity = models.IntegerField()
    status = models.CharField(max_length=50, default="available")
    Event_id = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        id = str(self.Event_id)
        title = str(self.title)
        sector_title = id + '_' +title
        return sector_title
    
class Seat (models.Model):
    number = models.IntegerField()
    row = models.CharField(max_length=1)
    status = models.CharField(max_length=50, default="Available")
    Sector_id = models.ForeignKey(Sector, on_delete=models.CASCADE)

    def __str__(self):
        event_sector = str(self.Sector_id)
        row = str(self.row)
        number = str(self.number)
        seat = event_sector + '_' + row + number
        return seat
    
class Ticket (models.Model):
    ticket_code = models.CharField(max_length=36)
    Seat_id = models.ForeignKey(Seat, on_delete=models.CASCADE)
    Event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    User_cpf = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.ticket_code