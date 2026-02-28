from app.services import parent_notification_service


def test_notify_parent_student_created_retries_then_succeeds(monkeypatch):
    monkeypatch.setattr(parent_notification_service.settings, "send_parent_email_on_student_create", True)
    monkeypatch.setattr(parent_notification_service.settings, "email_retry_attempts", 2)

    calls = {"count": 0}

    def _flaky_send(**kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("temporary failure")

    monkeypatch.setattr(parent_notification_service, "_send_student_created_email", _flaky_send)

    ok = parent_notification_service.notify_parent_student_created(
        parent_email="parent@example.com",
        student_name="Jon",
        student_id="jon_zhao",
        initial_pin="1234",
    )
    assert ok is True
    assert calls["count"] == 2


def test_notify_parent_student_created_returns_false_after_retries(monkeypatch):
    monkeypatch.setattr(parent_notification_service.settings, "send_parent_email_on_student_create", True)
    monkeypatch.setattr(parent_notification_service.settings, "email_retry_attempts", 2)
    monkeypatch.setattr(
        parent_notification_service,
        "_send_student_created_email",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("smtp down")),
    )

    ok = parent_notification_service.notify_parent_student_created(
        parent_email="parent@example.com",
        student_name="Astrid",
        student_id="astrid_zhao",
        initial_pin="2345",
    )
    assert ok is False
