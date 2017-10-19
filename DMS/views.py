from django.conf.urls import url
from django.contrib.auth import authenticate, login as auth_login, logout
# from django.contrib.auth.views import *
from django.core.mail import EmailMessage
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import FormView
from rest_framework import permissions
from rest_framework import viewsets
from reversion.models import Version
from reversion.views import RevisionMixin
from reversion_compare.views import HistoryCompareDetailView

from .forms import FolderForm, DocumentForm
from .models import Document, Folder, CustomUser
from .serializers import DocumentSerializer
from django.contrib.auth.models import Group


class DocumentHistoryCompareView(HistoryCompareDetailView):
    model = Document


def user_login(request):
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a CustomUser object is returned if it is.
        user = authenticate(email=email, password=password)
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:

                auth_login(request, user)
                return HttpResponseRedirect('/DMS/index/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your DMS account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print("Invalid login details: {0}, {1}".format(email, password))
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'DMS/login.html', {})


def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/DMS/login/')


def index(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/DMS/login/')
    else:
        user = request.user
        folder_name = Folder.objects.all()
        document_list = Document.objects.all()
        query = request.GET.get("q")
        if query:
            document_list = document_list.filter(Q(keywords__icontains=query) or
                                                 # Q(query in type)
                                                 Q(type__icontains=query) or
                                                 Q(name__contains=query) or
                                                 Q(owner__first_name=query)or
                                                 Q(creation_time__month=query)or
                                                    Q(creation_time__day=query)


                                                 ).distinct()
            return render(request, 'DMS/documents.html', {'document_list': document_list})
        context = {

            'folder_name': folder_name,
            'user': user
        }

        return render(request, 'DMS/index.html', context)


def FolderDetail(request, pk):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/DMS/login/')
    else:
        folder = get_object_or_404(Folder, pk=pk)
        folder_name = Folder.objects.all()
        # users_in_group = Group.objects.get(name="HR").user_set.all()
        document_list = Document.objects.filter(folder=folder)
        documents = []
        for doc in document_list:

            # Load a queryset of versions for a specific model instance.
            versions = Version.objects.get_for_object(doc)
            document_versions = []
            for version in versions:
                document_versions.append({
                    'date': version.revision.date_created,
                    'path': version.field_dict['path']

                })
            documents.append({
                'doc': doc,
                'versions': document_versions
            })
        query = request.GET.get("q")
        if query:
            document_list = document_list.filter(Q(keywords__icontains=query) |
                                                 # Q(query in type)|
                                                 Q(type__icontains=query) |
                                                 Q(name__contains=query) |
                                                 Q(owner__first_name=query)
                                                 ).distinct()
            return render(request, 'DMS/documents.html', {'document_list': document_list})

        context = {
            'folder': folder,
            'folder_name': folder_name,
            'documents': documents,
            # 'users_in_group':users_in_group
        }

        return render(request, "DMS/folder-details.html", context)


def DocumentView(request):
    document_list = Document.objects.all()
    query = request.GET.get("q")
    if query:
        document_list = document_list.filter(Q(keywords__icontains=query)
                                             # Q(type__icontains =query)|
                                             # Q(name__icontains=query)|
                                             # Q(owner__icontains=query)|
                                             # Q(description__icontains=query)
                                             ).distinct()
        return render(request, 'DMS/documents.html', {'document_list': document_list})

    return render(request, 'DMS/documents.html', {'document_list': document_list})


def versions(request, pk, document_id):
    folder = get_object_or_404(Folder, pk=pk)
    docs = get_object_or_404(Document, pk=document_id)
    document_list = Document.objects.filter(folder=folder)
    user =CustomUser.objects.all()
    documents = []
    for doc in document_list:

        # Load a queryset of versions for a specific model instance.
        versions = Version.objects.get_for_object(doc)
        document_versions = []
        for version in versions:
            document_versions.append({
                'date': version.revision.date_created,
                'path': version.field_dict['path'],
                'comment': version.revision.comment,
                'user_id': version.revision.user_id

            })
        documents.append({
            'doc': doc,
            'versions': document_versions
        })

    context = {
        'folder': folder,
        'documents': documents,
        'docs': docs,
        'user':user
    }
    return render(request, 'DMS/history.html', context)


def create_document(request, folder_id):
    # form = forms.DocumentForm()
    form = DocumentForm(request.POST or None, request.FILES or None)
    folder = get_object_or_404(Folder, pk=folder_id)
    # foldern = get_object_or_404(Folder,)
    folder_name = Folder.objects.all()
    if form.is_valid():
        folder_document = folder.document_set.all()
        for d in folder_document:
            if d.name == form.cleaned_data.get("name"):
                context = {
                    'folder': folder,
                    'form': form,
                    'folder_name': folder_name,
                    'error_message': 'You already added that document',
                }
                return render(request, 'DMS/folder-details.html', context)
        document = form.save(commit=False)
        document.folder = folder
        document.save()
        return HttpResponseRedirect('/DMS/' + folder_id)
    context = {
        'folder': folder,
        'form': form,
        'folder_name': folder_name
    }
    return render(request, 'DMS/create_document.html', context)


def checkin_document(request, folder_id, document_id):
    folder = get_object_or_404(Folder, pk=folder_id)
    documentid = Document.objects.get(pk=document_id)
    folder_name = Folder.objects.all()
    documents = Document.objects.all()
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES, instance=documentid)
        if form.is_valid():
            document = form.save(commit=False)
            document.save()
            return HttpResponseRedirect('/DMS/' + folder_id)
        else:
            form = DocumentForm(initial={'name': documentid.name,
                                         'type': documentid.type,
                                         'owner': documentid.owner,
                                         'keywords': documentid.keywords,
                                         'description': documentid.description}, instance=documentid)
    context = {
        'folder': folder,
        'form': form,
        'folder_name': folder_name
    }
    return render(request, 'DMS/create_document.html', context)


