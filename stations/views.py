from django.shortcuts import render
from django.shortcuts import render_to_response
from django.core.serializers import serialize

from stations.models import Stations

# Create your views here.

def index(request):
    stations = serialize('geojson', Stations.objects.all(),
          geometry_field='point',
          fields=('label',))
    return render_to_response('index.html', {'stations': stations})