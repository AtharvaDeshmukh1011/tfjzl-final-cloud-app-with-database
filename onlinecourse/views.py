from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Choice, Course, Learner, Question, Submission


def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, "onlinecourse/course_details_bootstrap.html", {"course": course})


@login_required
def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    Learner.objects.get_or_create(user=request.user, course=course)
    return redirect("onlinecourse:course_details", course_id=course.id)


@login_required
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method != "POST":
        return HttpResponseBadRequest("Exam submissions must be POSTed.")

    enrollment, _ = Learner.objects.get_or_create(user=request.user, course=course)

    # Each question's radio/checkbox inputs are named "question_<id>" and hold choice ids.
    selected_ids = []
    for question in Question.objects.filter(course=course):
        selected_ids.extend(int(cid) for cid in request.POST.getlist(f"question_{question.id}"))

    submission = Submission.objects.create(enrollment=enrollment)
    submission.choices.set(Choice.objects.filter(id__in=selected_ids))

    return redirect(
        "onlinecourse:show_exam_result", course_id=course.id, submission_id=submission.id
    )


@login_required
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(
        Submission, pk=submission_id, enrollment__user=request.user, enrollment__course=course
    )

    selected_ids = list(submission.choices.values_list("id", flat=True))
    total_score = 0
    possible_score = 0
    results = []

    for question in Question.objects.filter(course=course).prefetch_related("choice_set"):
        # Only this question's choices count toward its score.
        selected = [c for c in question.choice_set.all() if c.id in selected_ids]
        is_correct = question.is_get_score([c.id for c in selected])
        possible_score += question.grade
        if is_correct:
            total_score += question.grade
        results.append({"question": question, "is_correct": is_correct, "selected": selected})

    percent = round(100 * total_score / possible_score) if possible_score else 0
    passed = percent >= 80

    context = {
        "course": course,
        "submission": submission,
        "results": results,
        "total_score": total_score,
        "possible_score": possible_score,
        "percent": percent,
        "passed": passed,
    }
    return render(request, "onlinecourse/exam_result_bootstrap.html", context)
