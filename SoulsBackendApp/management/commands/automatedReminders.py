import sched
import time as tm
from datetime import datetime

import pytz
import schedule
from django.core.management.base import BaseCommand
from django.utils import timezone

from SoulsBackendApp.models import SmallGroup
from SoulsBackendApp.oauth.views import GenerateOauthCodeTesting
from SoulsBackendApp.serializers import UserResponseSerializer


class Command(BaseCommand):
    help = "Send leaders email reminder at the group meeting time weekly"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("scheduling daily task..."))

        # Schedule the job to run every day at 00:05 AM
        # s = (
        #     schedule.every()
        #     .day.at("00:05", pytz.timezone("America/Chicago"))
        #     .do(self.send_weekly_attendance_recording_reminder)
        # )
        s = schedule.every().hour.at("30:00").do(self.lighter_reminder_sender)
        # self.lighter_reminder_sender()
        print(datetime.now())
        # s = schedule.every(2).minutes.do(self.send_weekly_attendance_recording_reminder)

        while True:
            print(datetime.now(), repr(s))
            schedule.run_pending()
            tm.sleep(600)

    def lighter_reminder_sender(self):
        self.stdout.write(
            self.style.SUCCESS("Running the lighter email sending function...")
        )
        """
        get the local time in american central time, assuming the most users of the application in the beginning
        will be located in the midwest.
        """
        central_timezone = pytz.timezone("America/Chicago")
        current_time_central = timezone.localtime(
            timezone.now(), timezone=central_timezone
        )
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
            for group in small_groups:
                group_meet_time = datetime.combine(
                    current_time_central.date(), group.meet_time
                )  # group meet-time combined with current date
                localized_group_meet_time = central_timezone.localize(
                    group_meet_time
                )  # group meet-time and date localized to central time
                group_meet_time_in_server_timezone = timezone.localtime(
                    localized_group_meet_time,
                    timezone=timezone.get_current_timezone(),
                )  # group meet_time converted into server local time.
                if group_meet_time_in_server_timezone.hour == datetime.now().hour:
                    GenerateOauthCodeTesting(UserResponseSerializer(group.leader).data)
                self.stdout.write(
                    self.style.SUCCESS("email sent to group-leader successfully.")
                )
        self.stdout.write(
            self.style.SUCCESS("auto-email sending function ran successfully.")
        )

    def send_weekly_attendance_recording_reminder(self):
        self.stdout.write(self.style.SUCCESS("Running the email sending function..."))
        """
        get the local time in american central time, assuming the most users of the application in the beginning
        will be located in the midwest.
        """
        central_timezone = pytz.timezone("America/Chicago")
        current_time_central = timezone.localtime(
            timezone.now(), timezone=central_timezone
        )
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
        # small_groups = SmallGroup.objects.filter(is_deleted=False, meet_day=day_of_week)
        small_groups = SmallGroup.objects.filter(is_deleted=False)
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
                        localized_group_meet_time,
                        timezone=timezone.get_current_timezone(),
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
        self.stdout.write(self.style.SUCCESS("email send function ran successfully."))


# change this functionality to only use schedule, and eliminate the need for sched. schedule would run every hour
# 1.if group is meeting today, then continue
# 2. check if it's meeting hour is equal to the current hour
# 3. if it is send, if not, ignore.
