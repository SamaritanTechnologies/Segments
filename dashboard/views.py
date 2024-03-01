from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, DeleteView
from .models import Segment
from .scrapper import CsvParser


@method_decorator(csrf_exempt, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'dashboard/index.html'

    def get(self, request):
        segment = Segment.objects.all()
        return render(request, self.template_name, context={"segment": segment})

    def post(self, request):
        message = CsvParser().upload_traits(request)
        return redirect('dashboard')


@method_decorator(csrf_exempt, name='dispatch')
class UpdateSegmentTraitsView(View):

    def get_object(self, *args, **kwargs):
        return Segment.objects.get(id=self.kwargs.get("pk"))

    def post(self, request, *args, **kwargs):
        message = CsvParser().update_segment(request, self.get_object())
        return redirect('dashboard')


@method_decorator(csrf_exempt, name='dispatch')
class DeleteSegmentView(DeleteView):
    template_name = 'dashboard/delete_segment.html'
    model = Segment

    def get_success_url(self):
        return reverse('dashboard')
