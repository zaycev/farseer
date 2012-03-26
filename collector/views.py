# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from bundle import get_bundles
from agent import Agency, MailBox
from collector.superv import RiverFetchingSupervisor
from collector.superv import LinkXSpotter
from collector.models import DataSet
from collections import OrderedDict
import json
import time

import urllib2
request = urllib2.Request("")


Agency()
mb = MailBox("@morbo")
supervisors = [
	RiverFetchingSupervisor(Agency.alloc_address(mb)),
	LinkXSpotter(Agency.alloc_address(mb)),
]
services = OrderedDict([(sup.address, sup) for sup in supervisors])

def apps(request):

	import re
	regex = re.compile('^HTTP_')
	headers = dict((regex.sub('', header), value) for (header, value)
		in request.META.items() if header.startswith('HTTP_'))
	print "\n\n"
	for k in headers:
		print k, headers[k]
	print "\n\n"
	return redirect("/apps/collector/service/%s" % services.values()[0].address)

def show_service(request, address):
	if address not in services:
		return redirect("/apps/collector/service/%s" % services.values()[0].address)
	service_states = OrderedDict([(serv.address, serv.call("__get_full_state__", (), mb))
						for serv in services.itervalues()])
	datasets = DataSet.objects.all()
	bundles = get_bundles()
	return render_to_response("collector/show_service.html", {
		"services": service_states.itervalues(),
		"bundles": bundles,
		"datasets": datasets,
		"active": service_states[address],
	})

def show_dataset(request, dataset_id):
	service_states = OrderedDict([(serv.address, serv.call("__get_full_state__", (), mb))
		for serv in services.itervalues()])
	datasets = DataSet.objects.all()
	bundles = get_bundles()
	return render_to_response("collector/show_dataset.html", {
		"services": service_states.itervalues(),
		"bundles": bundles,
		"datasets": datasets,
		"active": DataSet.objects.get(id=dataset_id),
	})

def call(request):
	address = request.GET.get("address")
	func = request.GET.get("func")
	params = json.loads(request.GET.get("args"))
	result = mb.call((func, params), address)
	return HttpResponse(result.dumps())