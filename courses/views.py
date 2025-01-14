from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, CourseMaterial, Assignment, AssignmentSubmission, Attendance, Quiz, Choice, QuizSubmission, Announcement, CourseSchedule, DiscussionTopic, DiscussionReply, Notification, ResourceCategory, CourseResource, StudentGroup, GroupProject, VideoMeeting, MeetingAttendance
from .forms import CourseForm, MaterialForm, AssignmentForm, SubmissionForm, AnnouncementForm, ScheduleForm, DiscussionForm, ReplyForm, ResourceForm, ResourceCategoryForm, GroupForm, ProjectForm, VideoMeetingForm
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Q
import uuid
from django.utils.timezone import now
from django.http import JsonResponse
import json
from datetime import timedelta
from django.urls import reverse


@login_required
def course_list(request):
    if request.user.is_instructor:
        courses = Course.objects.filter(instructor=request.user)
    else:
        courses = Course.objects.filter(students=request.user)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filtering
    status = request.GET.get('status')
    if status == 'active':
        courses = courses.filter(end_date__gte=timezone.now())
    elif status == 'completed':
        courses = courses.filter(end_date__lt=timezone.now())
    
    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'search_query': search_query,
        'status': status
    })

@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    is_enrolled = request.user in course.students.all()
    is_instructor = request.user == course.instructor
    
    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'is_instructor': is_instructor,
        'materials': course.materials.all(),
        'assignments': course.assignments.all(),
        'quizzes': course.quizzes.all(),
    }
    return render(request, 'courses/course_detail.html', context)

@login_required
def upload_material(request, course_id):
    if not request.user.is_instructor:
        return redirect('course_list')
    
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.save()
            messages.success(request, 'Material uploaded successfully!')
            return redirect('course_detail', pk=course_id)
    else:
        form = MaterialForm()
    
    return render(request, 'courses/upload_material.html', {'form': form, 'course': course})

@login_required
def mark_attendance(request, course_id):
    if not request.user.is_instructor:
        return redirect('course_list')
    
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        date = request.POST.get('date')
        present_students = request.POST.getlist('students')
        
        for student in course.students.all():
            Attendance.objects.update_or_create(
                course=course,
                student=student,
                date=date,
                defaults={'is_present': str(student.id) in present_students}
            )
        messages.success(request, 'Attendance marked successfully!')
        
    return redirect('course_detail', pk=course_id)

@login_required
def view_attendance(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.user.is_instructor:
        attendances = course.attendance.all()
    else:
        attendances = course.attendance.filter(student=request.user)
    
    return render(request, 'courses/view_attendance.html', {
        'course': course,
        'attendances': attendances
    })

@login_required
def create_course(request):
    if not request.user.is_instructor:
        return redirect('course_list')
    
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, 'Course created successfully!')
            return redirect('course_detail', pk=course.pk)
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {'form': form})

@login_required
def submit_assignment(request, pk):
    if request.user.is_instructor:
        return redirect('course_list')
    
    assignment = get_object_or_404(Assignment, pk=pk)
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()
            messages.success(request, 'Assignment submitted successfully!')
            return redirect('course_detail', pk=assignment.course.pk)
    else:
        form = SubmissionForm()
    
    return render(request, 'courses/assignment_submit.html', {
        'form': form,
        'assignment': assignment
    })

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    if request.method == 'POST':
        score = 0
        total_points = 0
        
        for question in quiz.questions.all():
            answer = request.POST.get(f'question_{question.id}')
            if question.question_type == 'mcq':
                if answer and Choice.objects.get(id=answer).is_correct:
                    score += question.points
            elif question.question_type == 'true_false':
                if answer == str(question.correct_answer).lower():
                    score += question.points
            total_points += question.points
        
        submission = QuizSubmission.objects.create(
            quiz=quiz,
            student=request.user,
            score=score,
            completed=True
        )
        return redirect('quiz_results', pk=quiz.id)
    
    return render(request, 'courses/take_quiz.html', {'quiz': quiz})

