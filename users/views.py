import datetime
import json
import re

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Group, Permission
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import Q
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import HttpResponse, redirect, render
from django.urls import reverse
from django.utils.encoding import force_text
from django.views.generic.base import View
from django.views.generic.edit import FormView

from borgia.utils import (GroupLateralMenuMixin, GroupPermissionMixin,
                          get_members_group, group_name_display,
                          human_unused_permissions, permission_to_manage_group)
from finances.models import SharedEvent
from settings_data.utils import settings_safe_get
from users.forms import (ManageGroupForm, SelfUserUpdateForm,
                         UserCreationCustomForm, UserSearchForm,
                         UserUpdateForm)
from users.models import User


class UserListView(PermissionRequiredMixin, FormView, GroupLateralMenuMixin):
    """
    List User instances.

    :param kwargs['group_name']: name of the group used.
    :param self.perm_codename: codename of the permission checked.
    """
    permission_required = 'users.view_user'
    form_class = UserSearchForm
    template_name = 'users/user_list.html'
    lm_active = 'lm_user_list'

    search = None
    year = None
    state = None
    headers = {'username': 'asc',
               'last_name': 'asc',
               'surname': 'asc',
               'family': 'asc',
               'campus': 'asc',
               'year': 'asc',
               'balance': 'asc'}
    sort = None

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)

        # Header List
        context['list_header'] = [["username", "Username"], ["last_name", "Nom Prénom"], ["surname", "Bucque"], [
            "family", "Fam's"], ["campus", "Tabagn's"], ["year", "Prom's"], ["balance", "Solde"]]

        try:
            self.sort = self.request.GET['sort']
        except KeyError:
            pass

        if self.sort is not None:
            context['sort'] = self.sort
            if self.headers[self.sort] == "des":
                context['reverse'] = True
                context['user_list'] = self.form_query(
                    User.objects.all().exclude(groups=1).order_by(self.sort).reverse())
                self.headers[self.sort] = "asc"
            else:
                context['user_list'] = self.form_query(
                    User.objects.all().exclude(groups=1).order_by(self.sort))
                self.headers[self.sort] = "des"
        else:
            context['user_list'] = self.form_query(
                User.objects.all().exclude(groups=1))

        return context

    def form_query(self, query):
        if self.search:
            query = query.filter(
                Q(last_name__icontains=self.search)
                | Q(first_name__icontains=self.search)
                | Q(surname__icontains=self.search)
                | Q(username__icontains=self.search)
            )

        if self.year and self.year != 'all':
            query = query.filter(
                year=self.year)

        if self.state and self.state != 'all':
            if self.state == 'negative_balance':
                query = query.filter(balance__lt=0.0, is_active=True)
            elif self.state == 'threshold':
                threshold = settings_safe_get(
                    'BALANCE_THRESHOLD_PURCHASE').get_value()
                query = query.filter(balance__lt=threshold, is_active=True)
            elif self.state == 'unactive':
                query = query.filter(is_active=False)
        else:
            query = query.filter(is_active=True)

        return query

    def form_valid(self, form):
        if form.cleaned_data['search']:
            self.search = form.cleaned_data['search']

        if form.cleaned_data['state']:
            self.state = form.cleaned_data['state']

        if form.cleaned_data['year']:
            self.year = form.cleaned_data['year']

        return self.get(self.request, self.args, self.kwargs)

    def get_initial(self):
        initial = super(UserListView, self).get_initial()
        initial['search'] = self.search
        return initial


