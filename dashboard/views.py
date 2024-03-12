from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, DeleteView
from .models import Segment, Audience
from .scrapper import CsvParser
import pandas as pd

from .utils import AnalyzeQuestions, ExportCsv


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


class AnalyzeQuestion(View):

    def post(self, request):
        questions = request.FILES.get("questions")
        df = pd.read_csv(questions, encoding='ISO-8859-1')
        questions = df['Questions'].tolist()
        created, status = AnalyzeQuestions().analyze_report(questions)
        if status == 400:
            messages.error(request, message="Please provide Audience text.")
            return redirect('dashboard')
        return ExportCsv().csv_export(created.audience)


class FeedbackView(View):

    def post(self, request):
        audience = Audience.objects.last()
        return ExportCsv().feedback_csv(audience)
