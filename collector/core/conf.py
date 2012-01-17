# -*- coding: utf-8 -*-
import collector.core as core

CORE_APPS = {
	"namespace": "sys",
	"apps": [
		core.Console,
		core.SimpleStore,
		core.Worker,
	    core.TaskBootstraper,
	],
}