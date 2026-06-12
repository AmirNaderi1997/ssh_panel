from decimal import Decimal
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.exceptions import EntityNotFoundException, BusinessRuleException
from backend.app.models.reseller import Reseller, Transaction
from backend.app.models.admin import Admin
from backend.app.repositories.reseller_repo import ResellerRepository, TransactionRepository


class ResellerService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.reseller_repo = ResellerRepository(db)
        self.transaction_repo = TransactionRepository(db)

    async def create_reseller(self, admin_id: uuid.UUID, max_users: int = 100) -> Reseller:
        """Initialize a reseller profile for an existing Admin."""
        existing = await self.reseller_repo.get_by_admin_id(admin_id)
        if existing:
            raise BusinessRuleException("Reseller profile already exists for this admin")
            
        reseller = Reseller(
            admin_id=admin_id,
            credits=Decimal("0.00"),
            balance=Decimal("0.00"),
            max_users=max_users,
            status="ACTIVE"
        )
        self.db.add(reseller)
        await self.db.flush()
        return reseller

    async def allocate_credits(
        self, reseller_id: uuid.UUID, amount: Decimal, description: str, performer_id: uuid.UUID
    ) -> Transaction:
        """Add credit balance to a reseller."""
        reseller = await self.reseller_repo.get(reseller_id)
        if not reseller:
            raise EntityNotFoundException("Reseller", reseller_id)

        reseller.credits += amount
        self.db.add(reseller)

        # Create audit transaction record
        transaction = Transaction(
            reseller_id=reseller_id,
            type="CREDIT",
            amount=amount,
            description=description,
            admin_id=performer_id
        )
        self.db.add(transaction)
        await self.db.flush()
        return transaction

    async def deduct_credits(
        self, reseller_id: uuid.UUID, amount: Decimal, description: str, performer_id: uuid.UUID
    ) -> Transaction:
        """Deduct credit balance from a reseller."""
        reseller = await self.reseller_repo.get(reseller_id)
        if not reseller:
            raise EntityNotFoundException("Reseller", reseller_id)

        if reseller.credits < amount:
            raise BusinessRuleException("Insufficient credit balance")

        reseller.credits -= amount
        self.db.add(reseller)

        transaction = Transaction(
            reseller_id=reseller_id,
            type="DEBIT",
            amount=amount,
            description=description,
            admin_id=performer_id
        )
        self.db.add(transaction)
        await self.db.flush()
        return transaction
