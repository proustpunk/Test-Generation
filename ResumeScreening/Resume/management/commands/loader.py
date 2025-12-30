from django.core.management.base import BaseCommand
from Resume.models import Question
import json
import os

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        filepath = "Resume/data/test.json"
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data:
            q = Question.objects.create(**item)
            self.stdout.write(f"Created: {q.id}")