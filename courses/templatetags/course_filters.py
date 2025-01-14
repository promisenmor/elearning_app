from django import template

register = template.Library()

@register.filter
def filter_submission(submissions, assignment):
    return submissions.filter(assignment=assignment).first() 