from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, CreateView

from .forms import WebSignUpForm
from .models import Segment, Audience
from .scrapper import CsvParser, in_memory_file_to_temp, data_scrap
from .utils import ExportCsv, DeleteObjectsOnRefresh


class SignUpView(CreateView):
    form_class = WebSignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


@method_decorator(csrf_exempt, name='dispatch')
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get(self, request, *args, **kwargs):
        DeleteObjectsOnRefresh(request.user).delete_instances()
        return render(request, self.template_name)

    def post(self, request):
        data = dict()
        user = request.user
        prompt = request.POST.get("prompt")
        if prompt:
            return JsonResponse(data={"message": "Prompt created"}, safe=False, status=200)
        else:
            message = CsvParser().upload_traits(request)
            segments = Segment.objects.filter(user=user)
            context = {
                "segment": segments
            }
            data['all_segments'] = render_to_string("dashboard/segments_json.html", context=context)
            data['csv_file'] = message
            return JsonResponse(data, safe=False, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class UpdateSegmentTraitsView(View):

    def get_object(self, *args, **kwargs):
        return Segment.objects.get(id=self.kwargs.get("pk"))

    def post(self, request, *args, **kwargs):
        data = dict()
        message = CsvParser().update_segment(request, self.get_object())
        segments = Segment.objects.filter(user=request.user)
        context = {
            "segment": segments
        }
        data['all_segments'] = render_to_string("dashboard/segments_json.html", context=context)
        return JsonResponse(data, safe=False, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class DeleteSegmentView(View):

    def get(self, request, *args, **kwargs):
        data = dict()
        segment_id = kwargs.get('pk')
        Segment.objects.get(id=segment_id).delete()
        segments = Segment.objects.filter(user=request.user)
        context = {
            "segment": segments
        }
        data['all_segments'] = render_to_string("dashboard/segments_json.html", context=context)
        return JsonResponse(data, safe=False, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class AnalyzeQuestion(View):

    def post(self, request):
        email = request.POST.get("email")
        audience_text = request.POST.get("audience")

        if not email:
            return JsonResponse(data={"error_message": "Please enter your email", "status": 400}, safe=False)
        Audience.objects.get_or_create(user=request.user, email=email, prompt=audience_text)
        file = request.FILES.get('questions')
        file_path = in_memory_file_to_temp(file)
        scrap, status = data_scrap(file_path, request)
        if status == 400:
            return JsonResponse(data={"error_message": scrap, "status": 400}, safe=False)
        return JsonResponse(
            data={"success_message": "Thank you. We will email you your results shortly!", "status": 200},
            safe=False)


class FeedbackView(View):

    def post(self, request):
        audience = Audience.objects.last()
        return ExportCsv().feedback_csv(audience)
