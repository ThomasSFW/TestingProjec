from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render, redirect
from django.urls import reverse

class LoginCheckMiddleWare(MiddlewareMixin):
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        #print(modulename)
        user = request.user

        #Check whether the user is logged in or not
        if user.is_authenticated:
            now = datetime.datetime.now()
            cache.set('seen_%s' % (current_user.username), now, settings.USER_LASTSEEN_TIMEOUT)
            if user.user_type == "1":
                if modulename == "zenPOS_app.HodViews":
                    pass
                elif modulename == "zenPOS_app.views" or modulename == "django.views.static":
                    pass
                else:
                    return redirect("system_tab")
            
            elif user.user_type == "2":
                if modulename == "zenPOS_app.StaffViews":
                    pass
                elif modulename == "zenPOS_app.views" or modulename == "django.views.static":
                    pass
                else:
                    return redirect("staff_home")
            
            elif user.user_type == "3":
                if modulename == "zenPOS_app.StudentViews":
                    pass
                elif modulename == "zenPOS_app.views" or modulename == "django.views.static":
                    pass
                else:
                    return redirect("student_home")

            else:
                return redirect("login")

        else:
            if request.path == reverse("login") or request.path == reverse("doLogin"):
                pass
            else:
                return redirect("login")