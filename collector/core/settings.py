# -*- coding: utf-8 -*-
import collector.core as core

CORE_APPS = {
	"namespace": "sys",
	"apps": [
		("console", core.Console),
		("store", core.SimpleStore),
		("workers", core.Worker),
	],
}