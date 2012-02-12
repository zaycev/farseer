# -*- coding: utf-8 -*-
import collector.core.service
import collector.core.orm

CORE_APPS = {
	"namespace": "sys",
	"apps": [
		collector.core.service.Worker,
		collector.core.orm.SqlWriter,
	],
}