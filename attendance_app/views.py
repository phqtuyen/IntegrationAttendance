from django.shortcuts import render
from django.http import HttpResponse,  HttpResponseServerError
from django.template import loader, RequestContext
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from django.http import JsonResponse

from attendance_app.models import UserProfile, Attendance, AttendanceSubmit
from django.utils import timezone
from attendance_app.default_data.rocket_data import RCRole, RCActionLink
from urllib.parse import parse_qs
question_key = 'Question'
#to be update using database
question = "What is 1 + 1"
answer = "2"

class AppControllers:

    def urlToConfirmCreateAttendance(self, request, path):
        params = request.GET
        source = params.get('source')
        username = params.get('username')
        submitURL = request.scheme + "://" + request.get_host() + "/" + AppViews.path \
                + 'confirm_create_attendance?source=' + str(source) + 'username=' + str(username)

        # submitURL = AppViews.path \
        #       + '/confirm_create_attendance?source=' + str(source)
        return submitURL

    def urlToConfirmSubmit(self, request, path):
        params = request.GET
        source = params.get('source')
        submitURL = request.scheme + "://" + request.get_host() + "/" + AppViews.path \
                + 'confirm_submit?source=' + str(source)
        return submitURL

    def get_role(self, st):
        if st is None:
            return RCRole.USER
        if RCRole.ADMIN in st:
            return RCRole.ADMIN
        else:
            return RCRole.USER

    def userProfileFromRequest(self, requestParam):
        print("param to create tempProfile: ", requestParam)
        tempProfile = UserProfile()\
                                        .configID(requestParam.get('username'), requestParam.get('source')) \
                                        .configName(requestParam.get('name'))\
                                        .configEmail(requestParam.get('email'),
                                                                        self.get_role(requestParam.get('role'))) \
                                        .configCreatedOn(None)
        return tempProfile

    def createUserProfileIfNeeded(self, request):
        requestParam = request.GET or request.POST
        print("param provided to create user profile:", requestParam)
        user_prof = self.userProfileFromRequest(requestParam)
        instructor = UserProfile.objects.createUserProfile(user_prof)
        return instructor

    def createAttendanceObject(self, request):
        requestParam = request.GET or request.POST
        username = requestParam.get('username')
        chat_url = requestParam.get('source')
        instructor = UserProfile.objects.hasUserWithRole(username, chat_url, RCRole.ADMIN)
        if (instructor):
            attendanceID = Attendance.objects.createAttendance(instructor, timezone.now())
            return attendanceID
        else:
            return None

    def contextForCreateAttendanceHTML(self, instructor, submitURL):
        context = {"submitURL" : submitURL,
                                "username" : instructor.username,
                                "chat_url" : instructor.chat_url}
        return context

    def contextForConfirmCreateAttendanceHTML(self, question, submitResultURL, attendance_id):
        context = {"question" : question, "submitResultURL" : submitResultURL, "attendance_id" : attendance_id}
        return context

    def verifyAnswer(self, params):
        query_str = params.get(RCActionLink.ACTION_PARAM)
        #print ("query ", query_str)
        if query_str is not None:
            answer_dict = parse_qs(query_str)
            #print('answer ', answer_dict)
            choice = answer_dict.get(RCActionLink.VALUE)[0]
            correct_choice = params.get(RCActionLink.ANSWER)
            #print ('student answer ', choice)
            #print ('correct answer ', correct_choice)
            if choice == correct_choice :
                return True
            else :
                return False

