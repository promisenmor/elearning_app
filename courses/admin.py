from django.contrib import admin
from .models import Course, CourseMaterial, Assignment, AssignmentSubmission, Attendance, Quiz, Question, Choice, QuizSubmission, Announcement, CourseSchedule, DiscussionTopic, DiscussionReply, Notification, ResourceCategory, CourseResource, StudentGroup, GroupProject, VideoMeeting, MeetingAttendance

admin.site.register(Course)
admin.site.register(CourseMaterial)
admin.site.register(Assignment)
admin.site.register(AssignmentSubmission)
admin.site.register(Attendance)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(QuizSubmission)