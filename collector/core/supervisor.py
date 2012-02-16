# -*- coding: utf-8 -*-
import sys
import time
import logging
import rqueue
from options import BOOTSTRAP

def Namespace(app_forrest):
	ns = dict()
	for tree in app_forrest:
		ns_name = tree.get("namespace")
		apps = tree.get("apps")
		for app in apps:
			fullname = "{0}.{1}".format(ns_name, app.name)
			ns[fullname] = app
		else:
			logging.debug("config parser error")
	return ns

class SysSV:
	def __init__(self, apps, workflow, mode="shell"):
		namespace = Namespace(apps)

		keepers = dict()
		last_queue = None
		workers = []

		for tier in workflow:

			if tier.params["wk"] == "bootstrap":
				task = namespace[BOOTSTRAP[0]](**BOOTSTRAP[1])
				rqueue.flush_db()
				last_queue = rqueue.RQueue("BootStrap")
				last_queue.put(task)
			else:
				wk_path = tier.params["wk"]
				wk_qti = tier.params.get("qti", 1)
				wk_keeper = tier.params.get("keeper", None)
				keeper_queue = None

				worker_cls = namespace[wk_path]
				new_queue = rqueue.RQueue(wk_path)

				if wk_keeper:
					if wk_keeper not in keepers:
						keeper_proc = namespace[wk_keeper]()
						keeper_queue = rqueue.RQueue(wk_keeper)
						keepers[wk_keeper] = keeper_queue
						keeper_proc.mailbox.input_queue = keeper_queue
						keeper_proc.run()
					else:
						keeper_queue = keepers[wk_keeper]

				for i in xrange(0, wk_qti):
					new_worker = worker_cls()
					new_worker.mailbox.input_queue = last_queue
					new_worker.mailbox.output_queues.append(new_queue)
					if wk_keeper and keeper_queue:
						new_worker.mailbox.output_queues.append(keeper_queue)
					workers.append(new_worker)
				last_queue = new_queue

		print "\n\n"

		pipe = ""
		for wkr in workers:
			pipe += wkr.name + " -> "
		pipe += "\\"

		print pipe, "\n\n"

		for wkr in workers:
			wkr.run()

		while True:
			time.sleep(1)