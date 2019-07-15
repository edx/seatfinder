# seatfinder

An application for serving searchable floor plan data to assist in finding seats/rooms.

# Getting started (Mac)

## Create a checkout of seatfinder and set up basics

Run the following commands from Terminal:

```
git clone _________ seatfinder
cd seatfinder
virtualenv ve --python="python3"
. ve/bin/activate
pip install -r requirements.txt
./manage.py migrate
```

## Create a check of drawio-batch

`drawio-batch` is a [now deprecated] package for converting drawio xml to numerous different formats. It does exactly what we need it to (as of July 2019) for conversion to images, so no shame for now.

From any directory you will remember, make a checkout of drawio-batch:

```
git clone git@github.com:languitar/drawio-batch.git
```

In your seatfinder checkout, locate seatfinder/settings.py.

Update the value of XML_TO_IMG_SCRIPT_LOCATION (in seatfinder/settings.py) to the absolute path to the drawio-batch.js file in your drawio-batch checkout. By default it is set to `/put_an_absolute_path_here/drawio-batch/drawio-batch.js'`

Your django app will now know where the javascript file required for converted XML to a PNG image lives.

## Create your floor plan

1) Create a floor plan in https://www.draw.io/
2) Include text in the shape of the desks (this is what will be searchable)
3) Export floor plan by doing the following:
  1) Select File -> Export as -> XML
  2) Deselect "Compressed"
  3) Select Export
  4) Select the media in which to save
    - Note: for getting started with the app, select "Device", and then move the XML file to the `floor_plans/` subdirectory in your seatfinder checkout


## Ingest XML data into your database

To ingest the XML floor plan data into your database, you can run the `import_floor_plan_data` management command, which will attempt to parse and import data for all XML files in the `floor_plans/` subdirectory of your seatfinder checkout.

Run the following command:

```
./manage.py import_floor_plan_data
```

You should see a success message like the following if the ingestion was successful:

```
Successfully saved FloorPlan for floor_8.xml from file "~/seatfinder/floor_plans/test_floor.xml"
```

## Using Your App to Find Someone or Something

Run your application:

```
./manage.py runserver
```

In your browser, navigate to `http://127.0.0.1:8000/find_a_seat/`

In the textbox, search for `superman`.

You should see an imagine returned with superman's desk highlighted red.
