"""This functionality has now been moved to the  management/commands directory to make use of django's
 custom management commands, for better code quality and to make a more performant use of our memory and 
 other resources"""
import sched
import threading
import time as tm
from datetime import datetime

import pytz
import schedule
from django.utils import timezone

from .models import SmallGroup
from .oauth.views import GenerateOauthCodeTesting
from .serializers import UserResponseSerializer

"""this function will be called every day at midnight in the midwest(Central time), and schedule email to be sent to small-group
leaders whose groups are meeting on that day. the email will be sent out to the leader at the exact time their group is
supposed to meet."""


def send_weekly_attendance_recording_reminder():
    print("the automation function was called")
    """
    get the local time in american central time, assuming the most users of the application in the beginning
    will be located in the midwest.
    """
    central_timezone = pytz.timezone("America/Chicago")
    current_time_central = timezone.localtime(timezone.now(), timezone=central_timezone)
    (
        current_central_year,
        current_central_month,
        current_central_day,
    ) = current_time_central.date().timetuple()[:3]
    day_of_week = datetime(  # the current day of the week in central america when the function is executed
        current_central_year, current_central_month, current_central_day
    ).strftime(
        "%A"
    )

    small_groups = SmallGroup.objects.filter(is_deleted=False, meet_day=day_of_week)
    if small_groups:
        email_scheduler = sched.scheduler(tm.time, tm.sleep)
        for group in small_groups:
            if group.meet_day == day_of_week:
                group_meet_time = datetime.combine(
                    current_time_central.date(), group.meet_time
                )  # group meet-time combined with current date
                localized_group_meet_time = central_timezone.localize(
                    group_meet_time
                )  # group meet-time and date localized to central time
                group_meet_time_in_server_timezone = timezone.localtime(
                    localized_group_meet_time, timezone=timezone.get_current_timezone()
                )  # group meet_time converted into server local time.
                function_args = UserResponseSerializer(group.leader).data
                # print(group_meet_time_in_server_timezone.timestamp())
                email_scheduler.enterabs(
                    group_meet_time_in_server_timezone.timestamp(),
                    1,
                    GenerateOauthCodeTesting,
                    (function_args,),
                )  # scheduled-email to be send to group-leader at a time in the server-timezone that corresponds to the group.meet_time in the central time

                # email_scheduler.enterabs(
                #     tm.time() + 10, 1, GenerateOauthCodeTesting, (function_args,)
                # )
                print(email_scheduler.queue)
        email_scheduler.run()


s = (
    schedule.every()
    .day.at("00:05", pytz.timezone("America/Chicago"))
    .do(send_weekly_attendance_recording_reminder)
)
# s = schedule.every(2).minutes.do(send_weekly_attendance_recording_reminder)


# def test(str):
#     print(f"user email is: {str}")


def run_script():
    while True:
        # central_timezone = pytz.timezone("America/Chicago")
        # current_time_central = timezone.localtime(
        #     timezone.now(), timezone=central_timezone
        # )
        # left_hours = 24 - int(current_time_central.hour) - 1
        # left_mins = 60 - int(current_time_central.minute)
        # left_secs = 60 - int(current_time_central.second)
        # sleep_time = (left_hours * 3600) + (left_mins * 60) + left_secs
        print(datetime.now(), repr(s))
        # print(datetime.now(), left_hours)
        # print(datetime.now(), sleep_time)
        schedule.run_pending()
        tm.sleep(3600)


script_thread = threading.Thread(target=run_script)
