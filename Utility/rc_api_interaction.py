
from Utility.networks import *
from Utility.default_data import *
from attendance_app.models import RocketAPIAuthentication
import htmlmin

class APIFunctions:

	def __init__(self, path):
		self.data = ''
		self.rocketPath = 'views/'
		self.path = path

	def build_URL(self, request):
        return request.scheme + "://" + request.get_host() + self.path	

    def format_html(self, response):
        html = response.getvalue().decode('utf-8')
        minified_html_value = htmlmin.minify(html, remove_empty_space = True)
        return minified_html_value            

    def get_users(self, users, admin_username):
        return [user for user in users if user.username != admin_username]

    def get_admin(self, users, admin_username):
        return [user for user in users if user.username = admin_username] 

    def authenticate(self, params):
        source = params.get('source')
        username = RCLoginDataDefault.USERNAME
        password = RCLoginDataDefault.PASSWORD
        api_authentication = RocketAPIAuthentication.objects.getRocketAPIAuth(source)
        rocket_setting = RocketSetting()
        rocket_setting.url = source + RocketSetting.API_PATH
        if (api_authentication):
            if api_authentication.rocket_chat_user_id != None:
                rocket_setting.user_id = api_authentication.rocket_chat_user_id

            if api_authentication.rocket_chat_auth_token != None:
                rocket_setting.auth_token = api_authentication.rocket_chat_auth_token

            if rocket_setting.user_id == None or rocket_setting.auth_token == None:
                rocket_api = RocketUsersAPI(rocket_setting)
                login_result = rocket_api.login(username, password)
                if (login_result.is_sucess()):
                    rocket_setting.user_id = login_result.get_uid()
                    rocket_setting.auth_token = login_result.get_auth_token()
                    api_authentication.set_user_id(login_result.get_uid()) \
                                                            .set_auth_token(login_result.get_auth_token()) \
                                                            .save()
                else :
                    rocket_setting = None
        else:
            rocket_api = RocketUsersAPI(rocket_setting)
            login_result = rocket_api.login(username, password)
            if (login_result.is_success()):
                rocket_setting.user_id = login_result.get_uid()
                rocket_setting.auth_token = login_result.get_auth_token()
                RocketAPIAuthentication.objects.createRocketAPIAuth(source, login_result.get_uid(),
                                                                                                login_result.get_auth_token())
            else :
                rocket_setting = None
        return rocket_setting	

