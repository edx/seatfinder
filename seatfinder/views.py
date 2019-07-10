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
            name = form.cleaned_data.get('name').lower()
            floor_plan_with_name = None
            # TODO - allow for duplicate names
            for fp in FloorPlan.objects.all():
                if name in fp.indexed_names:
                    floor_plan_with_name = fp
                    break

            if not floor_plan_with_name:
                data = {
                'form': form,
                'submitted': True,
                'found': False
                }
                return render(request, 'name.html', data)

            # Update the xml with new styles
            updated_xml = update_element_style_found_with_value(fp.floor_data, name)

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

    element = root.find('.//mxCell[@value="{}"]'.format(search_string))
    # if you update an element you update the tree in place!
    # remove fillcolor, then add it, cause we don't know if there will be a fill color present
    element.attrib['style'] = re.sub(r'(fillColor=)(.*?);', '', element.attrib['style'])
    element.attrib['style'] += 'fillColor=#FF0000;'
    
    return etree.tostring(root)
