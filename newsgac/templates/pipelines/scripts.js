document.addEventListener("DOMContentLoaded", e => {
    Vue.options.delimiters = ["[[", "]]"];

    initComponents();

    v = new Vue({
        el: "#vue-root",
        data: { ...data, error: {} },
        computed: {
            nlpParams: function() {
                return this.nlp_tools[this.model.nlp_tool._tag].parameters;
            },
            learnerParams: function() {
                return this.learners[this.model.learner._tag].parameters;
            },
            errors: function() {
                return Object.keys(this.error).map(fieldName => ({
                    fieldName,
                    errors: this.error[fieldName],
                }));
            }
        },
        methods: {
            setNlpTool: function(toolKey) {
                this.model.nlp_tool._tag = toolKey;
                this.model.nlp_tool.parameters = {};
                // set defaults for this tool:
                this.nlp_tools[toolKey].parameters.forEach((param) => {
                    this.$set(this.model.nlp_tool.parameters, param.attname, param.default);
                });

            },
            setLearner: function(key) {
                this.model.learner._tag = key;
                this.model.learner.parameters = {};
                // set defaults for this tool:
                this.learners[key].parameters.forEach((param) => {
                    this.$set(this.model.learner.parameters, param.attname, param.default);
                });

            },
            save: function() {
                fetch(this.saveUrl, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json; charset=utf-8",
                    },
                    body: JSON.stringify(this.model)
                }).then(response => response.json().then(responseObj => {
                    if (response.status < 200 || response.status > 299) {
                        this.error = responseObj.error
                    } else {
                        this.error = {};
                        window.location = this.pipelinesUrl;
                    }
                })).catch(e => {
                    this.error = {submit: [e.toString()]}
                });
            }
        },
    });

    function initComponents() {
        Vue.component("document-field", {
            props: ["param", "value"],
            template: `
                <div>
                    <h6><strong>[[ param.verbose_name || param.attname ]]</strong></h6>
                    <span class="help-block"><i>[[param.description]]</i></span>
                    <parameter-field
                        v-for="field in param.model"
                        :key="field.attname"
                        :param="field"
                        v-model="value[field.attname]"
                    />
                </div>
              `
        });

        Vue.component("textinput-field", {
            props: ["param", "value"],
            template: `
                <div class="row mar_ned">
                    <div class="col-md-3">
                        <p align="right" class="center-align-pad">
                            <strong>[[ param.verbose_name || param.attname ]]</strong>
                        </p>
                    </div>
                    <div class="col-md-1" />
                    <div class="col-md-8">
                        <input
                            type="text"
                            :value="value"
                            @change="$emit('input', $event.target.value)"
                        />
                        <span class="help-block"><i>[[param.description]]</i></span>
                    </div>
                </div>
              `
        });

         Vue.component("select-field", {
            props: ["param", "value"],
            template: `
                <div class="row mar_ned">
                    <div class="col-md-3">
                        <p align="right" class="center-align-pad">
                            <strong>[[ param.verbose_name || param.attname ]]</strong>
                        </p>
                    </div>
                    <div class="col-md-1" />
                    <div class="col-md-8">
                        <div class="btn-group">
                            <div
                                v-for="(choice, key) in param.choices"
                                :key="key"
                                @click="$emit('input', choice[0])"
                                :class="['btn', 'btn-default', {active: value === choice[0]}]"
                            >
                                [[ choice[1] ]]
                            </div>
                        </div>
                        <span class="help-block"><i>[[param.description]]</i></span>
                    </div>
                </div>
              `
        });

        Vue.component("boolean-field", {
            props: ["param", "value"],
            template: `
                <div class="row mar_ned">
                    <div class="col-md-3">
                        <p align="right" class="center-align-pad">
                            <strong>[[ param.verbose_name || param.attname ]]</strong>
                        </p>
                    </div>
                    <div class="col-md-1">
                        <div class="checkbox">
                            <label>
                                <input type="checkbox" :checked="value" @input="$emit('input', $event.target.checked)">
                                <span class="cr"><i class="cr-icon fa fa-check"></i></span>
                            </label>
                        </div>
                    </div>
                    <div class="col-md-8">
                        <span class="help-block"><i>[[param.description]]</i></span>
                    </div>
                </div>
              `
        });


        Vue.component("parameter-field", {
            props: ["param", "value"],
            template: `<div>
                            <boolean-field v-if="param.type === 'BooleanField'" @input="$emit('input', $event)" v-bind="$props"></boolean-field>
                            <document-field v-else-if="param.type === 'EmbeddedDocumentField'" @input="$emit('input', $event)" v-bind="$props"></document-field>
                            <select-field v-else-if="param.type === 'CharField' && param.choices" @input="$emit('input', $event)" v-bind="$props"></select-field>
                            <textinput-field v-else @input="$emit('input', $event)" v-bind="$props"></textinput-field>
                        </div>`
        });
    }

});
