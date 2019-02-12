from django.contrib import admin

from .models import Proposal, ProposalImage, ProposalAttachment, Favorite


class ProposalAdmin(admin.ModelAdmin):
    search_fields = ['Title', ]
    list_filter = ('Track', 'Status', 'TimeSlot')  # TODO add group back.


class ProposalFileAdmin(admin.ModelAdmin):
    search_fields = ['Proposal__Title', 'Caption']


admin.site.register(Proposal, ProposalAdmin)
admin.site.register(ProposalImage, ProposalFileAdmin)
admin.site.register(ProposalAttachment, ProposalFileAdmin)
admin.site.register(Favorite)
