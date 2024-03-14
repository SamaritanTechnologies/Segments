import csv
import os

import pandas as pd
from django.contrib import messages

from .models import Segment, Traits, Audience, Questions


def in_memory_file_to_temp(in_memory_file):
    is_folder = os.path.isdir('tmp')

    if not is_folder:
        os.makedirs('tmp')

    path = 'tmp/%s' % in_memory_file.name
    product_csv = open(path, 'wb')
    product_csv.write(in_memory_file.read())
    return path


class DataframeUtil(object):
    @staticmethod
    def get_validated_dataframe(path: str) -> pd.DataFrame:
        df = pd.read_csv(path, dtype=str, on_bad_lines='skip', encoding='ISO-8859-1')
        df.columns = df.columns.str.lower()
        df = df.fillna(-1)
        return df.mask(df == -1, None)


ANALYZER_HEADER = ['questions']


def data_scrap(file_path, request):
    dataframe = DataframeUtil.get_validated_dataframe(file_path)
    parser_obj = CSVToJsonParser(dataframe, request)
    headers = parser_obj.get_header()
    if headers:
        return headers, 400
    titles = parser_obj.get_titles()
    if titles:
        return titles, 400
    parser_obj.get_data()
    return True, 201


class CSVToJsonParser:

    def __init__(self, df, request):
        self.request = request
        self.df = df
        self.df.columns = self.df.columns.str.replace('\n', '')
        self.df.columns = self.df.columns.str.strip()
        self.df = self.df.fillna('None')
        self.header = self.df.columns.ravel()
        self.data = self.df.to_dict(orient='records')

    def get_header(self):
        default_header = set(ANALYZER_HEADER)
        difference = default_header.difference(set(self.header))
        if difference:
            return f"please enter the correct header {difference}"

    def get_titles(self):
        product_title = []
        header = ['questions']
        for row, query_obj in enumerate(self.data, 1):
            for data in header:
                if query_obj.get(data) == 'None':
                    product_title.append(f"{data} is missing on row number {row}")
        return product_title

    def get_data(self):
        questions_data = [question['questions'] for question in self.data]
        audience_instance = Audience.objects.first()
        for text in questions_data:
            created = Questions.objects.create(question=text, audience=audience_instance)


class CsvParser:

    def upload_csv(self, file):
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)
        headers = next(reader)
        for row in reader:
            data = dict(zip(headers, row))
            try:
                sample_size = data['sample_size']
            except:
                return "file"
            segment = Segment.objects.create(sample_size=sample_size)
            for key, value in data.items():
                if key != "sample_size" and value != "":
                    Traits.objects.create(title=value, segment=segment)
        return "created"

    def upload_traits(self, request):
        sample_size = request.POST.get("sample_size")
        if sample_size == '':
            messages.error(
                request, message="Please enter sample size"
            )
        traits = request.POST.getlist("traits[]")
        file = request.FILES.get('csvfile')
        if file:
            csv_file = self.upload_csv(file)
            return csv_file
        else:
            segment = Segment.objects.create(sample_size=sample_size)
            for item in traits:
                Traits.objects.create(title=item, segment=segment)

    def update_segment(self, request, segment):
        sample_size = request.POST.get("sample_size")
        if sample_size == '':
            messages.error(
                request, message="Please enter sample size"
            )
        traits = request.POST.getlist("traits[]")
        segment_id = segment.id
        segment.delete()
        segment = Segment.objects.create(id=segment_id, sample_size=sample_size)
        for item in traits:
            Traits.objects.create(title=item, segment=segment)

    def audience_prompt(self, prompt):
        return Audience.objects.create(prompt=prompt)
