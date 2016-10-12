from django.contrib import admin
from .models import User,Category,Product,Address,Country,City,State,Order,OrderItem,Coupon
# Register your models here.
from .forms import UserPasswordFixForm
#'last_login',

class CountryAdmin(admin.ModelAdmin):
    model = Country

admin.site.register(Country,CountryAdmin)

class StateAdmin(admin.ModelAdmin):
    model = State

admin.site.register(State,StateAdmin)

class CityAdmin(admin.ModelAdmin):
    model = City
    list_display = ['name','get_state','get_country']
	
    def get_state(self,obj):
        return obj.state
    get_state.short_description = 'state'
    def get_country(self,obj):
        return obj.state.country

admin.site.register(City,CityAdmin)

class AddressInline(admin.TabularInline):
    model = Address
    extra = 1
    #inlines = [CityInline,StateInline,CountryInline]
	
# CREATE TABLE "user_useraddress" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
# "user_id" integer NOT NULL REFERENCES "user" ("id"), "address_id" integer NOT NULL REFERENCES "shop_address" ("id"));


class UserAdmin(admin.ModelAdmin):
    form = UserPasswordFixForm
    fieldsets = (('User Details',{'classes':('collapse',),'fields':('first_name','last_name','email','password1','password2','gender','phone_number','address1', 'address2', 'country', 'state', 'city','date_of_birth','is_active','is_staff','is_superuser',),}),)
    list_display = ['first_name','last_name','email','is_active','is_staff','last_login']
    list_display_links = ['first_name','last_name','email','is_active','is_staff']
    #list_editable = ['first_name','last_name','email']
    #inlines = [AddressInline,]
	
    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js', # jquery
            'django_js_reverse/js/reverse.js',
            'shop/js/address.js',   # app static folder
        )

    def save_model(self,request,obj,form,change):
        #Address()
        #print(form)
        #obj.address.address_line
        
        address1 = form.cleaned_data['address1']
        address2 = form.cleaned_data['address2']
        city_id = form.cleaned_data['city']
        state_id = form.cleaned_data['state']
        country_id = form.cleaned_data['country']
        # user_city = City.objects.filter(id=city_id)
        # user_city.save()
        # user_state = State.objects.filter(id=state_id)
        # user_state.save()
        # user_country = Country.objects.filter(id=country_id)
        # user_country.save()
        obj.save()
        print(obj)
        old_user_address = Address.objects.filter(user = obj.id)
        old_user_address.delete()
        user_address=Address(address_line1=address1,address_line2=address2,city=city_id,user=obj)
        user_address.save()
        # user_address.save()
        # if change:
            # obj.address_set.       		
        #print(obj.address_set.create(address_line1=address1,address_line2=address2,city=city_id))       
        #obj.address.address_line1 == form.cleaned_data['address1'] 
        super(UserAdmin,self).save_model(request,obj,form,change)
        

	
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name','slug']
    fields = ('name','slug')
    prepopulated_fields = {'slug':('name',)}

	
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','image','price','category','quantity','available','created','updated']
    list_filter = ['category','available','created','updated']
    list_editable = ['price','quantity','available','category','image']
    fields = ('name','slug','price','category','quantity','available','image')
    prepopulated_fields = {'slug':('name',)}
	
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name']
    fields = ('name',)

class StateAdmin(admin.ModelAdmin):
    pass
	

admin.site.register(User,UserAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Address)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
	
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','user','shipping_address','paid','created','updated']
    list_filter = ['paid','created','updated']
    inlines = [OrderItemInline]

admin.site.register(Order,OrderAdmin)

class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'valid_from', 'valid_to', 'discount', 'active']
    list_filter = ['active', 'valid_from', 'valid_to']
    search_fields = ['code']

admin.site.register(Coupon, CouponAdmin)