from django.contrib import admin
from .models import Item, Order, OrderItem, Payment, Address, Coupon, Refund
# Register your models here.


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'ordered',
        'being_delivered',
        'received',
        'refund_requested',
        'refund_granted',
        'user',
        'billing_address',
        'shipping_address',
        'payment',
        'coupon'
    ]

    list_display_links = [
        'user',
        'billing_address',
        'shipping_address',
        'payment',
        'coupon'

    ]
    list_filter = [
        'ordered',
        'being_delivered',
        'received',
        'refund_requested',
        'refund_granted'
    ]
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'appartment_address',
        'country',
        'postcode',
        'address_type',
        'default',
    ]
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user', 'street_address', 'appartment_address', 'zip']

    class Meta:
        verbose_name_plural = 'Addresses'


admin.site.register(Item)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Address, AddressAdmin)
admin.site.register(Coupon)
admin.site.register(Refund)
