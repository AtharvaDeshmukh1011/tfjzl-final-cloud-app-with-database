from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from onlinecourse.models import Choice, Course, Instructor, Lesson, Question


class Command(BaseCommand):
    help = "Load a sample course with lessons and a mock exam."

    def handle(self, *args, **options):
        User = get_user_model()
        instructor_user, _ = User.objects.get_or_create(
            username="instructor", defaults={"first_name": "Ada", "last_name": "Lovelace"}
        )
        instructor, _ = Instructor.objects.get_or_create(user=instructor_user, defaults={"bio": "Python educator."})

        course, created = Course.objects.get_or_create(
            name="Introduction to Django",
            defaults={"description": "Build web applications with Django, from models to templates."},
        )
        course.instructors.add(instructor)
        if not created:
            self.stdout.write("Demo course already exists; nothing to add.")
            return

        lesson1 = Lesson.objects.create(course=course, title="Models and the ORM", order=1,
                                        content="Define data with model classes and query with the ORM.")
        lesson2 = Lesson.objects.create(course=course, title="Views, URLs and Templates", order=2,
                                        content="Route requests to views and render Django templates.")

        self._question(lesson1, "Which field type stores a true/false value?", 2, [
            ("BooleanField", True), ("CharField", False), ("IntegerField", False),
        ])
        self._question(lesson1, "Which command creates database migrations?", 2, [
            ("makemigrations", True), ("migrate", False), ("runserver", False),
        ])
        self._question(lesson2, "Which template tag loops over a list?", 3, [
            ("{% for %}", True), ("{% if %}", False), ("{% url %}", False),
        ])
        self._question(lesson2, "Which of these are valid HTTP methods? (select all that apply)", 3, [
            ("GET", True), ("POST", True), ("FETCH", False),
        ])

        self.stdout.write(self.style.SUCCESS(f"Loaded demo course with id {course.id}."))

    def _question(self, lesson, text, grade, choices):
        question = Question.objects.create(lesson=lesson, question_text=text, grade=grade)
        for text, is_correct in choices:
            Choice.objects.create(question=question, choice_text=text, is_correct=is_correct)
