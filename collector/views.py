# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from bundle import get_bundles
from agent import Agency, MailBox
from collector.superv import RiverFetcher
from collector.superv import LinkSpotter
from collector.superv import PageFetcher
from collector.models import DataSet
from collector.models import RawRiver, RawDocument, ExtractedUrl
from collections import OrderedDict

from django.utils.simplejson import dumps


Agency()
mb = MailBox("@morbo")
supervisors = [
	RiverFetcher(Agency.alloc_address(mb)),
	LinkSpotter(Agency.alloc_address(mb)),
	PageFetcher(Agency.alloc_address(mb)),
]
services = OrderedDict([(sup.address, sup) for sup in supervisors])

def apps(request):
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


def call(request, format):
	if format not in ("xml", "json",):
		return HttpResponseForbidden()
	try:
		address = request.GET.get("address")
		func = request.GET.get("func")
		params = json.loads(request.GET.get("args"))
		result = mb.call((func, params), address)
		return HttpResponse(result.dumps())
	except Exception: return HttpResponseNotFound()


def model_get(request, format):
	model = request.GET.get("model")
	if model not in ("river", "document", "probe"):
		return HttpResponseForbidden("model %s doesn't exist" % model)
	try:
		id = request.GET.get("id", -1)
		if model == "river":
			river = RawRiver.objects.get(id=id)
			obj = {"id": river.id, "body": river.body}
		elif model == "document":
			doc = RawDocument.objects.get(id=id)
			obj = {"id": doc.id, "body": doc.body}
		else:
			return HttpResponseNotFound("model %s doesn't exist" % model)
		if format == "json": return HttpResponse(dumps(obj), content_type="application/json")
		return HttpResponseForbidden("internal error")
	except Exception:
		import traceback
		print traceback.format_exc()
		return HttpResponseNotFound("object %s not found" % model)


def model_list(request, format):
	model = request.GET.get("model")
	if model not in ("eurl",):
		return HttpResponseForbidden("model %s doesn't exist" % model)
	try:
		dataset_id = request.GET.get("dataset", -1)
		ds = DataSet.objects.get(id=dataset_id)
		if model == "eurl":
			objs = ExtractedUrl.objects.filter(dataset=ds)\
				.order_by("?").values("id","url")[0:32]
		else:
			return HttpResponseNotFound("model %s doesn't exist" % model)
		if format == "json": return HttpResponse(dumps(list(objs)), content_type="application/json")
		return HttpResponseForbidden("internal error")
	except Exception:
		import traceback
		print traceback.format_exc()
		return HttpResponseNotFound("object %s not found" % model)