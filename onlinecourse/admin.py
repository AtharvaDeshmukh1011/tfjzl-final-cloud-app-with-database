from django.contrib import admin

from .models import Choice, Course, Instructor, Learner, Lesson, Question, Submission


class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 2


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    show_change_link = True


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1


class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_text", "lesson", "grade")
    list_filter = ("lesson__course",)
    search_fields = ("question_text",)
    inlines = [ChoiceInline]


class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)
    search_fields = ("title", "content")
    inlines = [QuestionInline]


class CourseAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name", "description")
    inlines = [LessonInline]


admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Choice)
admin.site.register(Submission)