class UserCreateView(PermissionRequiredMixin, SuccessMessageMixin, FormView, GroupLateralMenuMixin):
    """
    Create a new user and redirect to the workboard of the group.

    :param kwargs['group_name']: name of the group used.
    :param self.perm_codename: codename of the permission checked.
    """
    permission_required = 'users.add_user'
    form_class = UserCreationCustomForm
    template_name = 'users/create.html'
    lm_active = 'lm_user_create'
    success_url = None

    def form_valid(self, form):
        user = User.objects.create(username=form.cleaned_data['username'],
                                   first_name=form.cleaned_data['first_name'],
                                   last_name=form.cleaned_data['last_name'],
                                   email=form.cleaned_data['email'],
                                   surname=form.cleaned_data['surname'],
                                   family=form.cleaned_data['family'],
                                   campus=form.cleaned_data['campus'],
                                   year=form.cleaned_data['year'])
        user.set_password(form.cleaned_data['password'])
        user.save()

        is_external_member = form.cleaned_data['is_external_member']
        user.groups.add(get_members_group(is_external_member))

        user.save()

        # User object is assigned to self.object (so we can access to it in get_success_url)
        self.object = user

        return super(UserCreateView, self).form_valid(form)

    def get_initial(self):
        initial = super(UserCreateView, self).get_initial()
        initial['campus'] = 'Me'
        initial['year'] = datetime.datetime.now().year - 1
        return initial

    def get_success_message(self, cleaned_data):
        return "L'utilisateur a bien été crée'"

    def get_success_url(self):
        """
        If can retrieve user: go to the user.
        If not, go to the workboard of the group.
        """
        if self.request.user.has_perm('users.view_user'):
            return reverse('url_user_retrieve', kwargs={'pk': self.object.pk})
        else:
            return reverse('url_group_workboard')


class UserRetrieveView(PermissionRequiredMixin, View, GroupLateralMenuMixin):
    """
    Retrieve a User instance.

    :param kwargs['group_name']: name of the group used.
    :param self.perm_codename: codename of the permission checked.
    """
    permission_required = 'users.view_user'
    template_name = 'users/retrieve.html'

    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(pk=self.kwargs['pk'])
            user.forecast_balance()
        except ObjectDoesNotExist:
            raise Http404

        context = self.get_context_data(**kwargs)
        context['user'] = user
        return render(request, self.template_name, context=context)


