from django.db import models

class AuditLog(models.Model):
    action = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()
    changes = models.JSONField()

    def __str__(self):
        return f"{self.action} on {self.model_name} (ID: {self.object_id}) at {self.timestamp}"

class UserAction(models.Model):
    audit_log = models.ForeignKey(AuditLog, related_name='user_actions', on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
        return self.description
