# -*- coding: utf-8 -*-
import time
from collector.core.task import ExampleTask
from collector.core.server.service import Service
from collector.core.server.confparser import Namespace
from collector.core.server.confparser import Workflow

# system supervisor
class SysSV:
	def __init__(self, apps, usrconf, mode="shell"):
		
		namespace = Namespace(apps)
		workflow = Workflow(usrconf, namespace)
		services = []
		
		for cons in workflow:
			services.append(cons())
		
		Service.connect(services[0], services[1])
		for i in range(1, len(services) - 1):
			Service.connect(services[i - 1], services[i + 1])
		Service.connect(services[-2], services[-1])
		
		for serv in services:
			serv.run()
		while True:
			time.sleep(1)
			# text = input(">")
			# task = ExampleTask(msg=text)
			# services[0].put(task)