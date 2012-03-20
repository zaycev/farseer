# -*- coding: utf-8 -*-

from supervisor import AbsSupervisor
from collector.workers import RiverFetherAgent

class RiverFetchingSupervisor(AbsSupervisor):

	def __init__(self, aid):
		super(RiverFetchingSupervisor, self).__init__(aid, RiverFetherAgent)

	def initialize(self):
		super(RiverFetchingSupervisor, self).initialize()

	def __default_params__(self):
		return dict(
			pool_size = 32,
			source_id = None,
			start_page = 3,
			page_count = 128,
		)

	def __get_state__(self):
		return [
		]