def create_folder(request):
    form = FolderForm(request.POST or None, request.FILES or None)
    folder_name = Folder.objects.all()
    if form.is_valid():
        folder = form.save(commit=False)
        folder.save()

        return HttpResponseRedirect('/DMS/index')
    context = {
        "form": form,
        "folder_name": folder_name
    }

    return render(request, 'DMS/create_folder.html', context)


def delete_document(request, folder_id, document_id):
    folder = get_object_or_404(Folder, pk=folder_id)
    folder_name = Folder.objects.all()
    document = Document.objects.get(pk=document_id)
    document.delete()
    context = {
        "folder": folder,
        "folder_name": folder_name
    }
    # return render(request, 'DMS/folder-details.html', context)
    return HttpResponseRedirect("http://127.0.0.1:8000/DMS/"+folder_id)


def delete_folder(request, id_folder):
    folder = Folder.objects.get(pk=id_folder)
    folder_name = Folder.objects.all()
    if folder_name.filter(root=folder.name).exists():
        folder_name.filter(root=folder.name).delete()
        folder_name.filter(id=folder.id).delete()
    else:
        folder_name.filter(id=folder.id).delete()
    context = {
        'folder': folder,
        'folder_name': folder_name
    }
    return render(request, 'DMS/folder-details.html', context)


class DocumentViewSet(RevisionMixin, viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly)


class RevisionFormView(RevisionMixin, FormView):
    pass


@receiver(post_save, sender=CustomUser)
def send_user_data_when_created_by_admin(sender, instance, **kwargs):
    first_name = instance.first_name
    last_name = instance.last_name
    email = instance.email
    html_content = "Hello, your account has been created! <br> Now, you can log into the application following this " \
                   "link:" + " \n http://127.0.0.1:8000/DMS/login/" + "\n <p> For authentification, " \
                                                                      "please, use your current " \
                                                                      "email: %s. </p> <p> Your " \
                                                                      "current password is " \
                                                                      "monitor123, please reset " \
                                                                      "it </p>"
    message = EmailMessage(subject='Welcome, %s %s' % (first_name, last_name), body=html_content % (email), to=[email])
    message.content_subtype = 'html'
    message.send()
