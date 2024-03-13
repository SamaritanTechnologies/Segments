from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from .email_service import Multiprocess
from .models import Segment, Audience
from .scrapper import CsvParser, in_memory_file_to_temp, data_scrap

from .utils import ExportCsv


@method_decorator(csrf_exempt, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'dashboard/index.html'

    def get(self, request):
        segment = Segment.objects.all()
        segment.delete()
        return render(request, self.template_name)

    def post(self, request):
        data = dict()
        prompt = request.POST.get("prompt")
        if prompt:
            CsvParser().audience_prompt(prompt)
            return JsonResponse(data={"message": "Prompt created"}, safe=False, status=200)
        else:
            message = CsvParser().upload_traits(request)
            segments = Segment.objects.all()
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
        segments = Segment.objects.all()
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
        segments = Segment.objects.all()
        context = {
            "segment": segments
        }
        data['all_segments'] = render_to_string("dashboard/segments_json.html", context=context)
        return JsonResponse(data, safe=False, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class AnalyzeQuestion(View):

    def post(self, request):
        email = request.POST.get("email")
        audience = request.POST.get("audience")
        if not email:
            return JsonResponse(data={"error_message": "Please enter your email", "status": 400}, safe=False)
        file = request.FILES.get('questions')
        file_path = in_memory_file_to_temp(file)
        scrap, status = data_scrap(file_path, request, audience)
        if status == 400:
            return JsonResponse(data={"error_message": scrap, "status": 400}, safe=False)
        csv_report = ExportCsv().csv_export(scrap.audience)
        Multiprocess().process_to_send_emails(email=email, attachment_content=csv_report,
                                              attachment_filename="export_file.csv",
                                              attachment_content_type="text/csv")
        return JsonResponse(
            data={"success_message": "Thank you. We will email you your results shortly!", "status": 200},
            safe=False)


class FeedbackView(View):

    def post(self, request):
        audience = Audience.objects.last()
        return ExportCsv().feedback_csv(audience)
