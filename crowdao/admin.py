from django.contrib import admin
from crowdao.models import Order, Reward, Update, Question, Value
from crowdao.forms import AdminOrderForm, AdminRewardForm, AdminUpdateForm
from crowdao.forms import AdminQuestionForm, AdminValueForm

admin.site.register(Order, AdminOrderForm)
admin.site.register(Reward, AdminRewardForm)
admin.site.register(Update, AdminUpdateForm)
admin.site.register(Question, AdminQuestionForm)
admin.site.register(Value, AdminValueForm)
