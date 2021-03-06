# -*- coding: utf-8 -*-

from django.db.models import Model
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from bundle import get_bundles
from agent import create_agency, MailBox, Timeout
from collector.superv import RiverFetcher
from collector.superv import LinkSpotter
from collector.superv import PageFetcher
from collector.superv import PageParser
from collector.superv import SocialStat
from collector.models import DataSet
from collector.models import RawRiver, RawDocument, DocumentUrl, Document
from collections import OrderedDict
from supervisor import read_supv_state

from django.utils.simplejson import dumps, loads

agency = create_agency()

mb = MailBox(agency.alloc_address(), latency=Timeout.Latency.EXTRA_LOW)

supervisors = [
	RiverFetcher(agency.alloc_address()),
	LinkSpotter(agency.alloc_address()),
	PageFetcher(agency.alloc_address()),
	PageParser(agency.alloc_address()),
	SocialStat(agency.alloc_address()),
]
services = OrderedDict([(sup.address, sup) for sup in supervisors])

def apps(request):
	return redirect("/apps/collector/service/%s" % services.values()[0].address)

def show_service(request, address):
	if address not in services:
		return redirect("/apps/collector/service/%s" % services.values()[0].address)
	service_states = OrderedDict([(serv.address, read_supv_state(mb, serv),)
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
	service_states = OrderedDict([(serv.address, read_supv_state(mb, serv),)
		for serv in services.itervalues()])
	datasets = DataSet.objects.all()
	bundles = get_bundles()
	return render_to_response("collector/show_dataset.html", {
		"services": service_states.itervalues(),
		"bundles": bundles,
		"datasets": datasets,
		"active": DataSet.objects.get(id=dataset_id),
	})


def service_call(request, format):
	print "ok, call"
	if format not in ("xml", "json",):
		return HttpResponseForbidden()
	try:
		address = request.GET.get("address")
		func = request.GET.get("func")
		params = loads(request.GET.get("args"))
		result = mb.call((func, params), address)
		return HttpResponse(result.dumps())
	except Exception: return HttpResponseNotFound()


def _get_instance(model, id, dataset_id=None, values=None):
	if not issubclass(model, Model):
		raise TypeError("model should be inherited from django.db.models.Model")
	if id == "@":
		ds = DataSet.objects.get(id=dataset_id)
		query = model.objects.filter(dataset=ds).order_by("?")
		if values: return query.values(*values)[0]
		return query[0]
	else:
		if values: return model.objects.values(*values).get(id=id)
		return model.objects.get(id=id)



def model_get(request, format):
	model = request.GET.get("model")
	if model not in ("doc", "river", "rawdoc", "probe"):
		return HttpResponseForbidden("model %s doesn't exist" % model)
	try:
		id = request.GET.get("id", -1)
		dataset_id = request.GET.get("dataset")
		if model == "river":
			obj = _get_instance(RawRiver, id, dataset_id,
								("id", "url", "body",))
		elif model == "rawdoc":
			obj = _get_instance(RawDocument, id, dataset_id,
								("id", "url", "body",))
		elif model == "doc":
			obj = _get_instance(Document, id, dataset_id,
				("id", "url", "title", "summary", "content", "published"))
		else:
			return HttpResponseNotFound("model %s doesn't exist" % model)
		if format == "json": return HttpResponse(dumps(obj),
				content_type="application/json")
		return HttpResponseForbidden("internal error")
	except Exception:
		import traceback
		print  traceback.format_exc()
		return HttpResponseNotFound("object %s not found" % model)


def model_list(request, format):
	model = request.GET.get("model")
	if model not in ("eurl",):
		return HttpResponseForbidden("model %s doesn't exist" % model)
	try:
		dataset_id = request.GET.get("dataset", -1)
		limit = request.GET.get("limit", 100)
		offset = request.GET.get("offset", 0)
		ds = DataSet.objects.get(id=dataset_id)
		if model == "eurl":
			objs = DocumentUrl.objects.filter(dataset=ds)\
				.order_by("?").values("id","url")[offset:(limit + offset)]
		else:
			return HttpResponseNotFound("model %s doesn't exist" % model)
		if format == "json": return HttpResponse(dumps(list(objs)),
				content_type="application/json")
		return HttpResponseForbidden("internal error")
	except Exception:
		import traceback
		print traceback.format_exc()
		return HttpResponseNotFound("object %s not found" % model)