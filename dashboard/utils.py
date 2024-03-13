from openai import OpenAI
from django.conf import settings
client = OpenAI(api_key=settings.OPENAI_API_KEY)
import csv
from django.http import HttpResponse
from .models import Segment, AnalyzeReport, Questions, Answers, Traits, Audience


class DeleteObjectsOnRefresh:

    def delete_instances(self):
        Questions.objects.all().delete()
        Answers.objects.all().delete()
        AnalyzeReport.objects.all().delete()
        Audience.objects.all().delete()
        Segment.objects.all().delete()
        Traits.objects.all().delete()


class AnalyzeQuestions:

    def analyze_report(self, questions, audience_text):
        segments = Segment.objects.all()
        audience = Audience.objects.create(prompt=audience_text)
        analyze_report_job = None
        for segment in segments:
            for _ in range(segment.sample_size):

                analyze_report_job = AnalyzeReport.objects.create(
                    segment=segment,
                    audience=audience,
                    trait=segment.traits_comma()
                )
                if _ > 0:
                    analyze_report_job.loop = True
                for count, question_text in enumerate(questions, start=0):
                    qa_history = ""
                    generated_answer = ""
                    prompt = f"Audience:{audience.prompt} Past Questions and Answers:{qa_history} Traits: {segment.traits_comma()} Question: {question_text}."
                    try:
                        response = OpenAiAnalyzer().call_openai_api(prompt)
                        generated_answer = response.choices[0].message.content
                        if generated_answer.startswith("Answer:"):
                            # Remove "Answer:" prefix and any leading/trailing whitespace
                            generated_answer = generated_answer[len("Answer:"):].strip()
                    except Exception as e:
                        print(f"Failed to get a response after several retries: {e}")
                    question, _ = Questions.objects.get_or_create(question=question_text, audience=audience)
                    answer = Answers.objects.create(answer=generated_answer)
                    analyze_report_job.question.add(question)
                    analyze_report_job.answer.add(answer)
                    analyze_report_job.save()
        return analyze_report_job, 201


class ExportCsv:
    def csv_export(self, audience):
        qs = AnalyzeReport.objects.filter(audience=audience).prefetch_related(
            'question', 'answer'
        )

        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export_file.csv"'

        all_questions = [q.question for q in Questions.objects.filter(audience=audience)]

        # Prepare the row with separate columns for each question
        row = ['trait', 'count', 'audience'] + all_questions
        writer = csv.writer(response)
        writer.writerow(row)

        for rule in qs:
            answers = [a.answer for a in rule.answer.all()]
            answers += [''] * (len(all_questions) - len(answers))
            writer.writerow([rule.trait, rule.segment.sample_size, rule.audience.prompt] + answers)
        return response

    def feedback_csv(self, audience):
        qs = AnalyzeReport.objects.filter(audience=audience, loop=False).prefetch_related(
            'question', 'answer'
        )

        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export_feedback.csv"'

        all_questions = [q.question for q in Questions.objects.filter(audience=audience)]
        row = ['trait'] + all_questions
        writer = csv.writer(response)
        writer.writerow(row)

        for segment in qs:
            generated_answer = []
            for question in all_questions:
                prompt = f"did the question make sense: {question}"
                openai_response = OpenAiAnalyzer().call_openai_api(prompt)
                generated_answer.append(openai_response.choices[0].message.content)
            writer.writerow([segment.trait] + generated_answer)
            generated_answer = []
        return response


class OpenAiAnalyzer:

    def call_openai_api(self, prompt):
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                }
            ],
            model="gpt-3.5-turbo",
        )
        return chat_completion
