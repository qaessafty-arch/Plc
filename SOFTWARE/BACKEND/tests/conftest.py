import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["API_TOKEN"] = "test-token"
os.environ["PLC_SOURCE"] = "none"
