# -*- coding: utf-8 -*-
import time
import logging
import multiprocessing
from settings import BOOTSTRAP


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

		for tier in workflow:

			if tier.params["wk"] == "bootstrap":
				last_queue = multiprocessing.Queue()
				task = namespace[BOOTSTRAP[0]](**BOOTSTRAP[1])
				last_queue.put(task)
			else:
				wk_path = tier.params["wk"]
				wk_qti = tier.params.get("qti", 1)
				wk_keeper = tier.params.get("keeper", None)
				keeper_queue = None

				if wk_keeper:
					if wk_keeper not in keepers:
						keeper_proc = namespace[wk_keeper]()
						keeper_queue = multiprocessing.Queue()
						keepers[wk_keeper] = keeper_queue
						keeper_proc.mailbox.input_queue = keeper_queue
						keeper_proc.run()
					else:
						keeper_queue = keepers[wk_keeper]


				new_queue = multiprocessing.Queue()
				worker_cls = namespace[wk_path]

				for i in xrange(0, wk_qti):
					new_worker = worker_cls()
					new_worker.mailbox.input_queue = last_queue
					new_worker.mailbox.output_queue = new_queue
					if wk_keeper and keeper_queue:
						new_worker.mailbox.keeper = keeper_queue
					new_worker.run()

				last_queue = new_queue

		while True:
			time.sleep(1)