import io
import pandas as pd
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
import random
from faker import Faker

fake = Faker()


@pytest.mark.django_db
class TestCSVImportAPI:
    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/file-upload/"

    def create_csv_file_with_records(self, records):
        df = pd.DataFrame(records)
        csv_io = io.StringIO()
        df.to_csv(csv_io, index=False)
        csv_io.seek(0)

        return SimpleUploadedFile(
            "users.csv", csv_io.read().encode("utf-8"), content_type="text/csv"
        )

    def create_csv_file(self):
        records = []
        for _ in range(1000):
            record = {}

            # Randomly include or skip fields
            if random.choice([True, False]):
                record["email"] = fake.email()
            if random.choice([True, False]):
                record["name"] = fake.name()
            if random.choice([True, False]):
                record["age"] = random.randint(18, 60)

            records.append(record)

        return self.create_csv_file_with_records(records)

    def create_other_columns_file(self):
        records = [
            {"username": fake.user_name(), "password": fake.password()}
            for _ in range(1000)
        ]
        return self.create_csv_file_with_records(records)

    def test_csv_import_large_random_data(self):
        file = self.create_csv_file()
        response = self.client.post(self.url, {"file": file}, format="multipart")
        assert response.status_code == 200

    def test_other_file_format(self):
        file = SimpleUploadedFile("users.txt", b"Hello, world!")
        response = self.client.post(self.url, {"file": file}, format="multipart")
        assert response.status_code == 400

    def test_csv_import_with_other_columns(self):
        file = self.create_other_columns_file()
        response = self.client.post(self.url, {"file": file}, format="multipart")
        assert response.status_code == 400
