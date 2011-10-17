# -*- coding: utf-8 -*-
import time
from collector.core.task import ExampleTask
from collector.core.server.service import Service
from collector.core.server.confparser import Namespace
from collector.core.server.confparser import Workflow

# system supervisor
class SysSV:
	def __init__(self, apps, usrconf, mode="shell"):

#		print apps
#		print "\n\n"

		namespace = Namespace(apps)

#		print namespace
#		print "\n\n"

		workflow = Workflow(usrconf, namespace)
		services = []
		
		for cons in workflow:
#			print "cons ... {0}".format(cons.name)
			services.append(cons())

#		print "\n"
		
		Service.connect(services[0], services[1])

		print "{0} -> {1}".format(services[0], services[1])

		for i in xrange(1, len(services) - 1):
			s1 = services[i]
			s2 = services[i + 1]
			Service.connect(s1, s2)
			print "{0} -> {1}".format(s1, s2)

		for serv in services:
#			print "run ... {0}".format(serv.name)
			serv.run()

		while True:
			time.sleep(1)