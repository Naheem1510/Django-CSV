from django.db import models

class Student(models.Model):
    roll_number = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100, null=True)


    def __str__(self):
        return f"{self.roll_number} - {self.name}"

class Module(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Mark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    marks_obtained = models.FloatField()
    total_marks = models.FloatField()

    def __str__(self):
        return f"{self.student.name} - {self.module.name}"
