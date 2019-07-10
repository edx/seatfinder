from lxml import etree
import os
import re

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from seatfinder.models import FloorPlan


class Command(BaseCommand):
    help = 'Import XML floor plan data from text file and put it into DB'

    def handle(self, *args, **options):
        for filename in os.listdir(settings.FLOOR_PLANS_DIRECTORY):
            full_filepath = os.path.join(settings.FLOOR_PLANS_DIRECTORY, filename)
            with open(full_filepath, 'r') as fh:
                floor_data = fh.read()

            floor_name, _ = os.path.splitext(filename)
            plan, _ = FloorPlan.objects.get_or_create(
                floor_name=floor_name,
            )

            # Because we're lowering the case of names everywhere,
            # we actually need to do it to the xml that we save too            

            root = etree.fromstring(re.sub(r'<\?xml version="1.0" encoding="UTF-8"\?>', '', floor_data))
            name_values = []
            for element in root.findall('.//mxCell'):
                if 'value' in element.attrib:
                    element.attrib['value'] = element.attrib['value'].lower()
                    element.attrib['value'] = re.sub('<br>', ' ', element.attrib['value'])
                    element.attrib['value'] = re.sub('<span(.*?)</span>', '', element.attrib['value'])
                    element.attrib['value'] = ' '.join(element.attrib['value'].split())
                    # add to indexed_name if there is some truthy value in element.attrib['value']
                    if element.attrib['value']:
                        name_values.append(element.attrib['value'])
            plan.floor_data = etree.tostring(root).decode('UTF-8')
            plan.file_with_data = full_filepath
            plan.indexed_names = name_values
            plan.save()

            self.stdout.write(self.style.SUCCESS('Successfully saved FloorPlan for %s from file "%s"' % (filename, full_filepath)))
            