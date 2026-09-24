/** @odoo-module **/

import { Component, useState, onWillStart, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { FormView } from "@Al_Shifa_pharmacy/components/formView/formView";
import { UpDateStockDialog } from "@Al_Shifa_pharmacy/components/updateStockDialog/updateStockDialog";

export class ListViewAction extends Component {
    static template = "Al_Shifa_pharmacy.action_list_view";

    static components = { FormView };

    setup() {
        // استبدال orm بـ rpc
        this.orm = useService("orm");
        // خدمة فتح الـ Dialogs (Popups) الرسمية بتاعة أودو
        this.dialog = useService("dialog");

        this.state = useState({
            records: [],
            showCreateForm: false,
        });

        onWillStart(async () => {
            await this.loadData();
        });

        this.intervalId = setInterval(() => { this.loadData() }, 3000);
        onWillUnmount(() => { clearInterval(this.intervalId) });

    }

    async loadData() {
        // جلب البيانات بأسلوب ORM المباشر
        const data = await this.orm.searchRead(
            "product.template",
            [],
            ["id", "name", "qty_available", "list_price"]
        );
        this.state.records = data;
    }

    async createRecord() {
        // إنشاء السجل عبر ORM
        await this.orm.create("product.template", [{
            name: "name of the new medicine",
            list_price: 15.0,
            is_medicine: true,
            requires_prescription: false,
            min_stock_qty: 5.0,
        }]);

        // إعادة تحميل القائمة بعد الإضافة
        await this.loadData();
    }
    async deleteRecord(recordId) {
        // حذف السجل باستعمال الـ ID
        await this.orm.unlink("product.template", [recordId]);

        // إعادة تحميل القائمة لتحديث الواجهة
        await this.loadData();
    }
     toggleCreateForm() {
       console.log(" from toggleCreateForm");
       this.state.showCreateForm=!this.state.showCreateForm;
       console.log(this.state.showCreateForm);
    }

    // بيفتح الـ Popup بتاع تحديث المخزون لسجل معيّن
    // بنبعت id و name بس (مش الـ record Object كامل) عشان نتجنب مشاكل الـ reactive proxy
    openUpdateDialog(record) {
        this.dialog.add(UpDateStockDialog, {
            productId: record.id,
            productName: record.name,
            onUpdated: () => this.loadData(),
        });
    }
}

registry.category("actions").add("Al_Shifa_pharmacy_tag", ListViewAction);