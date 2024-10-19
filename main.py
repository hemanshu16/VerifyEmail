import dns.resolver
from fastapi import FastAPI
from pydantic import BaseModel
import datetime
import smtplib
import json
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

# Initialize FastAPI app
app = FastAPI()

@app.get("/api/checkhealth")
async def checkHealth():
    return JSONResponse(status_code=200,content="Health Is Up")

class EmailRequest(BaseModel):
    email: EmailStr  # Email validation

# POST API endpoint to create an item
@app.post("/api/verifyemail")
async def verifyEmail(emailRequest: EmailRequest):
    email = None
    print(emailRequest.email)
    try:
        email = emailRequest.email
    except ValueError:
        return JSONResponse(status_code=400, content=ApiResponse("Provide Email Address",False).to_dict())

    if check_email_exists(email) :
        return JSONResponse(status_code=200, content=ApiResponse("Email Exist",True).to_dict())
    else:
        return JSONResponse(
             content=ApiResponse("Provided Email Not Exist",False).to_dict(),
             status_code=200
        )



def get_mx_records(domain):
    try:
        records = dns.resolver.resolve(domain, 'MX')
        mx_records = [str(record.exchange) for record in records]
        return mx_records
    except Exception as e:
        print(f"Error retrieving MX records for domain {domain}: {e}")
        return []

def check_email_exists(email):
    domain = email.split('@')[-1]
    mx_records = get_mx_records(domain)

    if not mx_records:
        print(f"No MX records found for domain {domain}")
        return False

    for mx in mx_records:
        try:
            server = smtplib.SMTP(mx)
            server.set_debuglevel(0)
            server.helo()
            server.mail('test@example.com')
            code, message = server.rcpt(email)
            server.quit()

            if code == 250:
                return True
            else:
                continue
        except Exception as e:
            print(f"Error connecting to mail server {mx}: {e}")
            continue

    return False


class ApiResponse:
    def __init__(self, message, isExist):
        self.message = message
        self.isExist = isExist
        self.timestamp = datetime.datetime.now()

    def to_dict(self):
        return {
            "message": self.message,
            "isExist": self.isExist,
            "timestamp": str(self.timestamp)
        }

    def __str__(self):
        return f"{self.message} at {self.timestamp}"

# Run the server with uvicorn
# uvicorn filename:app --reload
