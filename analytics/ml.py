# -*- coding: utf-8 -*-

import numpy as np
import analytics.models as am
import transformer.models as tm
from datetime import datetime
from sklearn import linear_model
from sklearn.ensemble import ExtraTreesClassifier
from scikits.learn import svm


tokens = {t.id:t for t in tm.Token.objects.all()}
token_ind = {token.ind:token for token in tokens.itervalues()}
samples = am.Sample.objects\
		.filter(published__gte=datetime(2011, 9, 1))\
		.filter(published__lte=datetime(2011, 10, 31))\
		.order_by("-day_id")



X_all = [s.to_feature_vector(tokens) for s in samples]
Y_all = [s.twits for s in samples]
DB_size = samples.count()
X_train = X_all[:DB_size / 3 * 2]
X_tests = X_all[DB_size / 3 * 2:DB_size]
Y_train = Y_all[:DB_size / 3 * 2]
Y_tests = Y_all[DB_size / 3 * 2:DB_size]


clf = ExtraTreesClassifier(n_estimators=35, max_depth=None, min_samples_split=1, random_state=0, compute_importances=True)

# clf = svm.SVC(kernel='rbf', gamma=0.001)

# clf = linear_model.LogisticRegression(penalty='l2')


# clf.fit(X_train, Y_train)


# Y_preds = clf.predict(X_train)


from sklearn import cross_validation

k_fold = cross_validation.KFold(len(X_all), k=10)
cross_validation.cross_val_score(clf, X_all, Y_all, cv=k_fold, n_jobs=-1)





# plot_data = zip(Y_train, Y_preds)
# plot_data.sort(key=lambda x:x[0])




# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.mlab as mlab
# import matplotlib.cbook as cbook
# import matplotlib.ticker as ticker
# from datetime import datetime
# from analytics.models import Sample
# from collections import OrderedDict
# 
# plot_data_0 = [x[0] for x in plot_data]
# plot_data_1 = [x[1] for x in plot_data]
# 
# N = len(plot_data)
# ind = np.arange(N)
# 
# fig = plt.figure()
# 
# 
# ax_1 = fig.add_subplot(111)
# ax_1.grid(True)
# ax_1.plot(ind, plot_data_0, ".")
# ax_1.plot(ind, plot_data_1, ".")
# 
# plt.show()





# alphas = np.logspace(-4, -1, 6)
# regr = linear_model.Lasso()
# scores = [regr.set_params(alpha=alpha)\
# 			.fit(X_train, Y_train )\
# 			.score(X_tests, Y_tests)
# 			for alpha in alphas]
# 
# 
# 
# 
# 
# 
# best_alpha = alphas[scores.index(max(scores))]
# regr.alpha = best_alpha
# regr.fit(X_all, Y_all)
# 
# 
# def feature_map(lasso_model, min_coef=0.001):
# 	coefs = lasso_model.coef_
# 	for i in xrange(len(coefs)):
# 		if abs(coefs[i]) >= min_coef:
# 			yield i
# 
# l = list(regr.coef_)
# z = 0
# for i in range(len(l) - 5):
#   if abs(l[i]) >= 0.0001:
#     print token_ind[i], l[i]
#     z += 1
# 
# for i in xrange(0, len(tests_y)):
#   print regr.predict(tests_x[i]), tests_y[i]



# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.mlab as mlab
# import matplotlib.cbook as cbook
# import matplotlib.ticker as ticker
# from datetime import datetime
# from analytics.models import Sample
# from collections import OrderedDict
# 
# pred_y = regr.predict(tests_x)
# 
# ind = np.arange(len(pred_y))
# 
# fig = plt.figure()
# 
# all_test = [s.twits for s in samples.order_by("-twits")]
# 
# ax_1 = fig.add_subplot(111)
# ax_1.grid(True)
# ax_1.plot(ind, test_y, ".")
# ax_1.plot(ind, pred_y, ".")
# 
# plt.show()