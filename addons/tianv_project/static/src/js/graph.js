openerp.tianv_project = function (instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.web.tianv_project = instance.web.tianv_project || {};

    instance.web.views.add('project_report', 'instance.tianv_project.QuickSearchListView');
    instance.tianv_project.QuickSearchListView = instance.web_graph.GraphView.extend({
        init: function () {
            this._super.apply(this, arguments);
            this.journals = [];
            this.periods = [];
            this.start_date = new Date().toString('yyyy') + '-01-01';
            this.end_date = new Date().toString('yyyy') + '-12-31';
        },
        start: function () {
            var tmp = this._super.apply(this, arguments);
            var self = this;
            var defs = [];
            this.$el.parent().prepend(QWeb.render("PeriodTimePicker", {widget: this}));
            this.start_date_picker = new instance.web.DateWidget(this);
            this.start_date_picker.on('datetime_changed', this, _.bind(function () {
                self.start_date = this.value === '' ? null : this.start_date_picker.get_value();
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            }, this));
            this.start_date_picker.appendTo(this.$el.parent().find('div.oe_start_date_picker'));
            this.start_date_picker.set_value(this.start_date);
            this.end_date_picker = new instance.web.DateWidget(this);
            this.end_date_picker.on('datetime_changed', this, _.bind(function () {
                self.end_date = this.value === '' ? null : this.end_date_picker.get_value();
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            }, this));
            this.end_date_picker.appendTo(this.$el.parent().find('div.oe_end_date_picker'));
            this.end_date_picker.set_value(this.end_date);
            return tmp;
        },
        do_search: function (domain, context, group_by) {
            var self = this;
            this.last_domain = domain;
            this.last_context = context;
            this.last_group_by = group_by;
            this.old_search = _.bind(this._super, this);
            return self.search_by_date();
        },
        search_by_date: function () {
            var self = this;
            var domain = [];
            if (self.start_date != null && self.start_date != false) domain.push(["period", ">=", self.start_date]);
            if (self.end_date != null && self.end_date != false) domain.push(["period", "<=", self.end_date]);
            var compound_domain = new instance.web.CompoundDomain(self.last_domain, domain);
            self.dataset.domain = compound_domain.eval();
            return self.old_search(compound_domain, self.last_context, self.last_group_by);
        }
    });
};
