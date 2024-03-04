from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)
import csv
from django.http import HttpResponse
from .models import Segment, AnalyzeReport, Audience, Questions, Answers


class AnalyzeQuestions:

    def analyze_report(self, questions):
        segments = Segment.objects.all()
        analyze_report_job = None
        audience = Audience.objects.last()
        for segment in segments:
            for _ in range(segment.sample_size):
                analyze_report_job = AnalyzeReport.objects.create(
                    segment=segment,
                    audience=audience,
                    trait=segment.traits_comma()
                )
                for count, question_text in enumerate(questions, start=0):
                    qa_history = ""
                    generated_answer = ""
                    prompt = f"Past Questions and Answers:{qa_history} Traits: {segment.traits_comma()} Question: {question_text}."
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
        return analyze_report_job


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
            # Split answer_text into a list of individual answers
            answers = [a.answer for a in rule.answer.all()]
            # Make sure answers list has the same length as all_questions
            answers += [''] * (len(all_questions) - len(answers))
            writer.writerow([rule.trait, rule.segment.sample_size, rule.audience.prompt] + answers)

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
