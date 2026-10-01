from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import Course, Lesson, Enrollment, Question, Choice, Submission

class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        return Course.objects.order_by('-pub_date')[:10]

class CourseDetailsView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_details_bootstrap.html'

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = Enrollment.objects.get(user=user, course=course)
    
    selected_choice_ids = request.POST.getlist('choice')
    submission = Submission.objects.create(enrollment=enrollment)
    
    for choice_id in selected_choice_ids:
        choice = Choice.objects.get(pk=choice_id)
        submission.choices.add(choice)
        
    return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)

def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    total_score = 0
    total_possible = 0
    
    for question in course.question_set.all():
        total_possible += question.grade
        selected_ids = [c.id for c in submission.choices.all()]
        if question.is_get_score(selected_ids):
            total_score += question.grade
            
    score_percentage = int((total_score / total_possible) * 100) if total_possible > 0 else 0
    
    context['course'] = course
    context['submission'] = submission
    context['grade'] = score_percentage
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
