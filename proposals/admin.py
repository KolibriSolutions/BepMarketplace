from django.contrib import admin
from .models import Proposal, ProposalImage, ProposalAttachment

admin.site.register(Proposal)
admin.site.register(ProposalImage)
admin.site.register(ProposalAttachment)