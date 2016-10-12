import json

from .cart import Cart
from django.http import HttpResponse
from django.views.generic.base import View
from django.shortcuts import render,get_object_or_404,redirect

from .models import Country, State,City,Category,Product,OrderItem



from django.urls import reverse
from django.contrib.auth.views import deprecate_current_app,_get_login_redirect_url
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, get_user_model, login as auth_login,
    logout as auth_logout, update_session_auth_hash,
)
from django.shortcuts import resolve_url
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm,
)
from django.http import HttpResponseRedirect, QueryDict
from django.contrib.sites.shortcuts import get_current_site
from django.template.response import TemplateResponse
from django.conf import settings


from .forms import CartAddProductForm,OrderCreateForm
from django.views.decorators.http import require_POST


class Getstates(View):
    """Class based view to get states related to country"""

    def get(self, request):

        """
        **Type:** public.

        **Arguments:**

            - request: Httprequest object.

        **Returns:** Dictionary containing  state details.

        **Raises:** Nothing.

        Following steps are performed in this method

        - Get country_id from request.GET.get('country_id').

        - Prepare an empty list say state_list.

        - Get states for country_id using.

        - for state in states
            - prepare a dictionary {"id": state.id, 'value': state.name}

            - append this dictionary to state_list.
        - Return state_list.
        """

        country_id = request.GET.get("country")
        list_states = []
        dict_states = {}
        # Get all active states from given country.
        country = get_object_or_404(Country, pk=country_id)
        states = country.state_set.order_by('name')
        for state in states:
            dict_states = {"id" : state.id, 'value' : state.name}
            list_states.append(dict_states)
        return HttpResponse(json.dumps(list_states))

class Getcities(View):
    """Class based view to get locations related to state"""

    def get(self, request):
        """
        **Type:** public.

        **Arguments:**

            - request: Http request object.

        **Returns:** Dictionary containing location details..

        **Raises:** Nothing.

        Following steps are performed in this method

        - Get state_id from *request.GET.get('state_id')*.

        - Prepare an empty list say *c*.

        - Get locations for *state_id*.

        - for location in locations
            - prepare a dictionary {"id": location.id, 'value': location.name}

            - append this dictionary to *location_list*.
        - Return location_list.
        """

        state_id = request.GET.get("state")
        list_cities = []
        dict_cities = {}
        # Get all active locations from given state.
        state = get_object_or_404(State, pk=state_id)
        cities = state.city_set.order_by('name')

        for city in cities:
            dict_cities = {"id" : city.id, 'value' : city.name}
            list_cities.append(dict_cities)
        return HttpResponse(json.dumps(list_cities))

#, category_slug=None
def product_list(request,category_slug = None):
    '''
    categories:All the categories from the Category model
    product:All the available products in the Product model
    from the category slug of the category object recieved in the 
    request, I would retrieve the category object based on the slug 
    then i would find all the products based on the category	
    and then return the catgory and the products within that category 
    in the context 
    '''
    category = None
    categories = Category.objects.all()
    #print(categories)
    products = Product.objects.filter(available=True)
    #print(products)
    #print(category_slug)
    #category_slug = request.GET.get('category_slug')
    if category_slug:
        category = get_object_or_404(Category,slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'shop/product/list.html', {'category': category,
                                                      'categories': categories,
                                                      'products': products})
													  
def product_detail(request, id, slug):
    product = get_object_or_404(Product,id=id,slug=slug,available=True)
    cart_product_form = CartAddProductForm()
    return render(request,'shop/product/detail.html',{'product': product,'cart_product_form':cart_product_form})

	
@deprecate_current_app
@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          extra_context=None, redirect_authenticated_user=False):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.POST.get(redirect_field_name, request.GET.get(redirect_field_name, ''))

    if redirect_authenticated_user and request.user.is_authenticated:
        redirect_to = _get_login_redirect_url(request, redirect_to)
        print(request.path,"------")
        if redirect_to == request.path:
            raise ValueError(
                "Redirection loop for authenticated user detected. Check that "
                "your LOGIN_REDIRECT_URL doesn't point to a login page."
            )
        return HttpResponseRedirect(redirect_to)
    elif request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())#######
            if request.user.is_superuser:
                print(redirect_to,"**********")
                return HttpResponseRedirect(_get_login_redirect_url(request, redirect_to))
            else:
                return HttpResponseRedirect(reverse("shop:product_list"))#use reverse.
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@deprecate_current_app
@never_cache
def logout(request, next_page=None,
           template_name='registration/logged_out.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           extra_context=None):
    """
    Logs out the user and displays 'You are logged out' message.
    """
    print(request.user.email,"$$$$$$")
    if not request.user.is_superuser:
        next_page=reverse("shop:product_list")
        
    auth_logout(request)

    if next_page is not None:
        next_page = resolve_url(next_page)
    elif settings.LOGOUT_REDIRECT_URL:
        next_page = resolve_url(settings.LOGOUT_REDIRECT_URL)

    if (redirect_field_name in request.POST or
            redirect_field_name in request.GET):
        next_page = request.POST.get(redirect_field_name,
                                     request.GET.get(redirect_field_name))
        # Security check -- don't allow redirection to a different host.
        if not is_safe_url(url=next_page, host=request.get_host()):
            next_page = request.path

    if next_page:
        # Redirect to this page until the session has been cleared.
        return HttpResponseRedirect(next_page)

    current_site = get_current_site(request)
    context = {
        'site': current_site,
        'site_name': current_site.name,
        'title': _('Logged out')
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)

@require_POST
def cart_add(request,product_id):
    cart = Cart(request)
    product = get_object_or_404(Product,id = product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product = product,quantity = cd['quantity'], update_quantity = cd['update'])
        return redirect('shop:cart_detail')

def cart_remove(request,product_id):
    cart = Cart(request)
    product = get_object_or_404(Product,id = product_id)
    cart.remove(product)
    return redirect('shop:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial = {'quantity':item['quantity'],'update':True})
    return render(request,'cart/detail.html',{'cart':cart})###
	

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order = order,product = item['product'],price=item['price'],quantity = item['quantity'])
            #clear the cart
            cart.clear()	
            return render(request,'orders/order/created.html',{'order':order})
			