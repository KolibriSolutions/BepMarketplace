from django.conf.urls import url

from . import views
# define all kinds of file downloads here.
# Files can be downloaded using their filename (for backward compatibility with file edit) or using their object ID
app_name = 'download'

reguuid = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}.[A-z]{1,5}"

urlpatterns = [
    # public files
    url(r'publicfile/(?P<fileid>[0-9]+)$', views.PublicFiles, name='publicfile'),  # by object-id
    url(r'public_files/(?P<timeslot>[0-9]+)/(?P<fileid>'+reguuid+')$', views.PublicFiles, name='public_files'),  # uri

    # proposal attachements
    url(r'proposalfile/(?P<ty>[a-z])/(?P<fileid>[0-9]+)$', views.ProposalFiles, name='proposalfile'),  # object-id
    url(r'proposal_(?P<proposalid>[0-9]+)/(?P<fileid>'+reguuid+')$', views.ProposalFiles, name='proposal_files'),  # uri

    # student files (professionalskills)
    url(r'studentfile/(?P<fileid>[0-9]+)$', views.StudentFiles, name='studentfile'),  # object-id
    url(r'dist_(?P<distid>[0-9]+)/(?P<fileid>' + reguuid + ')$', views.StudentFiles, name='student_files'),  # uri
]