@login_required
def quiz_results(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    submission = QuizSubmission.objects.filter(
        quiz=quiz,
        student=request.user,
        completed=True
    ).first()
    
    return render(request, 'courses/quiz_results.html', {
        'quiz': quiz,
        'submission': submission
    })

@login_required
def enroll_course(request, pk):
    if request.user.is_instructor:
        messages.error(request, 'Instructors cannot enroll in courses.')
        return redirect('course_list')
    
    course = get_object_or_404(Course, pk=pk)
    if request.user in course.students.all():
        messages.warning(request, 'You are already enrolled in this course.')
    else:
        course.students.add(request.user)
        messages.success(request, f'Successfully enrolled in {course.title}')
    return redirect('course_detail', pk=pk)

@login_required
def unenroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.user in course.students.all():
        course.students.remove(request.user)
        messages.success(request, f'Successfully unenrolled from {course.title}')
    return redirect('course_list')

@login_required
def dashboard(request):
    if request.user.is_instructor:
        courses = Course.objects.filter(instructor=request.user)
        total_students = sum(course.students.count() for course in courses)
        assignments_pending = AssignmentSubmission.objects.filter(
            assignment__course__instructor=request.user,
            grade__isnull=True
        ).count()
        
        context = {
            'courses': courses,
            'total_students': total_students,
            'assignments_pending': assignments_pending,
        }
    else:
        courses = Course.objects.filter(students=request.user)
        assignments_due = Assignment.objects.filter(
            course__in=courses,
            due_date__gte=timezone.now()
        ).order_by('due_date')
        recent_submissions = AssignmentSubmission.objects.filter(
            student=request.user
        ).order_by('-submitted_at')[:5]
        
        context = {
            'courses': courses,
            'assignments_due': assignments_due,
            'recent_submissions': recent_submissions,
        }
    
    return render(request, 'courses/dashboard.html', context)

@login_required
def grade_assignment(request, assignment_id):
    if not request.user.is_instructor:
        return redirect('course_list')
    
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    submissions = AssignmentSubmission.objects.filter(assignment=assignment)
    
    if request.method == 'POST':
        submission_id = request.POST.get('submission_id')
        grade = request.POST.get('grade')
        feedback = request.POST.get('feedback')
        
        submission = get_object_or_404(AssignmentSubmission, pk=submission_id)
        submission.grade = grade
        submission.feedback = feedback
        submission.save()
        messages.success(request, 'Grade submitted successfully!')
        
    return render(request, 'courses/grade_assignments.html', {
        'assignment': assignment,
        'submissions': submissions
    })

@login_required
def student_progress(request, course_id, student_id):
    if not request.user.is_instructor:
        return redirect('course_list')
    
    course = get_object_or_404(Course, pk=course_id)
    student = get_object_or_404(User, pk=student_id)
    
    # Get all assignments and their submissions
    assignments = Assignment.objects.filter(course=course)
    submissions = AssignmentSubmission.objects.filter(
        assignment__course=course,
        student=student
    )
    
    # Get attendance records
    attendance_records = Attendance.objects.filter(
        course=course,
        student=student
    ).order_by('-date')
    
    # Get quiz results
    quiz_results = QuizSubmission.objects.filter(
        quiz__course=course,
        student=student
    )
    
    return render(request, 'courses/student_progress.html', {
        'course': course,
        'student': student,
        'assignments': assignments,
        'submissions': submissions,
        'attendance_records': attendance_records,
        'quiz_results': quiz_results
    })

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'courses/home.html')

@login_required
def announcement_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    announcements = course.announcements.all()
    
    if request.user.is_instructor and request.user == course.instructor:
        can_create = True
    else:
        can_create = False
        
    return render(request, 'courses/announcement_list.html', {
        'course': course,
        'announcements': announcements,
        'can_create': can_create
    })

