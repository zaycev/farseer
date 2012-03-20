# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from agent import Agency, MailBox
from collector.superv import RiverFetchingSupervisor

Agency()
mb = MailBox("-1")
services = [
	RiverFetchingSupervisor(Agency.alloc_address(mb))
]

def list_apps(request):
	states = [serv.call("get_state", (), mb) for serv in services]
	print states
	return render_to_response("collector/list_apps.html", {
		"services": states,
	})