class AppViews:
    path = 'attendance_app/html/'

    def __init__(self):
        self.question = "What is 1 + 1"
        self.answer = "2"
        self.viewPath = "views/"
        self.appControllers = AppControllers()

        self.createAttendancePath = 'create_attendance'
        self.confirmCreateAttendancePath = 'confirm_create_attendance'
        self.confirmSubmitPath = 'confirm_submit'
        self.viewAttendancePath = 'view_attendance'

    @csrf_exempt
    def createAttendance(self, request):
        submitURL = self.appControllers.urlToConfirmCreateAttendance(request, AppViews.path)
        instructor = self.appControllers.createUserProfileIfNeeded(request)
        context = self.appControllers.contextForCreateAttendanceHTML(instructor, submitURL)
        response = HttpResponse(render(request, self.viewPath + "create.html", context))

        return response

    # Create your views here.
    @csrf_exempt
    def confirmCreateAttendance(self, request):
        submitResultURL = self.appControllers.urlToConfirmSubmit(request, AppViews.path)
        attendance_id = self.appControllers.createAttendanceObject(request)

        if (attendance_id):
            context = self.appControllers.contextForConfirmCreateAttendanceHTML(question, submitResultURL, attendance_id)
            #response = HttpResponse(render(request, self.viewPath + "question.html", context))
            #return response
            return render(request, self.viewPath + "question.html", context)
        else:
            #return 'Only Registered instructors are allowed to use this feature.'
            return  HttpResponse('Fail to create attendance.')

    def confirmCreateAttendanceAPI(self, request):
        submitResultURL = self.appControllers.urlToConfirmSubmit(request, AppViews.path)
        attendance_id = self.appControllers.createAttendanceObject(request)

        if (attendance_id):
            context = self.appControllers.contextForConfirmCreateAttendanceHTML(question, submitResultURL, attendance_id)
            #response = HttpResponse(render(request, self.viewPath + "question.html", context))
            #return response
            return (attendance_id ,render(request, self.viewPath + "question.html", context))
        else:
            #return 'Only Registered instructors are allowed to use this feature.'
            return  (attendance_id, HttpResponseServerError('Fail to create attendance.'))

    @csrf_exempt
    def confirmSubmit(self, request):
        context = {}
        requestParam = request.POST or request.GET
        attendance = Attendance.objects.getAttendanceByID(requestParam.get('attendance_id'))
        if ((requestParam.get("confirm_ans") == self.answer) and
                attendance):
            context['confirmResult'] = "Success!"
            tempProfile = self.appControllers.userProfileFromRequest(requestParam)
            submission = AttendanceSubmit.objects.createAttendanceSubmit(attendance = attendance,
                                                                        tempProfile = tempProfile)
        else:
            context['confirmResult'] = "Attendance check fail, please contact the instructor."

        return HttpResponse(render(request, self.viewPath + "confirm.html", context))

    def confirmSubmitAPI(self, request):
        params = request.POST
        #print ()
        attendance = Attendance.objects.getAttendanceByID(params.get('attendance_id'))
        print('inside confirmSubmitAPI, before call userProfileFromRequest')
        tempProfile = self.appControllers.userProfileFromRequest(params)
        print('inside confirmSubmitAPI, after call userProfileFromRequest')
        user_profile = UserProfile.objects.hasUserProfile(username = tempProfile.username,
                                                                                        chat_url = tempProfile.chat_url)

        print('tempProfile username: ', tempProfile.username)
        if user_profile:
            print ('user already exist: ', user_profile.username, ' ', user_profile.name)
            tempProfile = user_profile
        submitted = AttendanceSubmit.objects.student_submitted(submitted_by = tempProfile,
                                                            attendance = attendance)
        #print ('submitted list: ',submitted)
        if not submitted:
            submission = AttendanceSubmit.objects.createAttendanceSubmit(attendance = attendance,
                                                                                                            tempProfile = tempProfile)
            verify_ans = self.appControllers.verifyAnswer(params = params)
            if verify_ans :
                AttendanceSubmit.objects.verify_submission(submitted_by = tempProfile,
                                                                                        attendance = attendance)
                return (True, HttpResponse('Submission success.'))
            else :
                return (False ,HttpResponse('Submission fail, please see the instructor.'))
        else :
            return (False, HttpResponse('You can only make one submission.'))

    def viewAttendance(self,request, params = {}):
        params = params  or request.POST
        context = {}
        attendance = Attendance.objects.getAttendanceByID(params.get('attendance_id'))
        #print (attendance.id)
        if (attendance):
            submissionList = AttendanceSubmit.objects.getSubmissionList(attendance)
            context['submission_list'] = submissionList
            #print(submissionList)
            context['answer'] = params.get('answer')
            print(UserProfile.objects.all())
            print(submissionList)
            return (attendance, HttpResponse(render(request, self.viewPath + "view.html", context)))
        else:
            return (None, HttpResponse("No such attendance."))

    def test_output(self,request):
        ob = test_class()
        return HttpResponse(ob.test_print())

    # print(response.getvalue())
    # return response



# viewsets: create, edit, delete, post, get, list
#1. welcome user to create attendance
#2. create attendance
#3. allow student to check attendance
#4. list all attendances
#5. list all checks of an attendance
#6. http://www.django-rest-framework.org/api-guide/views/

# class APIViews:
#       def __init__(self):
#               self.data = ''

#       @csrf_exempt
#       def createAttendance(self, request):
#               view = AppViews()
#               response = view.createForm(request)
#               html_value = response.getvalue().decode("utf-8")
#               print('hi')
#               return JsonResponse({
#                               'key': 'create_attendance',
#                               'html': response.getvalue().decode("utf-8")
#                       })

#       @csrf_exempt
#       def confirmCreateAttendance(self, request):
#               # TODO: Need to create an attendance in database
#               return JsonResponse({
#                               'key': 'confirm_create_attendance',
#                               'attendance_id': 'NULL'
#                       })

#       @csrf_exempt
#       def confirmSubmit(self, request):
#               # TODO: Need to create an attendance submit in database

#               view = AppViews()
#               response = view.submitResult(request)
#               html_value = response.getvalue().decode("utf-8")

#               return JsonResponse({
#                               'key': 'confirm_submit',
#                               'html': html_value
#                       })

#       @csrf_exempt
#       def viewAttendance(self, request):
#               view = AppViews()
#               response = view.view(request)
#               html_value = response.getvalue().decode("utf-8")

#               return JsonResponse({
#                               'key': 'view_attendance',
#                               'html': html_value
#                       })
