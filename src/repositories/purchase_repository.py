"""
Repository layer for purchase-related database operations.
"""

from decimal import Decimal

from sqlalchemy.orm import Session

from baked_good.baked_good_schema import BakedGoodSchema
from drink_recipe.drink_recipe_schema import DrinkRecipeSchema
from exceptions.baked_good_exceptions import BakedGoodNotFoundError
from exceptions.drink_recipe_exceptions import DrinkRecipeNotFoundError
from promotion.promotion_schema import PromotionSchema
from purchase.purchase_schema import PurchaseItemSchema, PurchaseSchema


class PurchaseRepository:
    """
    Repository responsible for interacting with purchase-related tables.
    """

    def __init__(self, db: Session):
        self.db = db

    def _normalize_item_type(self, item_type: str) -> str:
        """
        Normalize an item type to the value used by the database.

        Accepts common variations of baked good and drink recipe item types
        and converts them to their standardized database values.

        Args:
            item_type: The item type provided by the caller.

        Returns:
            str: The normalized item type.

        Raises:
            ValueError: If the item type is not supported.
        """
        normalized = item_type.strip().lower().replace(" ", "_")

        baked_good_aliases = {"baked_good", "bakedgood"}
        drink_aliases = {"drink", "drink_recipe", "drinkrecipe"}

        if normalized in baked_good_aliases:
            return "baked_good"

        if normalized in drink_aliases:
            return "drink_recipe"

        raise ValueError(
            f"Invalid item_type '{item_type}'. "
            "Allowed types: Baked good or drink."
        )

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
            BakedGoodNotFoundError: If the baked good does not exist.
            DrinkRecipeNotFoundError: If the drink recipe does not exist.
            ValueError: If the item type is unknown.
        """
        item_type = self._normalize_item_type(item_type)

        if item_type == "baked_good":
            item = (
                self.db.query(BakedGoodSchema)
                .filter(BakedGoodSchema.id == item_id)
                .first()
            )
            if item is None:
                raise BakedGoodNotFoundError(item_id)
            return item.retail_price

        if item_type == "drink_recipe":
            item = (
                self.db.query(DrinkRecipeSchema)
                .filter(DrinkRecipeSchema.id == item_id)
                .first()
            )
            if item is None:
                raise DrinkRecipeNotFoundError(item_id)
            return item.sale_price

        # Should never reach here because normalization handles errors
        raise ValueError(f"Invalid item_type '{item_type}'. Allowed types: Baked good or drink.")

    def get_promotion(self, promo_id: int) -> PromotionSchema | None:
        """
        Retrieve a promotion by its ID.

        Args:
            promo_id: The ID of the promotion to retrieve.

        Returns:
            PromotionSchema | None: The matching promotion if found,
            otherwise None.
        """
        return (
            self.db.query(PromotionSchema)
            .filter(PromotionSchema.id == promo_id)
            .first()
        )

    def create_purchase(
        self,
        purchase_data: dict,
        items: list[dict],
    ) -> PurchaseSchema:
        """
        Create and persist a purchase and its associated items.

        The purchase record is created first so its generated ID can be
        assigned to each purchase item. Each item's price is retrieved from
        the corresponding baked good or drink recipe and stored as the
        price at the time of sale.

        Args:
            purchase_data (dict): Dictionary containing subtotal, discount,
                                tax, total, loyalty points, customer_id,
                                employee_id, and promo_id.
            items (list[dict]): List of item dictionaries containing
                                item_type, item_id, quantity, price_at_sale.

        Returns:
            PurchaseSchema: The newly created purchase with its items.

        Raises:
            ValueError: If an item type is invalid or an item cannot be found.
        """
        try:
            purchase = PurchaseSchema(**purchase_data)

            self.db.add(purchase)
            self.db.flush()

            for item in items:
                normalized_type = self._normalize_item_type(item["item_type"])
                price = self.get_item_price(
                    normalized_type,
                    item["item_id"],
                )

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

        except Exception:
            self.db.rollback()
            raise

        return purchase

    def get_purchase(self, purchase_id: int) -> PurchaseSchema | None:
        """
        Retrieve a purchase by its ID.

        Args:
            purchase_id: The ID of the purchase to retrieve.

        Returns:
            PurchaseSchema | None: The matching purchase if found,
            otherwise None.
        """
        return (
            self.db.query(PurchaseSchema)
            .filter(PurchaseSchema.id == purchase_id)
            .first()
        )

    def list_purchases(self) -> list[PurchaseSchema]:
        """
        Retrieve all purchases from the database.

        Returns:
            list[PurchaseSchema]: A list containing all purchase records.
        """
        return self.db.query(PurchaseSchema).all()
