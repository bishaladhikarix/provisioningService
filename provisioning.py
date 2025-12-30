from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
import subprocess
import re
from typing import List, Optional

app = FastAPI(title="Frappe Provisioning Service")

BENCH_DIR = "/home/username/Desktop/new-bench"
BENCH_BIN = "/home/username/.local/bin/bench"

ADMIN_PASSWORD = "admin"
DB_ROOT_USER = "root"
DB_ROOT_PASSWORD = "1234567"

#  User Creation Function Path
CREATE_USER_FUNCTION_PATH = "appname.users.create_user"

#Request Schema-
class CreateSiteRequest(BaseModel):
    site_name: str
    apps: List[str] = []
    email: str
    password: str
    first_name: Optional[str] = "User"

    @field_validator("site_name")
    @classmethod
    def validate_site_name(cls, v):
        if not re.match(r"^[a-z0-9.-]+$", v):
            raise ValueError("Invalid site name")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", v):
            raise ValueError("Invalid email address")
        return v


#Helper
def run_cmd(cmd: list):
    print("\n▶ Running:")
    print(" ".join(cmd))

    proc = subprocess.Popen(
            cmd,
            cwd=BENCH_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
            )

    for line in proc.stdout:
        print(line.strip())

    if proc.wait() != 0:
        raise RuntimeError("Command failed")

def create_user(site: str, email: str, password: str, first_name: str):
    """
    Calls the Frappe app function to create a user.
    Uses the CREATE_USER_FUNCTION_PATH variable.
    """
    kwargs = {
        "email": email,
        "password": password,
        "first_name": first_name
    }

    cmd = [
        BENCH_BIN,
        "--site",
        site,
        "execute",
        CREATE_USER_FUNCTION_PATH,  # e.g. something.users.create_user
        "--kwargs",
        str(kwargs)
    ]

    run_cmd(cmd)

# API Route
@app.post("/createsite")
def create_site(payload: CreateSiteRequest):
    site = payload.site_name.strip()

    try:
        # 1. Create site
        create_site_cmd = [
                BENCH_BIN,
                "new-site",
                site,
                "--admin-password",
                ADMIN_PASSWORD,
                "--mariadb-root-username",
                DB_ROOT_USER,
                "--mariadb-root-password",
                DB_ROOT_PASSWORD,
                ]
        run_cmd(create_site_cmd)

        # 2. Install apps
        for app_name in payload.apps:
            install_app_cmd = [
                    BENCH_BIN,
                    "--site",
                    site,
                    "install-app",
                    app_name
                    ]
            run_cmd(install_app_cmd)

        # 3. Create user via script
        create_user(site, payload.email, payload.password, payload.first_name)

        return {
                "status": "success",
                "site": site,
                "installed_apps": payload.apps,
                "user_created": payload.email
                }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#pip install fastapi uvicorn pydantic(install dependency)
#uvicorn provisioning:app --host 127.0.0.1 --port 9010 (to run this server)