@login_required
def create_announcement(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if not request.user.is_instructor or request.user != course.instructor:
        return redirect('course_detail', pk=course_id)
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.course = course
            announcement.save()
            
            # Create notifications for all students
            for student in course.students.all():
                Notification.objects.create(
                    user=student,
                    notification_type='announcement',
                    title=f'New Announcement in {course.title}',
                    message=announcement.title,
                    link=f'/courses/{course_id}/announcements/'
                )
            
            messages.success(request, 'Announcement created successfully!')
            return redirect('announcement_list', course_id=course_id)
    else:
        form = AnnouncementForm()
    
    return render(request, 'courses/announcement_form.html', {
        'form': form,
        'course': course
    })

@login_required
def course_schedule(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    schedules = course.schedules.all()
    
    if request.user.is_instructor and request.user == course.instructor:
        if request.method == 'POST':
            form = ScheduleForm(request.POST)
            if form.is_valid():
                schedule = form.save(commit=False)
                schedule.course = course
                schedule.save()
                messages.success(request, 'Schedule created successfully!')
                return redirect('course_schedule', course_id=course_id)
        else:
            form = ScheduleForm()
    else:
        form = None
    
    return render(request, 'courses/course_schedule.html', {
        'course': course,
        'schedules': schedules,
        'form': form
    })

@login_required
def discussion_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    discussions = course.discussion_topics.all()
    
    return render(request, 'courses/discussion_list.html', {
        'course': course,
        'discussions': discussions
    })

@login_required
def create_discussion(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    
    if request.method == 'POST':
        form = DiscussionForm(request.POST)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.course = course
            discussion.created_by = request.user
            discussion.save()
            messages.success(request, 'Discussion topic created successfully!')
            return redirect('discussion_list', course_id=course_id)
    else:
        form = DiscussionForm()
    
    return render(request, 'courses/discussion_form.html', {
        'form': form,
        'course': course
    })

@login_required
def discussion_detail(request, topic_id):
    topic = get_object_or_404(DiscussionTopic, pk=topic_id)
    replies = topic.replies.filter(parent_reply=None)
    
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.topic = topic
            reply.created_by = request.user
            reply.save()
            messages.success(request, 'Reply posted successfully!')
            return redirect('discussion_detail', topic_id=topic_id)
    else:
        form = ReplyForm()
    
    return render(request, 'courses/discussion_detail.html', {
        'topic': topic,
        'replies': replies,
        'form': form
    })

@login_required
def resource_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    categories = course.resource_categories.all()
    return render(request, 'courses/resources.html', {
        'course': course,
        'categories': categories
    })

@login_required
def create_resource(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if not request.user.is_instructor:
        return redirect('course_detail', pk=course_id)
    
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.course = course
            resource.save()
            messages.success(request, 'Resource added successfully!')
            return redirect('resource_list', course_id=course_id)
    else:
        form = ResourceForm()
    
    return render(request, 'courses/resource_form.html', {
        'form': form,
        'course': course
    })

@login_required
def group_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    groups = course.groups.all()
    
    if request.user.is_instructor:
        can_create = True
    else:
        can_create = False
        
    return render(request, 'courses/group_list.html', {
        'course': course,
        'groups': groups,
        'can_create': can_create
    })

@login_required
def create_group(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if not request.user.is_instructor:
        return redirect('course_detail', pk=course_id)
    
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.course = course
            group.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Group created successfully!')
            return redirect('group_list', course_id=course_id)
    else:
        form = GroupForm()
    
    return render(request, 'courses/group_form.html', {
        'form': form,
        'course': course
    })

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'courses/notifications.html', {
        'notifications': notifications
    })

@login_required
def mark_notification_read(request, notification_id):
    if request.method == 'POST':
        notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        messages.success(request, 'Notification marked as read.')
    return redirect('notifications')

@login_required
def video_meetings(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    meetings = course.meetings.filter(scheduled_time__gte=now()).order_by('scheduled_time')
    
    if request.user.is_instructor and request.user == course.instructor:
        can_create = True
    else:
        can_create = False
    
    return render(request, 'courses/video_meetings.html', {
        'course': course,
        'meetings': meetings,
        'can_create': can_create
    })

@login_required
def create_meeting(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if not request.user.is_instructor or request.user != course.instructor:
        return redirect('course_detail', pk=course_id)
    
    if request.method == 'POST':
        form = VideoMeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.course = course
            meeting.created_by = request.user
            meeting.meeting_id = f"{course.id}-{uuid.uuid4().hex[:12]}"
            meeting.save()
            
            # Create notifications for all students
            for student in course.students.all():
                Notification.objects.create(
                    user=student,
                    notification_type='meeting',
                    title=f'New Video Meeting in {course.title}',
                    message=f'A new meeting "{meeting.title}" has been scheduled.',
                    link=f'/courses/{course_id}/meetings/'
                )
            
            messages.success(request, 'Meeting created successfully!')
            return redirect('video_meetings', course_id=course_id)
    else:
        form = VideoMeetingForm()
    
    return render(request, 'courses/meeting_form.html', {
        'form': form,
        'course': course
    })

@login_required
def join_meeting(request, meeting_id):
    meeting = get_object_or_404(VideoMeeting, pk=meeting_id)
    course = meeting.course
    
    if not (request.user.is_instructor and request.user == course.instructor) and \
       not course.students.filter(id=request.user.id).exists():
        messages.error(request, 'You do not have permission to join this meeting.')
        return redirect('course_detail', pk=course.id)
    
    return render(request, 'courses/meeting_room.html', {
        'meeting': meeting
    })

@login_required
def track_attendance(request, meeting_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        meeting = get_object_or_404(VideoMeeting, pk=meeting_id)
        
        if data['action'] == 'join':
            MeetingAttendance.objects.get_or_create(
                meeting=meeting,
                student=request.user,
                defaults={'join_time': timezone.now()}
            )
        elif data['action'] == 'leave':
            attendance = get_object_or_404(
                MeetingAttendance,
                meeting=meeting,
                student=request.user,
                leave_time__isnull=True
            )
            attendance.leave_time = timezone.now()
            attendance.duration = (attendance.leave_time - attendance.join_time).seconds // 60
            attendance.save()
            
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_meeting_attendance(request, meeting_id):
    meeting = get_object_or_404(VideoMeeting, pk=meeting_id)
    if not request.user.is_instructor or request.user != meeting.created_by:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    attendances = meeting.attendances.all()
    data = {
        'attendances': [{
            'student_name': attendance.student.username,
            'join_time': attendance.join_time.strftime('%Y-%m-%d %H:%M'),
            'duration': attendance.duration or 'Still in meeting'
        } for attendance in attendances]
    }
    return JsonResponse(data)

@login_required
def get_meeting_events(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    meetings = course.meetings.all()
    
    events = [{
        'id': meeting.id,
        'title': meeting.title,
        'start': meeting.scheduled_time.isoformat(),
        'end': (meeting.scheduled_time + timedelta(minutes=meeting.duration)).isoformat(),
        'extendedProps': {
            'duration': meeting.duration,
            'host': meeting.created_by.username,
            'formattedTime': meeting.scheduled_time.strftime('%Y-%m-%d %H:%M'),
            'joinUrl': reverse('join_meeting', args=[meeting.id])
        }
    } for meeting in meetings]
    
    return JsonResponse(events, safe=False)

@login_required
def meeting_calendar(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    can_create = request.user.is_instructor and request.user == course.instructor
    
    return render(request, 'courses/meeting_calendar.html', {
        'course': course,
        'can_create': can_create
    }) 