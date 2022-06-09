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
the switch ports. Today's scan found <INSERT NUMBER OF CHANGES> IP address(es) \
that have changed since last scan. Today's scan failed to connect to <NUMBER OF FAILED \
CONNECTIONS> IP(s) out of <INSERT NUMBER OF DEVICES> device. View the attatched log file for details. The first \
attatched file is a report of switches with innactive ports \
querried.

-- Zeros Program
"""
        self.msg = EmailMessage()
        self._load_config()

    def _load_config(self):
        with open('config.json', 'r') as fd:
            config = json.load(fd).get('Email')
            self.username = config.get('username')
            self.password = config.get('password')
            self.server = config.get('server')
            self.port = config.get('port')
            self.recipient = config.get('recipient')

    def update_email_body(self, num_ip_changes=None, num_failed=None, num_devices=None):
        if num_ip_changes:
            self.body = self.body.replace('<INSERT NUMBER OF CHANGES>', str(num_ip_changes))
        if num_failed:
            self.body = self.body.replace('<NUMBER OF FAILED CONNECTIONS>', str(num_failed))
        if num_devices:
            self.body = self.body.replace('<INSERT NUMBER OF DEVICES>', str(num_devices))

    def send_update_email(self, fname):
        self.update_email_body(num_ip_changes=-1, num_failed=-1, num_devices=-1)
        self.msg['Subject'] = 'Daily Switch Ports Update'
        self.msg['From'] = self.username
        self.msg['To'] = self.recipient
        self.msg.set_content(self.body)
        for file in ['report.txt', f'logs/{fname}.log']:
            with open(file, 'rb') as fd:
                file_data = fd.read()
            self.msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file.replace('logs/', ''))
        with smtplib.SMTP(self.server, self.port) as smtp:
            smtp.send_message(self.msg)

