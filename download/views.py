#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core import signing
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from sendfile import sendfile

from general_model import get_ext
from general_view import get_grouptype
from professionalskills.models import StudentFile
from proposals.models import Proposal
from proposals.models import ProposalAttachment, ProposalImage
from support.models import PublicFile
from timeline.models import TimeSlot
from presentations.utils import planning_public
"""
Uploads go to /media/ directory
Download links point to /download
Downloads can either be by file path (old way, as if we're using a public file storage pool). Used by editfile widget
or as a primary key of the object the file belongs to (new way). Used in all templates.
"""


@login_required
def public_files(request, fileid, timeslot=None):
    """
    Public files, uploaded by type3, viewable on index.html, model in support-app

    :param request:
    :param fileid: The ID of the public file to download.
    :param timeslot: The timeslot id, used if the file is accessed by URI. This corresponds to the directory name.
    :return: file download
    """
    # first try PK, then filename
    try:
        obj = PublicFile.objects.get(id=fileid)
    except:
        # find by filename, used for edit widget for public file edit.
        ts = get_object_or_404(TimeSlot, id=timeslot)
        obj = get_object_or_404(PublicFile, File='public_files/{}/{}'.format(ts.id, fileid))
    return sendfile(request, obj.File.path, attachment=True, attachment_filename=obj.OriginalName)


def project_files(request, fileid, project_id=None, ty=None):
    """
    project files, attachements or images, viewable on project details, model in projects-app
    Because projects images and attachements are seperate models, but are stored in the same folder, the ID is not
    unique, therefore only the UUID is possible to get the file.
    Mode 1: (old) projectid gives the folder to search in, fileid is the filename (an UUID)
    Mode 2: (new) ty is either "a" or "i" to refer to image or attachement and fileid is the ID (pk) of-
     the corresponding model
    When the file is an image, it is send inline, otherwise it is send as attachement.

    :param request:
    :param fileid: id of the project file.
    :param project_id: id of the project, corresponds to directory name appendix.
    :param ty: type, image or attachment
    :return: file download
    """
    if not request.user.is_authenticated:
        # allow anonymous users when viewing from a sharelink
        # make sure referrerpolicy is set on links, otherwise HTTP_REFERER might not be available.
        # https: // bugs.chromium.org / p / chromium / issues / detail?id = 455987
        if "HTTP_REFERER" in request.META:
            ref = request.META["HTTP_REFERER"].split('/')
            if 'share' in ref:  # url  /api/share/<sharetoken>/
                # check if sharetoken is valid. Same as in api.views
                try:
                    pk = signing.loads(ref[-2], max_age=settings.MAXAGESHARELINK)
                except signing.SignatureExpired:
                    raise PermissionDenied('Not allowed!')
                except signing.BadSignature:
                    raise PermissionDenied('Not allowed!')
                if not Proposal.objects.filter(pk=pk).exists():
                    # a check whether this image/attachment belongs to this project would be better
                    # but is more difficult.
                    raise PermissionDenied('Not allowed!')
                pass  # anonymous user viewing a valid share link
            else:
                raise PermissionDenied('Not allowed!')  # random referred
        else:  # direct access to file
            raise PermissionDenied('Not allowed!')

    # first try filename as image, then as attachment
    if project_id:  # via a project id and a filename (UUID) as fileid, the old way
        ext = get_ext(fileid)
        if ext in settings.ALLOWED_PROPOSAL_IMAGES:
            obj = get_object_or_404(ProposalImage, File='proposal_{}/{}'.format(project_id, fileid))
            return sendfile(request, obj.File.path, attachment=False)  # serve inline
        elif ext in settings.ALLOWED_PROPOSAL_ATTACHMENTS:
            obj = get_object_or_404(ProposalAttachment, File='proposal_{}/{}'.format(project_id, fileid))
            return sendfile(request, obj.File.path, attachment=True, attachment_filename=obj.OriginalName)
        else:
            raise PermissionDenied("File extension not allowed.")
    elif ty:  # by specifying image or attachement and a ID (pk) as fileid, the new way
        if ty == "a":  # attachment, like pdf
            obj = get_object_or_404(ProposalAttachment, id=fileid)
            return sendfile(request, obj.File.path, attachment=True, attachment_filename=obj.OriginalName)
        elif ty == "i":  # image
            obj = get_object_or_404(ProposalImage, id=fileid)
            return sendfile(request, obj.File.path)
        else:
            raise PermissionDenied("Invalid request.")
    else:
        raise PermissionDenied("Invalid request.")


@login_required
def student_files(request, fileid, distid=''):
    """
    Student file, uploaded by student as professionalskill. Model in students-app
    Type3 and 4 (support and profskill) staff can see all studentfiles.
    Responsible and assistant of student can view files.
    Student itself can view its own files

    :param request:
    :param fileid: id of the student file.
    :param distid: id of the distribution of the student.
    :return:
    """
    # first try PK, then filename
    try:
        obj = StudentFile.objects.get(id=fileid)
    except (StudentFile.DoesNotExist, ValueError):
        # accessed by distribution, then by filename, (the old way)
        obj = get_object_or_404(StudentFile, File='dist_{}/{}'.format(distid, fileid))

    if get_grouptype("3") in request.user.groups.all() \
            or Group.objects.get(name='type4staff') in request.user.groups.all() \
            or obj.Distribution.Proposal.ResponsibleStaff == request.user \
            or request.user in obj.Distribution.Proposal.Assistants.all() \
            or obj.Distribution.Student == request.user:
        # Allowed to view this file
        pass
    elif planning_public():
        try:
            if request.user in obj.Distribution.presentationtimeslot.Presentations.Assessors.all():
                # assessor can view files
                pass
            else:
                # user is not assessor or planning is not public
                raise PermissionDenied("You are not allowed to view this file")
        except:
            # presentation not yet planned or presentationoptions do not exist.
            raise PermissionDenied("You are not allowed to view this file")

    else:
        # not allowed
        raise PermissionDenied("You are not allowed to view this file.")

    return sendfile(request, obj.File.path, attachment=True, attachment_filename=obj.OriginalName)