class UserUpdateView(PermissionRequiredMixin, SuccessMessageMixin, FormView, GroupLateralMenuMixin):
    """
    Update an user and redirect to the workboard of the group.

    :param kwargs['group_name']: name of the group used.
    :param self.perm_codename: codename of the permission checked.
    """
    permission_required = 'users.change_user'
    form_class = UserUpdateForm
    template_name = 'users/update_admin.html'
    model = User
    modified = False

    def get_form_kwargs(self):
        kwargs = super(UserUpdateView, self).get_form_kwargs()
        kwargs['user_modified'] = User.objects.get(pk=self.kwargs['pk'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        context['user_modified'] = User.objects.get(pk=self.kwargs['pk'])
        return context

    def get_initial(self):
        initial = super(UserUpdateView, self).get_initial()
        try:
            user_modified = User.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404
        for k in UserUpdateForm(user_modified=user_modified).fields.keys():
            initial[k] = getattr(user_modified, k)
        return initial

    def form_valid(self, form):
        user_modified = User.objects.get(pk=self.kwargs['pk'])
        for k in form.fields.keys():
            if form.cleaned_data[k] != getattr(user_modified, k):
                self.modified = True
                setattr(user_modified, k, form.cleaned_data[k])
        user_modified.save()

        return super(UserUpdateView, self).form_valid(form)

    def get_success_message(self, cleaned_data):
        return "Les informations ont bien été mises à jour"

    def get_success_url(self):
        return reverse('url_user_retrieve',
                       kwargs={'pk': self.kwargs['pk']})


class UserDeactivateView(PermissionRequiredMixin, View, GroupLateralMenuMixin):
    """
    Deactivate a user and redirect to the workboard of the group.

    :param kwargs['group_name']: name of the group used.
    :param self.perm_codename: codename of the permission checked.
    """
    permission_required = 'users.delete_user'
    template_name = 'users/deactivate.html'
    success_message = "Le compte de %(user)s a bien été "
    error_sharedevent_message = "Veuillez attribuer la gestion des évènements suivants à un autre utilisateur avant de désactiver le compte:"

    def has_permission(self):
        try:
            self.user = User.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404
        if self.user == self.request.user:
            return True
        else:
            perms = self.get_permission_required()
            return self.request.user.has_perms(perms)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['user'] = self.user
        return render(request, 'users/deactivate.html', context=context)

    def post(self, request, *args, **kwargs):
        deactivated = False
        if self.user.is_active is True:
            sharedevents = self.user.manager.filter(done=False)
            if sharedevents.count() > 0:
                for sharedevent in sharedevents:
                    self.error_sharedevent_message += "\n - " + sharedevent.description
                messages.warning(request, self.error_sharedevent_message)
            else:
                deactivated = True
                self.user.is_active = False
                # si c'est un gadz. Special members can't be added to other groups
                if Group.objects.get(pk=5) in self.user.groups.all():
                    self.user.groups.clear()
                    self.user.groups.add(Group.objects.get(pk=5))
                self.user.save()            
        else:
            self.user.is_active = True
        self.user.save()

        if self.user.is_active:
            self.success_message += 'activé'
        else:
            self.success_message += 'désactivé'

        messages.success(request, self.success_message % dict(
            user=self.user,
        ))

        if request.user == self.user and deactivated:
             self.success_url = reverse(
                'url_logout')
        else:           
            self.success_url = reverse(
                'url_user_retrieve',
                kwargs={'group_name': self.group.name,
                        'pk': self.kwargs['pk']})

        return redirect(force_text(self.success_url))


class UserSelfUpdateView(GroupPermissionMixin, SuccessMessageMixin, FormView,
                     GroupLateralMenuMixin):
    template_name = 'users/self_user_update.html'
    form_class = SelfUserUpdateForm
    perm_codename = None

    def get_initial(self):
        initial = super(UserSelfUpdateView, self).get_initial()
        initial['email'] = self.request.user.email
        initial['phone'] = self.request.user.phone
        initial['avatar'] = self.request.user.avatar
        initial['theme'] = self.request.user.theme
        return initial

    def get_form_kwargs(self):
        kwargs = super(UserSelfUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.request.user.email = form.cleaned_data['email']
        self.request.user.phone = form.cleaned_data['phone']
        self.request.user.theme = form.cleaned_data['theme']
        if form.cleaned_data['avatar'] is not False:
            setattr(self.request.user, 'avatar', form.cleaned_data['avatar'])
        else:
            if self.request.user.avatar:
                self.request.user.avatar.delete(True)
        self.request.user.save()
        return super(UserSelfUpdateView, self).form_valid(form)

    def get_success_message(self, cleaned_data):
        return "Vos infos ont bien été mises à jour"


class ManageGroupView(PermissionRequiredMixin, SuccessMessageMixin, FormView,
                      GroupLateralMenuMixin):
    template_name = 'users/group_manage.html'
    success_url = None
    form_class = ManageGroupForm
    perm_codename = None
    group_updated = None
    lm_active = None

    def dispatch(self, request, *args, **kwargs):
        """
        Check permission.

        This function is at some parts redundant with the mixin GroupPermission
        however you cannot set a perm_codename directly, because it depends
        on the group_name directly.

        :raises: Http404 if the group doesn't exist
        :raises: Http404 if the group updated doesn't exist
        :raises: PermissionDenied if the group doesn't have perm

        Save the group_updated in self.
        """
        try:
            self.group = Group.objects.get(name=kwargs['group_name'])
            self.group_updated = Group.objects.get(pk=kwargs['pk'])
            self.lm_active = 'lm_group_manage_' + self.group_updated.name
        except ObjectDoesNotExist:
            raise Http404

        if (permission_to_manage_group(self.group_updated)[0]
                not in self.group.permissions.all()):
            raise PermissionDenied

        return super(ManageGroupView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """
        Add possible members and permissions to kwargs of the form.

        Possible members are all members, except externals members and unactive users.
        Possible permissions are all permissions.
        :note:: For the special case of a shop management, two groups exist:
        group of chiefs and group of associates. If the group of associates is
        managed, possible permissions are only permissions of the chiefs group.
        """
        kwargs = super(ManageGroupView, self).get_form_kwargs()

        if self.group_updated.name.startswith('associates-') is True:
            chiefs_group_name = self.group_updated.name.replace(
                'associates', 'chiefs')
            kwargs['possible_permissions'] = Permission.objects.filter(
                pk__in=[p.pk for p in Group.objects.get(
                    name=chiefs_group_name).permissions.all().exclude(
                    pk=permission_to_manage_group(self.group_updated)[0].pk).exclude(
                    pk__in=human_unused_permissions())]
            )

        else:
            kwargs['possible_permissions'] = Permission.objects.all().exclude(
                pk__in=human_unused_permissions()
            )

        kwargs['possible_members'] = User.objects.filter(is_active=True).exclude(
            groups=Group.objects.get(name='externals'))
        return kwargs

    def get_initial(self):
        initial = super(ManageGroupView, self).get_initial()
        initial['members'] = User.objects.filter(groups=self.group_updated)
        initial['permissions'] = [
            Permission.objects.get(pk=p.pk) for p in self.group_updated.permissions.all()
        ]
        return initial

    def get_context_data(self, **kwargs):
        context = super(ManageGroupView, self).get_context_data(**kwargs)
        context['group_updated_name_display'] = group_name_display(
            self.group_updated)
        return context

    def form_valid(self, form):
        """
        Update permissions and members of the group updated.
        """
        old_members = User.objects.filter(groups=self.group_updated)
        new_members = form.cleaned_data['members']
        old_permissions = self.group_updated.permissions.all()
        new_permissions = form.cleaned_data['permissions']

        # Modification des membres
        for m in old_members:
            if m not in new_members:
                m.groups.remove(self.group_updated)
                m.save()
        for m in new_members:
            if m not in old_members:
                m.groups.add(self.group_updated)
                m.save()

        # Modification des permissions
        for p in old_permissions:
            if p not in new_permissions:
                self.group_updated.permissions.remove(p)
        for p in new_permissions:
            if p not in old_permissions:
                self.group_updated.permissions.add(p)
        self.group_updated.save()

        return super(ManageGroupView, self).form_valid(form)

    def get_success_message(self, cleaned_data):
        return "Le groupe a bien été mis à jour"


def username_from_username_part(request):
    data = []

    try:
        key = request.GET.get('keywords')

        regex = r"^" + re.escape(key) + r"(\W|$)"

        # Fam'ss en entier
        # where_search = User.objects.filter(family=key).exclude(groups=1).order_by('-year')
        where_search = User.objects.exclude(groups=1).filter(
            family__regex=regex, is_active=True).order_by('-year')

        if len(key) > 2:
            if key.isalpha():
                # Nom de famille, début ou entier à partir de 3 caractères
                where_search = where_search | User.objects.filter(
                    last_name__istartswith=key, is_active=True)
                # Prénom, début ou entier à partir de 3 caractères
                where_search = where_search | User.objects.filter(
                    first_name__istartswith=key, is_active=True)
                # Buque, début ou entier à partir de 3 caractères
                where_search = where_search | User.objects.filter(
                    surname__istartswith=key, is_active=True)

                # Suppression des doublons
                where_search = where_search.distinct()

        for e in where_search:
            data.append(e.username)

    except KeyError:
        pass

    return HttpResponse(json.dumps(data))


def balance_from_username(request):

    # Check permissions

    # User is authentified, if not the he can't access the view
    operator = request.user

    # try:
    #     shop_name = request.GET.get('shop_name')
    #     shop = Shop.objects.get(name = shop_name)
    #     module = OperatorSaleModule.objects.get(shop = shop)
    # except KeyError:
    #         raise Http404
    # except ObjectDoesNotExist:
    #     raise Http404

    # If deactivate
    # if module.state is False:
    #     raise Http404

    if operator.has_perm('modules.use_operatorsalemodule'):
        try:
            username = request.GET['username']
            data = str(User.objects.get(username=username).balance)
            return HttpResponse(json.dumps(data))
        except KeyError:
            return HttpResponseBadRequest()
        except ObjectDoesNotExist:
            return HttpResponseBadRequest()

    # If user don't have the permission
    else:
        raise PermissionDenied
