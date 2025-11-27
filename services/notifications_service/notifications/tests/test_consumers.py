"""Tests for NotificationConsumer.generate_notification_content."""

from django.test import SimpleTestCase

from notifications.consumers import NotificationConsumer


class NotificationContentECPTests(SimpleTestCase):
    """Black-box tests using equivalence class partitioning."""

    def setUp(self):
        self.consumer = NotificationConsumer()

    def test_ecp_club_created_with_name(self):
        subject, message = self.consumer.generate_notification_content(
            'club_created', {'name': 'Chess Club'}
        )
        self.assertEqual(subject, 'New Club Created')
        self.assertIn("Chess Club", message)

    def test_ecp_member_added_defaults_role(self):
        subject, message = self.consumer.generate_notification_content(
            'member_added', {'user_name': 'Alex'}
        )
        self.assertEqual(subject, 'New Club Member')
        self.assertIn("Alex has joined the club as a member", message)

    def test_ecp_event_created_missing_name_uses_fallback(self):
        subject, message = self.consumer.generate_notification_content(
            'event_created', {}
        )
        self.assertEqual(subject, 'New Event Created')
        self.assertIn("Unknown Event", message)

    def test_ecp_rsvp_created_uses_user_name(self):
        subject, message = self.consumer.generate_notification_content(
            'rsvp_created', {'user_name': 'Jamie'}
        )
        self.assertEqual(subject, 'Event RSVP')
        self.assertIn("Jamie has RSVP'd for the event.", message)

    def test_ecp_unknown_event_type_uses_default_template(self):
        subject, message = self.consumer.generate_notification_content(
            'unexpected_event', {'id': '123'}
        )
        self.assertEqual(subject, 'System Notification')
        self.assertIn("unexpected_event", message)


class NotificationContentControlFlowTests(SimpleTestCase):
    """White-box tests aimed at control-flow coverage."""

    def setUp(self):
        self.consumer = NotificationConsumer()

    def test_control_flow_club_approved_path(self):
        subject, message = self.consumer.generate_notification_content(
            'club_approved', {'name': 'Robotics Club'}
        )
        self.assertEqual(subject, 'Club Approved!')
        self.assertIn("Robotics Club", message)

    def test_control_flow_member_added_with_role(self):
        subject, message = self.consumer.generate_notification_content(
            'member_added', {'user_name': 'Priya', 'role': 'officer'}
        )
        self.assertEqual(subject, 'New Club Member')
        self.assertIn("Priya has joined the club as a officer", message)

    def test_control_flow_event_and_rsvp_paths(self):
        event_subject, event_message = self.consumer.generate_notification_content(
            'event_created', {'name': 'Hackathon'}
        )
        self.assertEqual(event_subject, 'New Event Created')
        self.assertIn("Hackathon", event_message)

        rsvp_subject, rsvp_message = self.consumer.generate_notification_content(
            'rsvp_created', {'user_name': 'Taylor'}
        )
        self.assertEqual(rsvp_subject, 'Event RSVP')
        self.assertIn("Taylor has RSVP'd for the event.", rsvp_message)

    def test_control_flow_order_created_path(self):
        subject, message = self.consumer.generate_notification_content(
            'order_created', {'id': 'ORDER-42', 'user_id': 'user-1'}
        )
        self.assertEqual(subject, 'Ticket Purchase Confirmation')
        self.assertIn("ORDER-42", message)

    def test_control_flow_falls_back_to_default(self):
        subject, message = self.consumer.generate_notification_content(
            'archived', {'note': 'cleanup'}
        )
        self.assertEqual(subject, 'System Notification')
        self.assertIn("archived", message)
