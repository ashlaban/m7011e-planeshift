#!/usr/bin/env python3
from app import db, models
from app.planes import models as plane_models
from app.modules import models as module_models

import uuid

# Add test users
####################################################################
print('Adding users...')
if db.session.query(models.User).filter(models.User.username=='john').first() is None:
	print('User: john')
	u = models.User(username='john', password='pass', email='john@email.com')
	db.session.add(u)
	db.session.commit()

if db.session.query(models.User).filter(models.User.username=='test').first() is None:
	print('User: test')
	u = models.User(username='test', password='test', email='test@test.com')
	db.session.add(u)
	db.session.commit()

# Add test modules
####################################################################
from app.modules import models as module_models
user_john = db.session.query(models.User).filter(models.User.username=='john').first()

if db.session.query(module_models.Module).filter(module_models.Module.name=='TestModule').first() is None:
	module1 = module_models.Module(
		owner   = user_john.id,
		picture = 'iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyJpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMy1jMDExIDY2LjE0NTY2MSwgMjAxMi8wMi8wNi0xNDo1NjoyNyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNiAoV2luZG93cykiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6NjBDQzFGRUI2NzY5MTFFMkE4MjNDMDhCMkMxNkVGMDEiIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6NjBDQzFGRUM2NzY5MTFFMkE4MjNDMDhCMkMxNkVGMDEiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDo2MENDMUZFOTY3NjkxMUUyQTgyM0MwOEIyQzE2RUYwMSIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDo2MENDMUZFQTY3NjkxMUUyQTgyM0MwOEIyQzE2RUYwMSIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/PuZpM2sAAAfYSURBVHja7F2NkZs6EJYz14BSAimBK4FXglOCUwJXAlcCLgGXgEvgSvCVACX4nWekyWYjQCtpJeGgGU18OR+I/bR/3wrpcL/fxd7yad92EeyA7G0HZAdkbzsgT9IeUZZNz7Qdv/rw1aX63H/1csty3qqGPITeqQ4BqBRAnQJpN1nM7SHkRgn9uKI5N/Xd3WQxtVoJ+W7o2mSZfvf4m9Nm5LwBQLRvuC/0JUB075VJ2wHxME/dipApgOjepvAvW3fqjTI1R4Zrn9S1692p04QlmbWPE/TNA1IpG/8wJ0XE+xbKLGaTv6QGRCoQkjpckL80qfOXlIDUuYSkhjHV/xIgMGnLMZu2TT43DwikOwqRf0sy3m/PPuMCaXQ0/8INSK0ephbbbjLWs3ABosPYZiPmiRImN+rZjlsARIK4vhLP2yo2/xKQy3qo8ijs+CTfflPmQ9t2OHsH0GOMZRQWNL+tnA+2xOHhcFhyeq6m6QN9nsDPn+jnK/g8ETRW/1uiCAqaoWLmd5T2GO/bV7/MAWIlZw9A9Iw8KgF9zggX/m5CIEyWAtWCkuDe+vM7uE4BEk3X+87dUxqAkwYgLwqYTxdAXjwt3i/VJ8JsFci/FJYz2dQu6t4FAKC08F8faGZ/WmgtZfI4+xUXDXExAwVTDP+qhNYrgf1UGtsx3GvJhH4i4P7SRuuaEtGpnyI5SttCk/Zh+v90KNplNM4TSc5EQMpMHnIEGgfr7APQyDGncXJVDD/moojITTvyxuBoa2VCzhmM80qICJ3zkGPiWXcDPmwkaE+KXpHlTABEgpBySPiQNn6izcDn9SBhllyAwJukfMiKMDv7RGOtweRlA+QOwtsUTrMkCJkCHpdZ1eZdci4D0mYrttM8q6CitiQuKzXWa4JA5AIAYSMXJXCasUNg7agl0VGvBQBcvUDyYdUQXaz5QNlqjDC3JtISmm+bImr0RYXdbvUSBw2BCViMENg32YsdBlcGH8vq1HH4yf2QIeiQLlIYPMxEoVEA6SKEwF1ATTxGCIPrmXtEAeQOWFwuh1kGTES5w+Bx4foy1ur3k3KYFyZHrsPcEOtuK3UtrjD4jNIC9nqIBLMA1gF+KIENAR9uUtfVPkqiqE4qARcLJOgVgVGq8b6i64aszUwg1Ibt+5ec7UhGT5O1ZDdD2OIW/Wyq548zf4ub9nV6QULD4Ovm/Gk0HwJtc6gQuEeJZ7NQKsU2uzUAJhEoI9CsUBHiWsQZFRDofG8ibDQ0IiAGABoU9ACCDPzdEfmgW+DobbAIqaMDEioExoKCtfEWfRdqToN8WD1zXXidUGGwjcmWsd8xrBRgZ3KF7E9H/gYErIMGaVhQYaJzrgurVQoUiAggyDfP4ONsudJFxHLqeKa4ZtQUZzsiIeNNAkx5izSYqXpG+6gLLdaeObrJgsyqS+JFYWWxT6gN0ZUtIJBFdkluS8u/lSleiy7Uw14dWOB3MFPlCpP6A6x7qpF5c2WuJzAGygKGD+XMw+UzATXk7ljitaE0RpQBmzYVWDJZ48oiDZcokUKuJjFZd8cS71pZFpuockYILYq6TKHpnI+ihsE34veTAtISnHNroVGVIbFbygdM2gb9Sx+ADaayE5LjdQQTlzUXCn634LcgXzXM8FIPn/ETkZnFTNhdit9rffWEqNTPv4B2DQv81yth3AWBv4vKZbnOoNpCk2zLoI1BS0ytFzQObSl5pXBhSU2WTYnXtix7AmHpUm/RtTGQpaV5sQmDXZZBJQdkLQqJsUp9VOBQ+bUlv+a6UDALQLoVXin1GmGXSqXrUtosADGVeCHlMWQMiKmkcPOYSDKXDcxwifesMupQZVmuVinBX9DYheDejYJZQ24omfPhjVKtzy2BtheO18rGZEG7W3oyqylXsFeeZd+kiaGJhPsPhLmd2E6bwNh1xOjyhq11YvgS4YHwK8ivYrvtvMAWBGlcGqIraXqRtASVRO4NLkNPqHfAMMNnoACTjDrB2+Pp1ecj+P+c84+5BLYVv/c0watYsqTfMRDlTBZeBVoMEdOhnwwMQGeoWt5yAMQWCNOrAV3GYHTgecaV79kAww5Ijyp4Nvuz4yyY+jZUrD6AfGkgAIiBGbgB0fT10REIE4G3NgNT7Lzgky91qKCm5SO5N+N3BcKUMNYZ+g3fMf21BSAnIE0ms5FrM5uKAWD24ypOgey/i73mfBUtlF+7xdQQrC1joJmZagcfWBLoAlyr8cr3AmyCWQR4kLmYP2by1wQIlQvvBDzgrqRHT7NTJfAnTQD2wGrH7pRHHrluFwtfMesjJn+u9ZlREHa5Tn0GlXQ0Ab2nkFzAHxz9HokgzeVQsNJhtocwI1zhtvNJPLmd0nYUbguZOZJGlwDC+6yqXI/Ns/UvIUNRH8rGahvxLQOi/UMnaMlaiKSRmoQGPU93CwdLVhb+JRQJCTWutfATwU922NJJn2vFnRCEnw2RyXpA2daOXpULNIwvCdmskIbB/MQzAbJGw7jmDWvFsGgHfm39cGITDdMRScilcjHbkUXPCshcmEzJIUyrDZMdGvlM56njF3Js2Fm85Mi0hGcHxLNpGmZcISFbxIdlcZDlMwICq5VzJOQAwGpFRgdZPjMg0JTBcBaGx9ktVbWV84vYbtNrZR+r69/Enwu7p60+1CHT2f/Ptm+7CHZA9rYDsgOyN8f2vwADAHfzs0AWRfhsAAAAAElFTkSuQmCC',

		name       = 'TestModule',
		short_desc = 'Short description of a module',
		long_desc  = 'This is a test module long description',

		latest_version=None,
	)
	db.session.add(module1)

