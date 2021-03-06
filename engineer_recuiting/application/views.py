
from datetime import datetime
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.views.generic import DetailView,FormView,ListView
from django.core.urlresolvers import reverse_lazy


from engineer_recuiting.application.models import Application,ApplicationCreateForm
from engineer_recuiting.department.models import RecruitmentInformation,DepartmentProfile
# Create your views here.

'''

this view is responsible for anything concern about the application.which application means after engineer
submit their application, it will be stored by application form, and the application can be a contract or an history
transaction baesd on the different status

this view includes any operation about application , CRUD....

'''
class AuthRequiredMixin(object):
    " if user didn't login then send it back to login page"
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse_lazy('login'))

        return super(AuthRequiredMixin, self).dispatch(request, *args, **kwargs)

class ApplicationRequiredMixin(object):
    "make sure the user is the owner of the application"

    def dispatch(self, request, *args, **kwargs):
        application=Application.objects.get(id=int(self.kwargs['pk']))

        if self.request.user.id == application.applier.id or \
                        self.request.user.id == application.recruitment.department.id:
            return super(ApplicationRequiredMixin, self).dispatch(request, *args, **kwargs)

        return HttpResponseRedirect('illgal')


class CreateApplicationView(AuthRequiredMixin,FormView):
    form_class = ApplicationCreateForm
    success_url = 'success'
    template_name = 'create_application.html'

    def form_valid(self, form):

        recuitment_id=int(self.args[0])
        recuitment=RecruitmentInformation.objects.get(id=recuitment_id)
        user=User.objects.get(id=self.request.user.id)
        instance=form.save(commit=False)
        instance.recruitment=recuitment
        instance.date=datetime.today()
        instance.applier=user
        instance.save()

        return super(CreateApplicationView, self).form_valid(form)

class ApplicationDetailView(AuthRequiredMixin,ApplicationRequiredMixin,DetailView):
    model = Application
    context_object_name = 'application'
    template_name = 'appliaction_detail.html'

    def get_context_data(self, **kwargs):
        user=User.objects.get(id=self.request.user.id)
        content=super(ApplicationDetailView,self).get_context_data(**kwargs)
        if hasattr(user,'departmentprofile'):
            content['template']='department'
        if hasattr(user,'engineerprofile'):
            content['template']='engineer'
        if hasattr(user,'companyprofile'):
            content['template']='company'
        return content

class AppliactionHistoryView(AuthRequiredMixin,ListView):
    template_name ='history.html'
    model = Application
    context_object_name = 'applications'
    paginate_by = 10
    def get_queryset(self):
        user=User.objects.get(id=self.request.user.id)
        if hasattr(user,'departmentprofile'):
            return Application.objects.filter(recruitment__department=user).filter(status='f')
        if hasattr(user,'engineerprofile'):
            return Application.objects.filter(applier=user).filter(status='f')
        if hasattr(user,'companyprofile'):
            departments=list(DepartmentProfile.objects.filter(company=user))
            application=Application.objects.all()
            for each in departments:
                application.filter(recruitment__status=departments.user)
            return application
    def get_context_data(self, **kwargs):

        context=super(AppliactionHistoryView,self).get_context_data(**kwargs)
        context['range'] = range(context["paginator"].num_pages)
        return context
def applicationStatusChange(application,status):
    application.status=status
    return True



