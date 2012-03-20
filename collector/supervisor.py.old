# -*- coding: utf-8 -*-
import time
import logging
from collector import rqueue
from options import BOOTSTRAP

def NamespaceTree(app_forrest):
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

class CollectorSupervisor:

	def __init__(self, imported_apps, workflow):
		"""
		Initializes workers in the order described in
		workflow, establishes connections (via queues)
		between them and start worker threads/processes.
		"""

		# step 1
		# initialize workers in the order
		# which they were put into workflow
		nm_tree = NamespaceTree(imported_apps)
		worker_pools = []
		for handler in workflow:
			wk_class = nm_tree[handler.params["wk"]]
			wk_pool_size = handler.params.get("size", 1)
			worker_pools.append({
				"class": wk_class,
				"units": [wk_class() for _ in xrange(0, wk_pool_size)],
				"persistent": handler.params.get("persistent", None),
			})
		logging.debug("done - workers initialization")


		# step 2
		# establish connections (Redis queues)
		# and init bootstrap queue
		qpool = rqueue.QConnPool()
		bq = qpool.allocate_queue()
		logging.debug("done - connections pre initialization")


		# step 3
		# assign connections to workers
		last_quque = bq
		persistents = {}
		# use a counter to check if the last pool
		# and do not create an output queue for it
		pools_counter = 1
		for pool in worker_pools:
			new_queue = qpool.allocate_queue()
			for unit in pool["units"]:
				unit.mailbox.input_queue = last_quque
				if pools_counter != len(worker_pools):
					unit.mailbox.output_queues.append(new_queue)
				# if worker requires persistent store
				# create or get one and add it to
				# the worker as an output queue
				pst_class_name = pool["persistent"]
				if pst_class_name is not None:
					if pst_class_name not in persistents:
						ps_store_class = nm_tree[pst_class_name]
						ps_store = ps_store_class()
						persistents[pst_class_name] = ps_store
						persistents[pst_class_name].mailbox.input_queue = qpool.allocate_queue()
					else:
						ps_store = persistents[pst_class_name]
					# append persistent store's input queue
					# unit's list of output queues
					unit.mailbox.output_queues.append(ps_store.mailbox.input_queue)
			last_quque = new_queue
			pools_counter += 1
		logging.debug("done - connections assigning")


		# step 4
		# run workers and persistent stores
		for pool in worker_pools:
			for unit in pool["units"]:
				unit.run()
		for k in persistents.keys():
			persistents[k].run()
		logging.debug("done - workers activation")


		# step 5
		# bootstraping
		qpool.initialize()
		logging.debug("done - redis connection establishing")
		qpool.flush_db()
		bq_task_class = nm_tree[BOOTSTRAP[0]]
		bq_task_params = BOOTSTRAP[1]
		bq_task = bq_task_class(**bq_task_params)
		bq = bq()
		bq.put(bq_task)
		logging.debug("done - bootstrapping")


		while True:
			time.sleep(1)