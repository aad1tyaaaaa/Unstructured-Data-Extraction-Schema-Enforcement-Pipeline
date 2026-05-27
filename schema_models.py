from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date

class InvoiceItem(BaseModel):
    description: str = Field(description="The description of the item or service provided.")
    quantity: float = Field(description="The number of items or hours of service. If not explicitly specified but a total is given, assume 1.")
    unit_price: float = Field(description="The price per single unit of the item.")
    total_price: float = Field(description="The total price for this line item (quantity * unit_price).")

    @field_validator('total_price')
    def check_total(cls, v, info):
        # We can implement internal consistency checks. Instructor will use these to retry.
        if 'quantity' in info.data and 'unit_price' in info.data:
            q = info.data['quantity']
            up = info.data['unit_price']
            # allow small floating point differences
            if abs((q * up) - v) > 0.05:
                raise ValueError(f"total_price ({v}) must approximately equal quantity ({q}) * unit_price ({up})")
        return v

class Invoice(BaseModel):
    invoice_number: str = Field(description="The unique identifier or number of the invoice.")
    invoice_date: date = Field(description="The date the invoice was issued in YYYY-MM-DD format.")
    
    vendor_name: str = Field(description="The name of the company or person issuing the invoice.")
    vendor_address: Optional[str] = Field(None, description="The address of the vendor.")
    
    customer_name: str = Field(description="The name of the company or person receiving the invoice.")
    customer_address: Optional[str] = Field(None, description="The address of the customer.")
    
    items: List[InvoiceItem] = Field(description="The list of line items in the invoice.")
    
    subtotal: Optional[float] = Field(None, description="The subtotal before tax. Must be sum of all item total_prices if present.")
    tax: Optional[float] = Field(None, description="The total tax amount applied.")
    total_amount: float = Field(description="The final total amount due on the invoice.")

    @field_validator('total_amount')
    def check_total_amount(cls, v, info):
        # Additional validation to guide the LLM
        subtotal = info.data.get('subtotal')
        tax = info.data.get('tax')
        if subtotal is not None and tax is not None:
            if abs((subtotal + tax) - v) > 0.05:
                raise ValueError(f"total_amount ({v}) should equal subtotal ({subtotal}) + tax ({tax})")
        return v
