from celery import shared_task

from .email_service import EmailService
from .models import Questions, Audience
from .utils import AnalyzeQuestions, ExportCsv, DeleteObjectsOnRefresh


@shared_task
def data_analyzer():
    questions_data = [question.question for question in Questions.objects.all()]
    audience = Audience.objects.last()

    if audience and not audience.process_completed:
        audience.process_completed = True
        audience.save()
        analyzer = AnalyzeQuestions().analyze_report(questions_data, audience)
        csv_report = ExportCsv().csv_export(audience)
        send_email = EmailService().send_email_with_attachment(recipient_email=audience.email,
                                                               attachment_content=csv_report,
                                                               attachment_filename="export_file.csv",
                                                               attachment_content_type="text/csv")
        DeleteObjectsOnRefresh().delete_instances()
