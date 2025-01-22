from django import forms
from .models import Course, CourseMaterial, Assignment, AssignmentSubmission, Announcement, CourseSchedule, DiscussionTopic, DiscussionReply, ResourceCategory, CourseResource, StudentGroup, GroupProject, VideoMeeting, Quiz

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'start_date', 'end_date']

class MaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ['title', 'description', 'file', 'is_video']

        

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date', 'max_points']

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'due_date', 'max_points']

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['submission_file']

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'is_pinned', 'attachment']

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = CourseSchedule
        fields = ['title', 'start_time', 'end_time', 'is_recurring', 
                 'recurrence_pattern', 'location', 'meeting_link']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class DiscussionForm(forms.ModelForm):
    class Meta:
        model = DiscussionTopic
        fields = ['title', 'content']

class ReplyForm(forms.ModelForm):
    class Meta:
        model = DiscussionReply
        fields = ['content']

class ResourceCategoryForm(forms.ModelForm):
    class Meta:
        model = ResourceCategory
        fields = ['name', 'description']

class ResourceForm(forms.ModelForm):
    class Meta:
        model = CourseResource
        fields = ['title', 'description', 'category', 'file', 'url']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        url = cleaned_data.get('url')
        if not file and not url:
            raise forms.ValidationError('You must provide either a file or a URL.')
        return cleaned_data

class GroupForm(forms.ModelForm):
    class Meta:
        model = StudentGroup
        fields = ['name', 'members']
        widgets = {
            'members': forms.CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.course:
            self.fields['members'].queryset = self.instance.course.students.all()

class ProjectForm(forms.ModelForm):
    class Meta:
        model = GroupProject
        fields = ['title', 'description', 'due_date']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

class VideoMeetingForm(forms.ModelForm):
    class Meta:
        model = VideoMeeting
        fields = ['title', 'scheduled_time', 'duration', 'is_recurring']
        widgets = {
            'scheduled_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        } 