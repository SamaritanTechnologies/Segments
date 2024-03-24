from celery import shared_task
from accounts.models import User
from .email_service import EmailService
from .models import Questions, Audience
from .utils import AnalyzeQuestions, ExportCsv, DeleteObjectsOnRefresh


@shared_task
def data_analyzer():
    users = User.objects.all()
    for user in users:
        audience = Audience.objects.filter(user=user).first()
        if audience and not audience.process_completed:
            audience.process_completed = True
            questions_data = [question.question for question in Questions.objects.filter(audience=audience)]
            analyzer = AnalyzeQuestions().analyze_report(questions_data, audience)
            csv_report = ExportCsv().csv_export(audience)
            send_email = EmailService().send_email_with_attachment(recipient_email=audience.email,
                                                                   attachment_content=csv_report,
                                                                   attachment_filename="export_file.csv",
                                                                   attachment_content_type="text/csv")
            print(send_email, 'email')
            audience.save()
            DeleteObjectsOnRefresh(user).delete_instances()
