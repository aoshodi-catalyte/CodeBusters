"""
Repository layer for purchase-related database operations.

Provides persistence and lookup utilities for purchases, purchase items,
promotions, and item pricing. This layer contains no business logic and
is used by the PurchaseService to execute domain rules.
"""

from sqlalchemy.orm import Session

from baked_good.baked_good_schema import BakedGoodSchema
from drink_recipe.drink_recipe_schema import DrinkRecipeSchema
from promotion.promotion_schema import PromotionSchema
from purchase.purchase_schema import PurchaseItemSchema, PurchaseSchema


class PurchaseRepository:
    """
    Repository responsible for interacting with purchase-related tables.
    """
    def _normalize_item_type(self, item_type: str) -> str:
        """
        Normalize user-provided item_type strings into canonical values.

        Accepted baked good variants:
            baked good, baked_good, Baked Good, Baked good, BakedGood

        Accepted drink recipe variants:
            drink, drink recipe, Drink, Drink Recipe, Drink recipe

        Returns:
            "baked_good" or "drink_recipe"

        Raises:
            ValueError if the type cannot be normalized.
        """
        normalized = item_type.strip().lower().replace(" ", "_")

        baked_good_aliases = {
            "baked_good", "bakedgood",
        }

        drink_aliases = {
            "drink", "drink_recipe", "drinkrecipe",
        }

        if normalized in baked_good_aliases:
            return "baked_good"

        if normalized in drink_aliases:
            return "drink_recipe"

        raise ValueError(f"Invalid item_type '{item_type}'. Allowed types: Baked good or drink.")


    def __init__(self, db: Session):
        """
        Initialize the repository with a database session.

        Args:
            db (Session): SQLAlchemy database session.
        """
        self.db = db


    def get_item_price(self, item_type: str, item_id: int) -> float:
        """
        Retrieve the price of an item based on its type and ID.

        Args:
            item_type (str): "baked_good" or "drink_recipe".
            item_id (int): ID of the item.

        Returns:
            float: The price of the item at time of sale.

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
            return item.retail_price

        if item_type == "drink_recipe":
            item = (
                self.db.query(DrinkRecipeSchema)
                .filter(DrinkRecipeSchema.id == item_id)
                .first()
            )
            if item is None:
                raise ValueError(f"Drink recipe with id {item_id} not found")
            return item.sale_price

        # Should never reach here because normalization handles errors
        raise ValueError(f"Invalid item_type '{item_type}'. Allowed types: Baked good or drink.")



    def get_promotion(self, promo_id: int) -> PromotionSchema | None:
        """
        Retrieve a promotion by ID.

        Args:
            promo_id (int): Promotion ID.

        Returns:
            PromotionSchema | None: Promotion record or None if not found.
        """
        return (
            self.db.query(PromotionSchema)
            .filter(PromotionSchema.id == promo_id)
            .first()
        )


    def create_purchase(self, purchase_data: dict, items: list[dict]) -> PurchaseSchema:
        """
        Create a purchase and its associated line items.

        Args:
            purchase_data (dict): Dictionary containing subtotal, discount,
                                  tax, total, loyalty points, customer_id,
                                  and promo_id.
            items (list[dict]): List of item dictionaries containing
                                item_type, item_id, quantity, price_at_sale.

        Returns:
            PurchaseSchema: The persisted purchase record.
        """
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
        """
        Retrieve a purchase by ID.

        Args:
            purchase_id (int): Purchase ID.

        Returns:
            PurchaseSchema | None: Purchase record or None if not found.
        """
        return (
            self.db.query(PurchaseSchema)
            .filter(PurchaseSchema.id == purchase_id)
            .first()
        )


    def list_purchases(self) -> list[PurchaseSchema]:
        """
        Retrieve all purchases.

        Returns:
            list[PurchaseSchema]: List of all purchase records.
        """
        return self.db.query(PurchaseSchema).all()
