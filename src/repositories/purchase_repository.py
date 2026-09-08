from sqlalchemy.orm import Session

from baked_good.baked_good_schema import BakedGoodSchema
from drink_recipe.drink_recipe_schema import DrinkRecipeSchema
from promotion.promotion_schema import PromotionSchema
from purchase.purchase_schema import PurchaseItemSchema, PurchaseSchema


class PurchaseRepository:
    def __init__(self, db: Session):
        self.db = db


    def get_item_price(self, item_type: str, item_id: int) -> float:
        if item_type == "baked_good":
            item = self.db.query(BakedGoodSchema).filter(BakedGoodSchema.id == item_id).first()
            if not item:
                raise ValueError(f"Baked good with id {item_id} not found")
            return item.retail_price

        elif item_type == "drink_recipe":
            item = self.db.query(DrinkRecipeSchema).filter(DrinkRecipeSchema.id == item_id).first()
            if not item:
                raise ValueError(f"Drink recipe with id {item_id} not found")
            return item.sale_price  # <-- correct field

        else:
            raise ValueError(f"Unknown item_type '{item_type}'")


    def get_promotion(self, promo_id: int) -> PromotionSchema | None:
        return (
            self.db.query(PromotionSchema)
            .filter(PromotionSchema.id == promo_id)
            .first()
        )


    def create_purchase(
        self,
        subtotal: float,
        discount_amount: float,
        tax_amount: float,
        total: float,
        loyalty_points_awarded: int,
        customer_id: int | None,
        promo_id: int | None,
        items: list[dict],
    ) -> PurchaseSchema:

        purchase = PurchaseSchema(
            customer_id=customer_id,
            promo_id=promo_id,
            subtotal=subtotal,
            discount_amount=discount_amount,
            tax_amount=tax_amount,
            total=total,
            loyalty_points_awarded=loyalty_points_awarded,
        )

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
        return (
            self.db.query(PurchaseSchema)
            .filter(PurchaseSchema.id == purchase_id)
            .first()
        )


    def list_purchases(self) -> list[PurchaseSchema]:
        return self.db.query(PurchaseSchema).all()
