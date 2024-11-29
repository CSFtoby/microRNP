from pydantic import BaseModel


class PaymentRequest(BaseModel):
    code_customer: str
    code_subsidiary: str
    code_user: str
