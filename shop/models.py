from django.db import models
from django.core.validators import RegexValidator
# Create your models here.

from django.core.urlresolvers import reverse
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

from decimal import Decimal

class Country(models.Model):
    name = models.CharField(max_length=30,validators = [RegexValidator(regex='^[A-Za-z\s]+$',message = 'Country name must have alphabets only',code= 'invalid_name'),])
    code = models.CharField(max_length = 3,unique = True,validators = [RegexValidator(regex='^[A-Z]{3}$',message = 'Country code must have all alphabets in caps only',code= 'invalid_code'),])
    
    def __str__(self):
        return self.name


class State(models.Model):
    name = models.CharField(max_length=30,validators = [RegexValidator(regex='^[a-zA-Z\s]+$',message = 'State name must have alphabets only',code= 'invalid_name'),])
    code = models.CharField(max_length =3,unique = True,validators = [RegexValidator(regex='^[A-Z]{3}$',message = 'State code must have all alphabets in caps only',code= 'invalid_code'),])
    country = models.ForeignKey(Country)

    def __str__(self):
        return self.name  

class City(models.Model):
    name = models.CharField(max_length=30,validators = [RegexValidator(regex='^[a-zA-Z\s]+$',message = 'City name must have alphabets only',code= 'invalid_name'),])
    code = models.CharField(max_length = 2, unique = True,validators = [RegexValidator(regex='^[A-Z]{2}$',message = 'City code must have all alphabets in caps only',code= 'invalid_code'),])
    state = models.ForeignKey(State)

    def __str__(self):
        return self.name


		
class Category(models.Model):
    name = models.CharField(max_length=200,db_index=True,validators = [RegexValidator(regex='^[a-zA-Z\s]+$',message = 'Category name must have alphabets only',code= 'invalid_name'),])
    slug = models.SlugField(max_length=200, db_index=True, unique=True)
    
    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])
        #return "%s?category_slug=self.slug"%reverse('shop:product_list')


class Product(models.Model):
    '''
    name:name of the product
    slug:to generate unique slug for url of each product.Used to create url
    image:optional product image.Need pillow for this

    category:Foreign Key to Category Model.
    One Category can have many Products
    Many Products belong to one Category

    description:Optional description of the product
    price:decimal field to store the price of the product upto 2 digit precision
    quantity:to store the quantity of products available in stock
    available:boolean field to indicate whether product is available or not.
    enable and disable product in catalog with this
    created:stores when the object was created
    updated:stores when the object was last updated
    '''
    category = models.ForeignKey(Category, related_name='products')
	
    name = models.CharField(max_length=200,db_index=True,validators = [RegexValidator(regex='^[a-zA-Z0-9_.:;,/\\-\s]+$',message = 'Product name must have alphabets only',code= 'invalid_name'),])
    slug = models.SlugField(max_length=200, db_index=True,unique=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)

    
    
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'),validators=[MinValueValidator(Decimal('0.00'))])
    quantity = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ('-created',)
        index_together = (('id', 'slug'),)
        

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])
		
    

class UserManager(BaseUserManager):
    use_in_migrations = True
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


		
class User(AbstractBaseUser, PermissionsMixin):

    GENDER_CHOICE = (('M','Male'),('F','Female'))
	
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True,validators = [RegexValidator(regex='^[a-zA-z\s]+$',message = 'First name must have alphabets only',code= 'invalid_name'),])
    last_name = models.CharField(_('last name'), max_length=30, blank=True,validators = [RegexValidator(regex='^[a-zA-Z\'\s]*$',message = 'Last name must have charecters only',code= 'invalid_name'),])
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff'), default=True)
    #avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)phone number validation not done
    phone_number = models.CharField(max_length=10,validators = [RegexValidator(regex='^[789]\d{9}$',message = 'Enter a valid Indian Phone Number',code= 'invalid_name'),])
    gender = models.CharField(max_length = 1, choices = GENDER_CHOICE)
    #need to add clean validation to date of birth i.e birthdate shouldnt be greater than today
    date_of_birth = models.DateField(null = True,blank = True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table='user'
        

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        pass

class Address(models.Model):
    address_line1 = models.CharField(max_length=250)
    address_line2 = models.CharField(max_length=250)
    city = models.ForeignKey(City)
    user = models.ForeignKey(User)
	
    def __str__(self):
        return self.address_line1+' '+self.address_line2

		
class Coupon(models.Model):
    code = models.CharField(max_length=50,unique=True,validators = [RegexValidator(regex='^[a-zA-z0-9]*$',message = 'Coupon Code must have AlphaNumeric charecters only',code= 'invalid_code'),])
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(100)])
    active = models.BooleanField()

    def __str__(self):
        return self.code

		
class Order(models.Model):
    user = models.ForeignKey(User)
    shipping_address = models.ForeignKey(Address)
    # postal_code = models.CharField(_('postal code'),
                                   # max_length=20)
    # city = models.CharField(_('city'),
                            # max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    coupon = models.ForeignKey(Coupon,related_name='orders',null=True,blank=True)
    discount = models.IntegerField(default=0,validators=[MinValueValidator(0),MaxValueValidator(100)])

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return 'Order {}'.format(self.id)

    def get_total_cost(self):
        total_cost = sum(item.get_cost() for item in self.items.all())
        return total_cost - total_cost * (self.discount / Decimal('100'))


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items')
    product = models.ForeignKey(Product, related_name='order_items')
    price = models.DecimalField(max_digits=10, decimal_places=2,validators=[MinValueValidator(Decimal('0.00'))])
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return self.price * self.quantity
 