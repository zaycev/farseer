# -*- coding: utf-8 -*-import sysimport timeimport datetimeimport threadingimport multiprocessingimport Queue as queueclass ServModel(object):	PROCCESS = 0	THREAD = 1class Service(object):	srv_model = ServModel.THREAD	name = u"nova_object"	datastore = True	def __init__(self, **kwargs):		self.meta = self.__class__.Meta(self, **kwargs)		self.mailbox = self.__class__.Mailbox(self, **kwargs)		if self.datastore:			self.meta.pipe_end, self.mailbox.pipe_end \				 = multiprocessing.Pipe()			self.meta.pipe_end.send(self.mailbox.magick)			def __unicode__(self):		return self.name	def __str__(self):		return self.name		def run(self):		if self.srv_model == ServModel.PROCCESS:			self.unit = multiprocessing.Process(				name=self.name,				target=lambda: self.__class__.target(self, self.mailbox)			)		elif self.srv_model == ServModel.THREAD:			self.unit = threading.Thread(				name=self.name,				target=lambda: self.__class__.target(self, self.mailbox)			)		else:			sys.stderr.write(				u"{0} - wrong srv_model value. {1}"\				.format(self.name, sys.exc_info()))			sys.exit(1)			self.unit.daemon = True		self.__before_start__(self.mailbox)		self.unit.start()			class Meta(object):		timeout = 1		def __init__(self, owner, **kwargs):			self.pipe_end = None			self.owner = owner	class Mailbox(object):		magick = 0xFA1E5C		timeout = 1		def __init__(self, owner, **kwargs):			self.pipe_end = None			self.input = None			self.output = None			self.owner = owner		@staticmethod			def connect(service_1, service_2):		service_1.mailbox.output = service_2		service_2.mailbox.input = service_1		def put(self, task, q_name=None):		q_name = q_name if q_name else 0		self.meta.pipe_end.send((task, q_name))		def pop(self, q_name=None):		q_name = q_name if q_name else 0		query = (q_name,)		self.meta.pipe_end.send(query)		if self.meta.pipe_end.poll(self.meta.timeout):			data = self.meta.pipe_end.recv()			# print("call put, pipe is not empty, response - {0}".format(data))			return data		# print("call put, pipe is empty")		return None		@staticmethod	def target(self, mailbox):		pipe_end = mailbox.pipe_end		magick = pipe_end.recv()		if magick != mailbox.magick:			sys.stderr.write(				u"the magick is broken: {0} != {1}\n"				.format(magick, mailbox.magick))			sys.exit(1)		while True:			if pipe_end.poll(mailbox.timeout):				try:					query = pipe_end.recv()					# print("query received {0}".format(query))					self.__target__(query, mailbox)				except Exception:					sys.stderr.write(					u"{0} {1} loop error. {2}".format(								self.__class__,								mailbox.__class__,								sys.exc_info()))						def __target__(self, query, **kwargs):		raise NotImplementedError()	def __before_start__(self, mailbox, **kwargs):		passclass Console(Service):	name = u"console"	format_put = u"> put (({0})) to {1}"	format_pop = u"> <- pop (({0}))"	def __target__(self, query, *args):		if len(query) == 2:			# print("console ok")			task, q_name = query			print(self.format_put.format(task, q_name))		elif len(query) == 1:			q_name = query[0]			print(self.format_pop.format(q_name))		else:			sys.stderr.write(			u"{0} query error. {0}".format(self.name, sys.exc_info()))class SimpleStore(Service):	name = u"store"	srv_model = ServModel.PROCCESS		class Mailbox(Service.Mailbox):		def __init__(self, owner, **kwargs):			super(SimpleStore.Mailbox, self).__init__(owner, **kwargs)			self.qs = {0: queue.Queue()}			if u"tasks" in kwargs:				for t in kwargs["tasks"]:					self.qs[0].put(t)		def list(self, q_name=0):		elist = []		q = self.mailbox.qs[q_name]		while not q.empty():			e = q.get()			# print(e)			elist.append(e)		while len(elist) > 0:			q.put(elist.pop())		# print("\n")		def __target__(self, query, mailbox):		# print("receive query - {0}".format(query))		# put		if len(query) == 2:			task, q_name = query			if q_name in mailbox.qs:				mailbox.qs[q_name].put(task)			else:				mailbox.qs[q_name] = queue.Queue()				mailbox.qs[q_name].put(task)		# pop		elif len(query) == 1:			# print("len == 1")			q_name = query[0]						# print("check if it's in mailbox")			if q_name in mailbox.qs:				# print("ok, in mailbox, check if q is empty")				if mailbox.qs[q_name].empty():					# print("yep, it is empty")					# print("call __target__/put q is emtpy")					mailbox.pipe_end.send(None)				else:					# print("not, try extract task")					task = mailbox.qs[q_name].get()					# print("call __target__/put - send {0}".format(task))					mailbox.pipe_end.send(task)			else:				# print("no")				# print("call __target__/put - q_name not found")				mailbox.pipe_end.send(None)		else:			sys.stderr.write(			u"{0} query error. {1}".format(self.name, sys.exc_info()))class TaskBootstraper(SimpleStore):	name = u"tasks"	class Mailbox(Service.Mailbox):		def __init__(self, owner, **kwargs):			super(TaskBootstraper.Mailbox, self).__init__(owner, **kwargs)			self.qs = {0: queue.Queue()}			from settings import SYS_TASKS			for t in SYS_TASKS:				self.qs[0].put(t)class Worker(Service):	name = "worker"	srv_model = ServModel.THREAD	target_wait_timeout = 3	@staticmethod	def target(self, mailbox):		inp = mailbox.input		otp = mailbox.output		dt = datetime.datetime.now()		result = None		task_received = False		task = None		while True:			try:				task_received = False				result = None				task = inp.pop()				# inp.list()				# print("worker get {0}".format(task))				if not task:					timeout = self.target_wait_timeout#					print "{0} {1} say: no more tasks found ... sleep for {2} secs"\#						.format(dt, name, timeout)					time.sleep(timeout)				else:					task_received = True#					print "try apply target func"					result = self.__target__(task, mailbox=mailbox)#					print "ok, get result"#					print result#					print "try send result"					for new_task in result:						if new_task.is_correct():							otp.put(new_task)							print "{0} {1} say: processed 1 task ..."\								.format(dt.strftime("%d.%m.%y %H:%M"), self.name)						else:							# TODO(vladimir@zvm.me):put error into a log							pass				# print("\n\n")			except Exception:				sys.stderr.write(				u"{0} {1} main loop error in because {2}\n"\					.format(dt, self.name, sys.exc_info()))				try:					if task_received and\					   (not result or not result.is_correct()):						inp.put(task)						time.sleep(self.target_wait_timeout)				except:					sys.stderr.write(					u"{0} {1} main loop error while try put task back. {2}\n"\						.format(dt, self.name, sys.exc_info()))		def __target__(self, task, **kwargs):		return [task]