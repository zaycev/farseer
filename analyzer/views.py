# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
import collector.models as cm

def model_get(request, *args):
	instance_id = request.GET.get("id")
	if instance_id:
		document = cm.Document.objects.get(id=instance_id)
	else:
		document = cm.Document.objects.order_by("?")[0]
	return render_to_response("analyzer/test.html", {
		"document": document,
	})