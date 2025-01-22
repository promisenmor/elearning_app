from django import template

register = template.Library()

@register.filter
def filter_submission(submissions, assignment):
    """
    Filter submissions to get the submission for a specific assignment
    """
    try:
        return submissions.get(assignment=assignment)
    except:
        return None 