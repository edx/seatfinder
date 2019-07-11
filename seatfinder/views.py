import base64
import os
import re
import subprocess
from tempfile import TemporaryDirectory

from lxml import etree

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.conf import settings

from seatfinder.forms import NameForm
from seatfinder.models import FloorPlan

def find_seat(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            search_string = form.cleaned_data.get('name').lower()

            floor_plan_with_names = {}
            # TODO - allow for duplicate names

            #### This is the part that aggregates what floors have
            #### What indexed_names that match
            for fp in FloorPlan.objects.all():
                floor_plan_with_names[fp] = []
                # for name in indexed_names
                # seomthnig... if name.contains('something')
                # this might be terrible, but we don't have a lot of floors
                # so it's fine... for now
                for indexed_name in fp.indexed_names:
                    if search_string in indexed_name:
                        floor_plan_with_names[fp].append(indexed_name)

                # if name in fp.indexed_names:
                #     floor_plan_with_name = fp
                #     break

            #### This part counts how many matches there were
            total_matches = 0
            for fp in floor_plan_with_names:
                total_matches += len(floor_plan_with_names[fp])



            print(floor_plan_with_names)
            if total_matches == 0:
                data = {
                'form': form,
                'submitted': True,
                'found': False,
                'multiple_matches': False,
                }
                return render(request, 'name.html', data)

            # If we have a bunch of matches, bring them to a special
            # page that gives options
            if total_matches > 1:
                # hand the dictionary over the template and let it do the iterating
                data = {
                    'form': form,
                    'submitted': True,
                    'found': True,
                    'multiple_matches': True,
                    'matched_floor_plans': floor_plan_with_names,
                }
                return render(request, 'name.html', data)

            if total_matches == 1:
                # I need a way to now grab the floor plan with the match
                fp = None
                for floor_plan_with_name in floor_plan_with_names:
                    if len(floor_plan_with_names[floor_plan_with_name]) == 1:
                        fp = floor_plan_with_name

            # Update the xml with new styles
            updated_xml = update_element_style_found_with_value(fp.floor_data, search_string)

            # create tempdir
            tempdir = TemporaryDirectory()

            # write updated xml to tempdir
            temp_xml_filepath = os.path.join(tempdir.name, floor_plan_with_name.file_basename)
            with open(temp_xml_filepath, 'wb') as fh:
                fh.write(updated_xml)

            resulting_filepath, _ = os.path.splitext(floor_plan_with_name.file_basename)
            resulting_filepath += '.png' # the png extension is required for the conversion script
            resulting_filepath = os.path.join(
                tempdir.name,
                resulting_filepath
            )
            # convert temp xml to png in tempdir
            bashCommand = '{} {} {}'.format(
                settings.XML_TO_IMG_SCRIPT_LOCATION,
                temp_xml_filepath,
                resulting_filepath
            )
            # read in png data and hand to context
            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()

            with open(resulting_filepath, 'rb') as fh:
                image = base64.b64encode(fh.read()).decode()

            data = {
                'form': form,
                'submitted': True,
                'found': True,
                'xml': updated_xml,
                'image': image,
                'multiple_matches': False,
                'floor_name': floor_plan_with_name.floor_name,
            }
            return render(request, 'name.html', data)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, 'name.html', {'form': form, 'submitted': False,})


def update_element_style_found_with_value(xml_string, search_string):
    """
    Takes a string with xml in it (from draw.io)

    Takes a search string

    Updates the style attribute of the appropriate element

    Returns a string with xml
    """
    root = etree.fromstring(xml_string) # 
    elements = root.xpath(".//mxCell[contains(@value, '{}')]".format(search_string))
    for element in elements:
        # if you update an element you update the tree in place!
        # remove fillcolor, then add it, cause we don't know if there will be a fill color present
        element.attrib['style'] = re.sub(r'(fillColor=)(.*?);', '', element.attrib['style'])
        element.attrib['style'] += 'fillColor=#FF0000;'
    
    return etree.tostring(root)
