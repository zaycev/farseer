# -*- coding: utf-8 -*-
import collector.service
import collector.orm

CORE_APPS = {
	"namespace": "sys",
	"apps": [
		collector.service.Worker,
		collector.orm.SqlWriter,
	],
}