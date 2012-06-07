# -*- coding: utf-8 -*-
# from analytics.plots import plot
# plot()

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.cbook as cbook
import matplotlib.ticker as ticker
from datetime import datetime
from analytics.models import Sample
from collections import OrderedDict

samples = Sample.objects.filter(published__gte=datetime(2011, 1, 1)).filter(published__lte=datetime(2011, 12, 31))

plot_data = OrderedDict()
for s in samples:
    sample_id = (s.published.year, s.published.month, s.published.day,)
    
    if sample_id not in plot_data:
        plot_data[sample_id] = {
            "stories": 0,
            "views": 0,
            "twitts": 0,
            "comms": 0,}
    plot_data[sample_id]["stories"] += 1
    plot_data[sample_id]["views"] += s.views if s.views > 0 else 400
    plot_data[sample_id]["twitts"] += s.twits if s.twits > 0 else 0
    plot_data[sample_id]["comms"] += s.comms if s.comms > 0 else 0
    
    



plot_data = plot_data.items()
plot_data.sort(key=lambda x: x[0])



days = [k for k, v in plot_data]
views = np.array([v["views"] for k, v in plot_data])
twitts = np.array([v["twitts"] for k, v in plot_data])
comms = np.array([v["comms"] for k, v in plot_data])
stories = np.array([v["stories"] for k, v in plot_data])


N = len(plot_data)
ind = np.arange(N)

def format_date(x, pos=None):
    thisind = np.clip(int(x+0.5), 0, N-1)
    return "%s-%s-%s" % days[thisind]


fig = plt.figure()

ax_1 = fig.add_subplot(3, 1, 1, title="Total number of stories")
ax_1.grid(True)
ax_1.plot(ind, stories,"-")
ax_1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
ax_1.ylim(0, 3500)

ax_2 = fig.add_subplot(3, 1, 2, title="Total number of page views")
ax_2.grid(True)
ax_2.plot(ind, views, "-")
ax_2.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))

ax_3 = fig.add_subplot(3, 1, 3, title="Total number of retwitts")
ax_3.grid(True)
ax_3.plot(ind, twitts, "-")
ax_3.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))


fig.autofmt_xdate()
plt.show()