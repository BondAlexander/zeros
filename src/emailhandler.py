from email.message import EmailMessage
import smtplib
import json

class EmailHandler:
    def __init__(self):
        self.username = None
        self.password = None
        self.server = None
        self.port = None
        self.recipient = None
        self.path_to_log_file = None
        self.body = """
        Hello,
            This is an automated update to inform you of the current activity on \
        switch ports. Today's scan found <INSERT NUMBER OF CHANGES> IP addrsses \
        that have changed since last scan. Today's scan found <NUMBER OF FAILED \
        CONNECTIONS>. View the attatched log file for details. The second \
        attatched file has the output from all switches that were successfully \
        querried.

        -- Zeros Program
        """
        self.msg = EmailMessage()
        self._load_config()

    def _load_config(self):
        with open('auth.json', 'r') as fd:
            config = json.load(fd).get('Email')
            self.username = config.get('username')
            self.password = config.get('password')
            self.server = config.get('server')
            self.port = config.get('port')
            self.recipient = config.get('recipient')

    def update_email_body(self, num_ip_changes, num_failed):
        self.body.replace('<INSERT NUMBER OF CHANGES>', num_ip_changes)
        self.body.replace('<NUMBER OF FAILED CONNECTIONS>', num_failed)

    def update_email_message(self):
        self.msg['Subject'] = 'Daily Switch Ports Update'
        self.msg['From'] = self.username
        self.msg['To'] = self.recipient
        self.msg.set_content(self.body)

    def send_update_email(self):
        with smtplib.SMTP(self.server, self.port) as smtp:
            smtp.send_message(self.msg)

