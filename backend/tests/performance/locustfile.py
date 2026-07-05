from locust import HttpUser, task, between
import random

SAMPLE_QUERIES = [
    "What is the return policy?",
    "How does authentication work?",
    "Explain the distributed tracing architecture."
]

TEST_DOCS = ["tests/fixtures/test_doc.pdf"]

class QueryUser(HttpUser):
    wait_time = between(1, 5)
    weight = 7
    @task
    def query_pipeline(self):
        self.client.post("/query", json={"query": random.choice(SAMPLE_QUERIES)})

class IngestUser(HttpUser):
    wait_time = between(5, 15)
    weight = 2
    @task
    def ingest_document(self):
        # Using a mock string as file content to simulate upload
        self.client.post("/ingest", files={"file": ("test_doc.pdf", b"mock content")})

class AdminUser(HttpUser):
    wait_time = between(10, 30)
    weight = 1
    @task
    def check_evaluations(self):
        self.client.get("/evaluations")
