from django.core.mail.backends.smtp import EmailBackend

class CustomEmailBackend(EmailBackend):
    def open(self):
        if self.connection is not None:
            return False
        try:
            self.connection = self.connection_class(self.host, self.port, timeout=self.timeout)
            if self.use_tls:
                self.connection.starttls()
            self.connection.login(self.username, self.password)
        except Exception:
            if not self.fail_silently:
                raise
            return False
        return True
