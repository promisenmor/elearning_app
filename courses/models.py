from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings

User = settings.AUTH_USER_MODEL



class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_teaching')
    students = models.ManyToManyField(User, related_name='courses_enrolled', blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class CourseMaterial(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='course_materials/')
    is_video = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    max_points = models.IntegerField(default=100)

    def __str__(self):
        return self.title

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    submission_file = models.FileField(upload_to='assignments/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.username}'s submission for {self.assignment.title}"

class Attendance(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendance')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=False)

    class Meta:
        unique_together = ['course', 'student', 'date'] 

class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    description = models.TextField()
    time_limit = models.IntegerField(help_text="Time limit in minutes")
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    max_points = models.IntegerField(default=100)

    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPES = (
        ('mcq', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
    )
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    points = models.IntegerField(default=1)

    def __str__(self):
        return self.question_text[:50]

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text

class QuizSubmission(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.FloatField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ['quiz', 'student']

    def __str__(self):
        return f"{self.student.username}'s submission for {self.quiz.title}" 

class CourseSchedule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='schedules')
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=50, blank=True)  # weekly, bi-weekly, etc.
    location = models.CharField(max_length=200, blank=True)  # can be physical or virtual
    meeting_link = models.URLField(blank=True)  # for virtual sessions

    class Meta:
        ordering = ['start_time'] 

class Announcement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_pinned = models.BooleanField(default=False)
    attachment = models.FileField(upload_to='announcements/', blank=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at'] 

class DiscussionTopic(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='discussion_topics')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_closed = models.BooleanField(default=False)

class DiscussionReply(models.Model):
    topic = models.ForeignKey(DiscussionTopic, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    parent_reply = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE) 

class StudentGroup(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='groups')
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(User, related_name='group_memberships')
    created_at = models.DateTimeField(auto_now_add=True)

class GroupProject(models.Model):
    group = models.ForeignKey(StudentGroup, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    submission = models.FileField(upload_to='group_projects/', blank=True) 

class ResourceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='resource_categories')
    
    class Meta:
        verbose_name_plural = "Resource Categories"
        
    def __str__(self):
        return self.name

class CourseResource(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(ResourceCategory, on_delete=models.CASCADE, related_name='resources')
    file = models.FileField(upload_to='course_resources/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class CourseProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed_materials = models.ManyToManyField(CourseMaterial)
    completed_assignments = models.ManyToManyField(Assignment)
    completed_quizzes = models.ManyToManyField(Quiz)
    progress_percentage = models.FloatField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)

class Certificate(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    issued_date = models.DateTimeField(auto_now_add=True)
    certificate_number = models.CharField(max_length=50, unique=True)
    is_valid = models.BooleanField(default=True) 

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('announcement', 'Announcement'),
        ('assignment', 'Assignment'),
        ('quiz', 'Quiz'),
        ('grade', 'Grade'),
        ('discussion', 'Discussion'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=200)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] 

class VideoMeeting(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='meetings')
    title = models.CharField(max_length=200)
    meeting_id = models.CharField(max_length=100, unique=True)
    scheduled_time = models.DateTimeField()
    duration = models.IntegerField(help_text="Duration in minutes")
    is_recurring = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.course.title} - {self.title}" 

class VideoMeetingRecording(models.Model):
    meeting = models.ForeignKey(VideoMeeting, on_delete=models.CASCADE, related_name='recordings')
    recording_url = models.URLField()
    duration = models.IntegerField(help_text="Duration in seconds")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Recording of {self.meeting.title}"

class MeetingAttendance(models.Model):
    meeting = models.ForeignKey(VideoMeeting, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    join_time = models.DateTimeField(auto_now_add=True)
    leave_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, help_text="Duration in minutes")
    
    class Meta:
        unique_together = ['meeting', 'student'] 

