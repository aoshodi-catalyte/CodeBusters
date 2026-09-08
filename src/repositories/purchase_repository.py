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

        raise ValueError(f"Unknown item_type '{item_type}'")

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
            purchase_item = PurchaseItemSchema(
                purchase_id=purchase.id,
                item_type=item["item_type"],
                item_id=item["item_id"],
                quantity=item["quantity"],
                price_at_sale=item["price_at_sale"],
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
