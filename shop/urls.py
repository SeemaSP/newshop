from django.conf.urls import url

from .views import Getstates, Getcities,product_list,product_detail,cart_detail,cart_add,cart_remove,order_create

urlpatterns = [
    url(r'^search/states$',
        Getstates.as_view(),
        name='search-states-view'),

    url(r'^search/cities$',
        Getcities.as_view(),
        name='search-cities-view'),
    url(r'^orders/create/$',order_create,name='order_create'),
    url(r'^cart/',cart_detail,name='cart_detail'),
    url(r'^cart/add/(?P<product_id>\d+)/$', cart_add , name = 'cart_add'),
    url(r'^cart/remove/{?P<product_id>\d+}/$',cart_remove,name='cart_remove'),
    url(r'^$',product_list,name='product_list'),
    url(r'^(?P<category_slug>[-\w]+)/$',product_list,name='product_list_by_category'),
    url(r'^(?P<id>\d+)/(?P<slug>[-\w]+)/$',product_detail,name='product_detail'),
]
