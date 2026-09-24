/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class FormView extends Component {
    static template = "Al_Shifa_pharmacy.action_formView";

    setup() {
        // في أودو 18 نستخدم خدمة ORM بدلاً من RPC المباشر
        this.orm = useService("orm");

        // متابعة حالة الحقول لربطها بـ t-model
        this.state = useState({
            name: "",
            is_medicine: true,
            list_price: 0.0,
        });
    }

    async createRecord() {
        await this.orm.create("product.template", [{
            name: this.state.name,
            list_price: this.state.list_price,
            is_medicine: this.state.is_medicine,
        }]);

        // تنظيف الحقول بعد الحفظ
        this.resetForm();

        // إشعار المكون الأب (List View) لإعادة تحميل البيانات إذا كان تمرير Callback متاحاً
        if (this.props.onRecordCreated) {
            await this.props.onRecordCreated();
        }
    }

    // دالة الإلغاء وتنظيف الواجهة
    cancel() {
        this.resetForm();
    }

    resetForm() {
        this.state.name = "";
        this.state.is_medicine = true;
        this.state.list_price = 0.0;
    }
   
}