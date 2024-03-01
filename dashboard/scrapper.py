import csv

from django.contrib import messages
from django.shortcuts import redirect

from dashboard.models import Segment, Traits


class CsvParser:

    def upload_csv(self, file):
        print(file, 'file')
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)
        headers = next(reader)
        for row in reader:
            data = dict(zip(headers, row))
            sample_size = data['sample_size']
            segment = Segment.objects.create(sample_size=sample_size)
            for key, value in data.items():
                if key != "sample_size" and value != "":
                    Traits.objects.create(title=value, segment=segment)
        return redirect('dashboard')

    def upload_traits(self, request):
        sample_size = request.POST.get("sample_size")
        if sample_size == '':
            messages.error(
                request, message="Please enter sample size"
            )
        traits = request.POST.getlist("traits[]")
        file = request.FILES.get('csvfile')
        if file:
            self.upload_csv(file)
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

