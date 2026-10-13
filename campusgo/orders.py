class Result:
    def __init__(self, rejected=False, message="", success=None):
        self.rejected = rejected
        self.message = message
        self.success = (not rejected) if success is None else success


def order_total(unit_price, qty, has_promo=False):
    if qty <= 0:
        raise ValueError("qty must be greater than 0")
    subtotal = unit_price * qty
    if has_promo and subtotal >= 50000:
        return int(subtotal * 0.9)
    return subtotal


class Order:
    def __init__(self, id, owner, total):
        self.id, self.owner, self.total = id, owner, total
        self.status = "UNPAID"
        self.tenant_notifications = []

    def cancel(self, by):
        if self.status == "PROCESSING":
            return Result(rejected=True, message="Order is being processed")
        self.status = "CANCELLED"
        self.tenant_notifications.append("cancelled")
        return Result(rejected=False, message="Cancelled")

    def delete(self):
        self.status = "DELETED"


class Wallet:
    def __init__(self, balance, provider):
        self.balance, self.provider = balance, provider

    def pay(self, amount):
        if amount > self.balance:
            return Result(success=False, message="Insufficient balance")
        resp = self.provider.charge(amount)
        if resp.get("status") == "ACCEPTED":
            self.balance -= amount
            return Result(success=True, message="Paid")
        return Result(success=False, message="Payment rejected")