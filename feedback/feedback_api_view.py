from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError
from django.template import loader, RequestContext
#from .serializers import UserSerializer, GroupSerializer, CreateFormSerializer
from django.contrib.auth.models import User, Group
from .views import *
from Utility.rc_api_interaction import APIFunctions
from Utility.default_data.rocket_data import RCAPI
from Utility.networks import RocketUsersAPI, ActionLinkPrep, ActionLinkBuilder, ActionParameters
from feedback.views import AppController, GeneralView, ActionLinkView
from feedback.models import FeedbackSession, StudentFeedback
from user.default_data.rocket_data import RocketUserData
from feedback.feedback_default_data.feedback_data import FeedbackData
import htmlmin

class FeedbackAPIView(APIFunctions):
    path = '/feedback_app'
    confirm_create_feedback = '/confirm_create_feedback'
    confirm_submit = '/confirm_submit'
    FURTHER_COMMENT = '/further_comment'

    def __init__(self):
        APIFunctions.__init__(self,FeedbackAPIView.path)
        self.app_controller = AppController()
        self.app_view = GeneralView()
        self.act_link_view = ActionLinkView()

    def confirm_create_feedback(self, request):
        params = request.GET
        admin_username = params.get(RocketUserData.USERNAME)
        rocket_setting = self.authenticate(params)
        if rocket_setting:
            rc_api = RocketUsersAPI(rocket_setting)
            response = rc_api.get_users()
            if response.is_success():
                all_acc = response.get_users()
                users = self.get_users_id(all_acc, admin_username)
                admin = self.get_admin_id(all_acc, admin_username)
                to_user_response = self.app_view.confirm_create_feedback(request)
                if to_user_response[0]:
                    feedback_id = to_user_response[0]
                    to_user_html = self.format_html(to_user_response[1])
                    temp_params = params.copy()
                    temp_params.update({RocketUserData.ADMIN_USERNAME: admin_username})
                    temp_params.update({FeedbackData.FEEDBACK_ID: feedback_id, FeedbackData.METHOD: 'get'})
                    temp_params.update({FeedbackData.URL: self.build_URL(request)
                                                                            + FeedbackAPIView.FURTHER_COMMENT})
                    temp_params.update({RCAPI.CLIENT_SERVER: RCAPI.CLIENT_ONLY})

                    act_link_obj = self.act_link_view.prepare_act_link_obj(temp_params)
                    to_user_api_res = rc_api.post_message(text = to_user_html,
                                                                                                    channel = users,
                                                                                                    opt = act_link_obj)
                    temp_params = dict(params)
                    temp_params.update({FeedbackData.FEEDBACK_ID: feedback_id})
                    to_admin_respose = self.app_view.view_feedback(request, temp_params)
                    to_admin_html = self.format_html(to_admin_respose[1])
                    to_admin_api_res = rc_api.post_message(text = to_admin_html,
                                                                                                    channel = admin)
                    if to_admin_api_res.is_success():
                        FeedbackSession.objects.set_message_id(to_user_response[0],
                                                                                                        to_admin_api_res.msg[0]._id)\
                                                                        .set_room_id(to_user_response[0],
                                                                                                        to_admin_api_res.msg[0].rid)

            else:
                print ('Fail to obtain user')
                print(response)
        return HttpResponse('Successful call.')

    @xframe_options_exempt
    def confirm_submit(self, request):
        print('confirm_submit')
        params = request.POST

        feedback_session = FeedbackSession.objects.get_session_by_id(params.get(FeedbackData.FEEDBACK_ID))
        localParams = params.dict()
        localParams.update({'source': feedback_session.source})

        rocket_setting = self.authenticate(localParams)
        if rocket_setting:
	        rc_api = RocketUsersAPI(rocket_setting)
	        submission_attempt = self.app_view.confirm_submit(request)
	        if submission_attempt[0]:
	            choice = localParams.get(FeedbackData.CHOICE)
	            submit_message = 'You chose: ' + choice
	            delete_result = rc_api.delete_message(localParams.get(RocketUserData.CHANNEL), localParams.get(RocketUserData.MESSAGE_ID))
	            post_result = rc_api.post_message(localParams.get(RocketUserData.CHANNEL), submit_message)

	            updated_admin_view = self.app_view.view_feedback(request, params)
	            if updated_admin_view[0]:
	                to_admin_response = self.format_html(updated_admin_view[1])

	                res = rc_api.update_message(updated_admin_view[0].roomid,
	                                                                updated_admin_view[0].messageid,
	                                                                to_admin_response)
	                print('finish update message: ', res)

	        return submission_attempt[1]
