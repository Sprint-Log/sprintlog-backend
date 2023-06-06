from litestar.config.cors import CORSConfig

config = CORSConfig(
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""Default CORS config."""
