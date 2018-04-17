from django.shortcuts import render
<<<<<<< 2849f78003514c19e21eab4177e9f3a2958b8b4b
from django.shortcuts import render
from django.http import HttpResponse,  HttpResponseServerError
from django.template import loader, RequestContext
#from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from django.http import JsonResponse
from Utility.views import AbstractController
from Utility.networks import ActionLinkPrep, ActionLinkBuilder, ActionParameters
from Utility.default_data import *
from feedback.models import FeedbackSession, StudentFeedback
from django.utils import timezone
from urllib.parse import parse_qs
# Create your views here.


class AppController(AbstractController):
	CHOICE_MAP = {ActionLinkView.HAPPY : 2,
				ActionLinkView.SAD : 0,
				ActionLinkView.NEUTRAL: 1}

	def __init__(self):
		AbstractController.__init__(self)

	def create_feedback_session(self, params):
		admin = self.isAdmin(params)
		if admin:
			feedback_id = FeedbackSession.objects.createAttendance(admin,
																timezone.now())
			return feedback_id
		else:
			return None	

	def aggregate_feedback(self, session_id):
		choice_stat = {}
		choice_stat.update({'total': 
							StudentFeedback.objects.calc_total(session_id)})
		for choice, value in AppController.CHOICE_MAP.items():
			num = StudentFeedback.objects.calc_num_choice(value, session_id)
			choice_stat.update({choice: num})
		return choice_stat
			
	def get_choice(self, params):
		query_str = params.get(RCActionLink.ACTION_PARAM)
		if query_str is not None:
			answer_dict = parse_qs(query_str)
			return answer_dict.get(RCActionLink.VALUE)[0]
		else:
			return None	

class GeneralView:
	path = 'feedback/html'

	def __init__(self):
		self.view_path = "views/"
		self.app_controller = AppController()
		self.create_feedback_path = 'create_feedback'
		self.confirm_create_feedback_path = 'confirm_create_feedback'
		self.confirm_submit_path = 'confirm_submit'
		self.view_feedback_path = 'view_feedback'

	#first call from RC is always GET, I dont know why people want it to be GET
	#ple	
	def confirm_create_feedback(self, request):
		params = request.GET	
		feedback_id = self.app_controller.create_feedback_session(params)
		context = {}
		question = params.get('question')
		if question:
			context.update({'has_question': True, 'question': question})
		if (feedback_id):
            return (feedback_id, render(request, self.view_path + "question.html", context))				
        else:
        	return (None ,render(request, 'Fail to create feedback session.'))

    def further_comments(self, request):



    def view_feedback(self, request, params = {}):
    	params = request.POST.update(params)
    	context = {}
    	session_id = params.get('feedback_id')
    	if session_id:
    		if FeedbackSession.has_session_with_id(FeedbackSession, session_id) 
    			and StudentFeedback.objects.has_submissions(session_id):
    			context.update({'has_submissions': True})
    			choice_stat = self.app_controller.aggregate_feedback(session_id)
    			context.update({'choice_stat': choice_stat})	
    		else:
    			context['has_submissions'] = False
    		return (session_id, render(request, self.view_path + 'view.html', context))			
    	else:
    		print('Invalid feedback session id.')	


class ActionLinkView:
	HAPPY = 'HAPPY'
	NEUTRAL = 'NEUTRAL'
	SAD = 'SAD' 

	def prepare_choice(self, choice)
		return ActionLinkPrep(HAPPY, 'value=' + choice).buildActionLink()

	def prepare_action_links(self):
		answer_links = [self.prepare_choice(ActionLinkView.HAPPY),
						self.prepare_choice(ActionLinkView.NEUTRAL),
						self.prepare_choice(ActionLinkView.SAD)]

		return answer_links

	def wrap_act_params(self, params):
		return {'source': params.get('source'),
				'username': '',
				'admin_username': params.get('username'),
				'feedback_id': params.get('feedback_id')}

	def prepare_action_params(self, params):
		act_params = ActionParameters(params.get('url'), params.get('method'))
		act_params.config_optional(self.wrap_act_params(params))
		return act_params.buildActionParameters()

	def prepare_act_link_obj(self, params):
		act_links = self.prepare_action_links()
		act_params = self.prepare_action_params()
		return ActionLinkBuilder(act_links = act_links,
								act_params = act_params)

						






=======

# Create your views here.
>>>>>>> init feedback app, setup data model and refactor data in attendance