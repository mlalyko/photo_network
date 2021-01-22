from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)

    objects = models.Manager()

    def __str__(self):
        return self.name
    

class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    objects = models.Manager()

    def __str__(self):
        return f'{self.name} ({self.country})'


class Item(models.Model):
    name = models.CharField(max_length=100, unique=True)

    objects = models.Manager()

    def __str__(self):
        return self.name


class User(models.Model):
    name = models.CharField(max_length=100, unique=True)
    moderator = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name


class PhotoQuerySet(models.query.QuerySet):
    def unapproved(self):
        return self.filter(approved=False)

    def by_essence(self, essence_type, essence_name):
        """
        get all approved photos with basic_key == essence_type
        :param essence_type: one of the basic keys
        :param essence_name: name of essence (ex. 'Chair' or 'Russia')
        :return: filtered queryset
        """
        if essence_type == 'item':
            item = Item.objects.filter(name__iexact=essence_name)
            if item:
                return self.filter(approved=True, item=item.first().id, basic_key=essence_type)
        elif essence_type == 'city':
            city = City.objects.filter(name__iexact=essence_name)
            if city:
                return self.filter(approved=True, city=city.first().id, basic_key=essence_type)
        elif essence_type == 'country':
            country = Country.objects.filter(name__iexact=essence_name)
            if country:
                return self.filter(approved=True, country=country.first().id, basic_key=essence_type)

    def by_type(self, essence_name):
        """
        get all approved photos that have essence_name
        :param essence_name: name of essence (ex. 'Chair' or 'Russia')
        :return: filtered queryset
        """
        item = Item.objects.filter(name__iexact=essence_name)
        city = City.objects.filter(name__iexact=essence_name)
        country = Country.objects.filter(name__iexact=essence_name)

        if country:
            return self.filter(approved=True, country=country.first().id)
        elif city:
            return self.filter(approved=True, city=city.first().id)
        elif item:
            return self.filter(approved=True, item=item.first().id)


class PhotoManager(models.Manager):
    def get_query_set(self):
        return PhotoQuerySet(self.model, using=self._db)
    
    def all(self):
        return self.get_query_set()

    def unapproved(self):
        return self.get_query_set().unapproved()
    
    def by_essence(self, essence_type, essence_name):
        return self.get_query_set().by_essence(essence_type, essence_name)

    def by_type(self, essence_name):
        return self.get_query_set().by_type(essence_name)


class Photo(models.Model):
    photo = models.ImageField(upload_to='media/photos/')
    approved = models.BooleanField(default=False)
    
    basic_key = models.CharField(max_length=50, choices=(('city', 'City'), ('country', 'Country'), ('item', 'Item')),
                                 default='item')
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    objects = PhotoManager()
        
    def __str__(self):
        returning_name = ''
        for i in (self.item, self.city, self.country):
            if i:
                returning_name += str(i) + ' '
        return returning_name