if db.session.query(module_models.Module).filter(module_models.Module.name=='FakeThing').first() is None:
	module2 = module_models.Module(
		owner   = user_john.id,
		picture = 'iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyJpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMy1jMDExIDY2LjE0NTY2MSwgMjAxMi8wMi8wNi0xNDo1NjoyNyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNiAoV2luZG93cykiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6NjBDQzFGRUI2NzY5MTFFMkE4MjNDMDhCMkMxNkVGMDEiIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6NjBDQzFGRUM2NzY5MTFFMkE4MjNDMDhCMkMxNkVGMDEiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDo2MENDMUZFOTY3NjkxMUUyQTgyM0MwOEIyQzE2RUYwMSIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDo2MENDMUZFQTY3NjkxMUUyQTgyM0MwOEIyQzE2RUYwMSIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/PuZpM2sAAAfYSURBVHja7F2NkZs6EJYz14BSAimBK4FXglOCUwJXAlcCLgGXgEvgSvCVACX4nWekyWYjQCtpJeGgGU18OR+I/bR/3wrpcL/fxd7yad92EeyA7G0HZAdkbzsgT9IeUZZNz7Qdv/rw1aX63H/1csty3qqGPITeqQ4BqBRAnQJpN1nM7SHkRgn9uKI5N/Xd3WQxtVoJ+W7o2mSZfvf4m9Nm5LwBQLRvuC/0JUB075VJ2wHxME/dipApgOjepvAvW3fqjTI1R4Zrn9S1692p04QlmbWPE/TNA1IpG/8wJ0XE+xbKLGaTv6QGRCoQkjpckL80qfOXlIDUuYSkhjHV/xIgMGnLMZu2TT43DwikOwqRf0sy3m/PPuMCaXQ0/8INSK0ephbbbjLWs3ABosPYZiPmiRImN+rZjlsARIK4vhLP2yo2/xKQy3qo8ijs+CTfflPmQ9t2OHsH0GOMZRQWNL+tnA+2xOHhcFhyeq6m6QN9nsDPn+jnK/g8ETRW/1uiCAqaoWLmd5T2GO/bV7/MAWIlZw9A9Iw8KgF9zggX/m5CIEyWAtWCkuDe+vM7uE4BEk3X+87dUxqAkwYgLwqYTxdAXjwt3i/VJ8JsFci/FJYz2dQu6t4FAKC08F8faGZ/WmgtZfI4+xUXDXExAwVTDP+qhNYrgf1UGtsx3GvJhH4i4P7SRuuaEtGpnyI5SttCk/Zh+v90KNplNM4TSc5EQMpMHnIEGgfr7APQyDGncXJVDD/moojITTvyxuBoa2VCzhmM80qICJ3zkGPiWXcDPmwkaE+KXpHlTABEgpBySPiQNn6izcDn9SBhllyAwJukfMiKMDv7RGOtweRlA+QOwtsUTrMkCJkCHpdZ1eZdci4D0mYrttM8q6CitiQuKzXWa4JA5AIAYSMXJXCasUNg7agl0VGvBQBcvUDyYdUQXaz5QNlqjDC3JtISmm+bImr0RYXdbvUSBw2BCViMENg32YsdBlcGH8vq1HH4yf2QIeiQLlIYPMxEoVEA6SKEwF1ATTxGCIPrmXtEAeQOWFwuh1kGTES5w+Bx4foy1ur3k3KYFyZHrsPcEOtuK3UtrjD4jNIC9nqIBLMA1gF+KIENAR9uUtfVPkqiqE4qARcLJOgVgVGq8b6i64aszUwg1Ibt+5ec7UhGT5O1ZDdD2OIW/Wyq548zf4ub9nV6QULD4Ovm/Gk0HwJtc6gQuEeJZ7NQKsU2uzUAJhEoI9CsUBHiWsQZFRDofG8ibDQ0IiAGABoU9ACCDPzdEfmgW+DobbAIqaMDEioExoKCtfEWfRdqToN8WD1zXXidUGGwjcmWsd8xrBRgZ3KF7E9H/gYErIMGaVhQYaJzrgurVQoUiAggyDfP4ONsudJFxHLqeKa4ZtQUZzsiIeNNAkx5izSYqXpG+6gLLdaeObrJgsyqS+JFYWWxT6gN0ZUtIJBFdkluS8u/lSleiy7Uw14dWOB3MFPlCpP6A6x7qpF5c2WuJzAGygKGD+XMw+UzATXk7ljitaE0RpQBmzYVWDJZ48oiDZcokUKuJjFZd8cS71pZFpuockYILYq6TKHpnI+ihsE34veTAtISnHNroVGVIbFbygdM2gb9Sx+ADaayE5LjdQQTlzUXCn634LcgXzXM8FIPn/ETkZnFTNhdit9rffWEqNTPv4B2DQv81yth3AWBv4vKZbnOoNpCk2zLoI1BS0ytFzQObSl5pXBhSU2WTYnXtix7AmHpUm/RtTGQpaV5sQmDXZZBJQdkLQqJsUp9VOBQ+bUlv+a6UDALQLoVXin1GmGXSqXrUtosADGVeCHlMWQMiKmkcPOYSDKXDcxwifesMupQZVmuVinBX9DYheDejYJZQ24omfPhjVKtzy2BtheO18rGZEG7W3oyqylXsFeeZd+kiaGJhPsPhLmd2E6bwNh1xOjyhq11YvgS4YHwK8ivYrvtvMAWBGlcGqIraXqRtASVRO4NLkNPqHfAMMNnoACTjDrB2+Pp1ecj+P+c84+5BLYVv/c0watYsqTfMRDlTBZeBVoMEdOhnwwMQGeoWt5yAMQWCNOrAV3GYHTgecaV79kAww5Ijyp4Nvuz4yyY+jZUrD6AfGkgAIiBGbgB0fT10REIE4G3NgNT7Lzgky91qKCm5SO5N+N3BcKUMNYZ+g3fMf21BSAnIE0ms5FrM5uKAWD24ypOgey/i73mfBUtlF+7xdQQrC1joJmZagcfWBLoAlyr8cr3AmyCWQR4kLmYP2by1wQIlQvvBDzgrqRHT7NTJfAnTQD2wGrH7pRHHrluFwtfMesjJn+u9ZlREHa5Tn0GlXQ0Ab2nkFzAHxz9HokgzeVQsNJhtocwI1zhtvNJPLmd0nYUbguZOZJGlwDC+6yqXI/Ns/UvIUNRH8rGahvxLQOi/UMnaMlaiKSRmoQGPU93CwdLVhb+JRQJCTWutfATwU922NJJn2vFnRCEnw2RyXpA2daOXpULNIwvCdmskIbB/MQzAbJGw7jmDWvFsGgHfm39cGITDdMRScilcjHbkUXPCshcmEzJIUyrDZMdGvlM56njF3Js2Fm85Mi0hGcHxLNpGmZcISFbxIdlcZDlMwICq5VzJOQAwGpFRgdZPjMg0JTBcBaGx9ktVbWV84vYbtNrZR+r69/Enwu7p60+1CHT2f/Ptm+7CHZA9rYDsgOyN8f2vwADAHfzs0AWRfhsAAAAAElFTkSuQmCC',

		name       = 'FakeThing',
		short_desc = 'Lorem ipsum sit amet. Praise be Amun-Ra!',
		long_desc  = 'This is a test module long description',

		latest_version=None,
	)
	db.session.add(module2)

db.session.commit()

# Add test planes
####################################################################
user_john = db.session.query(models.User).filter(models.User.username=='john').first()
test_module = db.session.query(module_models.Module).filter(module_models.Module.name=='TestModule').first()

'''
uid = []
for i in range(3):
	x = uuid.uuid4()
	
	while x in uid:
		x = uuid.uuid4()
	
	uid.append(x)
#debug stuff
for j in uid:
	print j.hex
'''

plane1 = plane_models.Plane(
	owner = user_john.id,
	password = None,
	module = test_module.id,
	name = 'Astral Plane',
	public = True)

plane2 = plane_models.Plane(
	owner = user_john.id,
	password = 'iomedae',
	module = test_module.id,
	name = 'Haven',
	public = False)

plane3 = plane_models.Plane(
	owner = user_john.id,
	password = 'asmodeus',
	module = test_module.id,
	name = 'Hell',
	public = False)

db.session.add(plane1)
db.session.add(plane2)
db.session.add(plane3)
db.session.commit()

