/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";

export class UpDateStockDialog extends Component {
    static template = "Al_Shifa_pharmacy.action_popUpView";
    static components = { Dialog };
    static props = {
        productId: Number,
        productName: String,
        onUpdated: { type: Function, optional: true },
        close: Function,
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");

        this.state = useState({
            lot_Name: "",
            new_purchased_qty: 0,
            expiration_date: "",
        });
    }

    async ADD_Quantity() {
        if (!this.state.lot_Name) {
            this.notification.add("من فضلك أدخل اسم اللوت", { type: "danger" });
            return;
        }
        if (!this.state.new_purchased_qty || Number(this.state.new_purchased_qty) <= 0) {
            this.notification.add("من فضلك أدخل كمية أكبر من صفر", { type: "danger" });
            return;
        }

        try {
            await this.orm.call(
                "product.template",
                "action_add_stock_lot",
                [
                    [this.props.productId],
                    this.state.lot_Name,
                    parseFloat(this.state.new_purchased_qty),
                    this.state.expiration_date || false,
                ]
            );

            this.notification.add("تم تحديث المخزون بنجاح", { type: "success" });

            // إشعار الـ List View إنه يعمل refresh
            if (this.props.onUpdated) {
                await this.props.onUpdated();
            }

            // قفل الـ Popup
            this.props.close();
        } catch (error) {
            this.notification.add(
                (error.data && error.data.message) || "حدث خطأ أثناء تحديث المخزون",
                { type: "danger" }
            );
        }
    }

    cancel() {
        this.props.close();
    }
}