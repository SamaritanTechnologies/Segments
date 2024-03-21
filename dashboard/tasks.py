from celery import shared_task

from .email_service import EmailService
from .models import Questions, Audience
from .utils import AnalyzeQuestions, ExportCsv, DeleteObjectsOnRefresh


@shared_task(name="data_analyzer")
def data_analyzer(setup_id):
    audience = Audience.objects.get(id=setup_id)
    print(audience.prompt, "prompt")
    questions_data = [question.question for question in Questions.objects.filter(audience=audience)]
    print(questions_data, "data question")
    analyzer = AnalyzeQuestions().analyze_report(questions_data, audience)
    csv_report = ExportCsv().csv_export(audience)
    send_email = EmailService().send_email_with_attachment(recipient_email=audience.email,
                                                           attachment_content=csv_report,
                                                           attachment_filename="export_file.csv",
                                                           attachment_content_type="text/csv")
    print(send_email, 'email')
    audience.task.enabled = False
    audience.task.save()
    DeleteObjectsOnRefresh(audience.user).delete_instances()
    # audience.task.delete()
