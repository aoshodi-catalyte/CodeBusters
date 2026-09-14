"""
Repository layer for purchase-related database operations.
"""

from decimal import Decimal

from sqlalchemy.orm import Session

from baked_good.baked_good_schema import BakedGoodSchema
from drink_recipe.drink_recipe_schema import DrinkRecipeSchema
from promotion.promotion_schema import PromotionSchema
from purchase.purchase_schema import PurchaseItemSchema, PurchaseSchema


class PurchaseRepository:
    """
    Repository responsible for interacting with purchase-related tables.
    """

    def __init__(self, db: Session):
        self.db = db

    def _normalize_item_type(self, item_type: str) -> str:
        normalized = item_type.strip().lower().replace(" ", "_")

        baked_good_aliases = {"baked_good", "bakedgood"}
        drink_aliases = {"drink", "drink_recipe", "drinkrecipe"}

        if normalized in baked_good_aliases:
            return "baked_good"

        if normalized in drink_aliases:
            return "drink_recipe"

        raise ValueError(f"Invalid item_type '{item_type}'. Allowed types: Baked good or drink.")

    @staticmethod
    def _as_decimal(value) -> Decimal:
        """
        Coerce a DB-returned price into Decimal.

        SQLAlchemy's Numeric type returns Decimal by default (asdecimal=True),
        so this is normally a no-op — but it guards against a column that's
        still typed as Float somewhere, which would otherwise silently
        reintroduce binary rounding error.
        """
        return value if isinstance(value, Decimal) else Decimal(str(value))

    def get_item_price(self, item_type: str, item_id: int) -> Decimal:
        """
        Retrieve the price of an item based on its type and ID.

        Returns:
            Decimal: The price of the item at time of sale.

        Raises:
            ValueError: If the item does not exist or type is unknown.
        """
        item_type = self._normalize_item_type(item_type)

        if item_type == "baked_good":
            item = (
                self.db.query(BakedGoodSchema)
                .filter(BakedGoodSchema.id == item_id)
                .first()
            )
            if item is None:
                raise ValueError(f"Baked good with id {item_id} not found")
            return self._as_decimal(item.retail_price)

        if item_type == "drink_recipe":
            item = (
                self.db.query(DrinkRecipeSchema)
                .filter(DrinkRecipeSchema.id == item_id)
                .first()
            )
            if item is None:
                raise ValueError(f"Drink recipe with id {item_id} not found")
            return self._as_decimal(item.sale_price)

        raise ValueError(f"Invalid item_type '{item_type}'. Allowed types: Baked good or drink.")

    def get_promotion(self, promo_id: int) -> PromotionSchema | None:
        return (
            self.db.query(PromotionSchema)
            .filter(PromotionSchema.id == promo_id)
            .first()
        )

    def create_purchase(self, purchase_data: dict, items: list[dict]) -> PurchaseSchema:
        purchase = PurchaseSchema(**purchase_data)

        self.db.add(purchase)
        self.db.flush()  # ensures purchase.id is available

        for item in items:
            normalized_type = self._normalize_item_type(item["item_type"])
            price = self.get_item_price(normalized_type, item["item_id"])

            purchase_item = PurchaseItemSchema(
                purchase_id=purchase.id,
                item_type=normalized_type,
                item_id=item["item_id"],
                quantity=item["quantity"],
                price_at_sale=price,
            )
            self.db.add(purchase_item)

        self.db.commit()
        self.db.refresh(purchase)

        return purchase

    def get_purchase(self, purchase_id: int) -> PurchaseSchema | None:
        return (
            self.db.query(PurchaseSchema)
            .filter(PurchaseSchema.id == purchase_id)
            .first()
        )

    def list_purchases(self) -> list[PurchaseSchema]:
        return self.db.query(PurchaseSchema).all()
