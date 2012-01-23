# -*- coding: utf-8 -*-
import time
import logging
from collector.core.server.service import Service
from collector.core.server.confparser import Namespace
from collector.core.server.confparser import Workflow

class SysSV:
	def __init__(self, apps, usrconf, mode="shell"):
		namespace = Namespace(apps)
		workflow = Workflow(usrconf, namespace)

		print workflow

#		services = []
#		for cons in workflow:
#			logging.debug("start {0}".format(cons.name))
#			services.append(cons())
#		Service.connect(services[0], services[1])
#		for i in xrange(1, len(services) - 1):
#			s1 = services[i]
#			s2 = services[i + 1]
#			Service.connect(s1, s2)
#		for serv in services:
#			serv.run()
#		while True:
#			time.sleep(1)