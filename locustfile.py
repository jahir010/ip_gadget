from locust import HttpUser, task, between

class FastAPIUser(HttpUser):
    wait_time = between(1, 3)  # simulate user delay

    @task
    def login(self):
        self.client.post(
            "/auth/login",
            data={
                "email": "admin@gmail.com",
                "password": "admin"
            }
        )