(function($) {
    // COMMON UTILITIES

    function get_question_data_names($survey, question, options) {
        var $question = $survey.find("#question-"+question);
        var names = [];
        if ($question.is('.question-text')) {
            names = $question.find('.user-field').map(function() { return this.name; });
        }
        else if ($question.is('.question-single-choice')) {
            names = $question.find('.user-field').map(function() { return this.name; });
        }
        else if ($question.is('.question-multiple-choice')) {
            var selectors = '.user-field';
            if (options && options.length)
                selectors = jQuery.map(options, function(o){ return '#option-'+o+'-field, #option-'+o+'-field-open'}).join(',');
            names = $question.find(selectors).map(function() { return this.name; });
        }
        return names;
    }

    function was_filled($survey, question, options, last_participation_data) {
        if (!last_participation_data)
            return false;

        var $question = $survey.find("#question-"+question);
        if ($question.is('.question-text')) {
            var data = last_participation_data[$question.find('.user-field').attr("name")];
            if (data || data === "" || data === 0)
                return true;
        }
        else {
            for (var i=0 ; i < options.length ; i++) {
                var $option = $("#option-"+options[i]);
                var name = $option.find("input").attr("name");
                var value = $option.find("input").val();
                if (last_participation_data[name] == value) {
                    return true;
                }
            }
        }

        return false;
    }


    function form_element_fill($element, value) {
        $element.each(function() {
            switch (this.nodeName.toLowerCase()) {
                case "input":
                    switch (this.type) {
                        case "radio":
                            if (value == this.value)
                                this.checked = true;
                            break;
                        case "checkbox":
                            if (jQuery.isArray(value) && jQuery.inArray(value, this.value))
                                this.checked = true;
                            else if (value == this.value)
                                this.checked = true;
                            break;
                        default:
                            jQuery(this).val(value);
                        break;
                    }
                    break;
                case "select":
                    jQuery("option", this).each(function() {
                        if (this.value == value)
                            this.selected = true;
                    });
                    break;
                case "textarea":
                	this.value = value;
                	break;
                break;
            }
        });
        return $element;
    }

    function enable_options($options) {
        $options.each(function() {
            var $this = $(this);
            var checked = $this.find(':input:visible:not(.open-option-data)').attr('disabled', false).is(':checked')
            $this.find(':input.open-option-data').attr('disabled', !checked);
        });
    }

    function get_target_signature(question, options) {
        var s = "Q" + question;
        if (options) {
            for (var i=0 ; i < options.length; i++) {
                s = s + "O" + options[i];
            }
        }
        return s;
    }

    function is_active($survey, $question, rule) {
        var $options = $question.find(":checked");
        for (var i=0 ; i < $options.length ; i++) {
            var oid = parseInt(($options.eq(i).closest("li").attr("id") || '').replace("option-",""));
            if ($.inArray(oid, rule.subjectOptions) >= 0)
                return true;
        }

        var $selected = $question.find(":selected");
        for (var i=0 ; i < $selected.length ; i++) {
            var oid = parseInt(($selected.eq(i).attr("id") || '').replace("option-",""));
            if ($.inArray(oid, rule.subjectOptions) >= 0)
                return true;
        }

        return false;
    }

    // BUILTIN RULES

    function ShowQuestionRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),

            init: function($survey, last_participation_data) {
            },

            activate: function($survey, $question) {
                var old = this.active;
                this.active = is_active($survey, $question, this);
                return old !== this.active;
            },

            apply: function($survey, target, forward) {
                var $t = $survey.find("#question-"+this.objectQuestion);

                if (!$t.hasClass("starts-hidden"))
                    return;

                if (forward) {
                    $t.slideDown(function() {
                        enable_options($t.find('.choices > li'));
                    });
                } else {
                    $t.slideUp();
                }
            }
        });
    }
    ShowQuestionRule.showQuestions = true;
    ShowQuestionRule.showOptions = false;
    ShowQuestionRule.prototype.isExclusive = false;
    ShowQuestionRule.prototype.isFuture = false;
    ShowQuestionRule.prototype.name = "ShowQuestionRule";

    function HideQuestionRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,
            isFuture: false,

            init: function($survey, last_participation_data) {
            },

            activate: function($survey, $question) {
                var old = this.active;
                this.active = is_active($survey, $question, this);
                return old !== this.active;
            },

            apply: function($survey, target, forward) {
                var $t = $survey.find("#question-"+this.objectQuestion);

                if ($t.hasClass("starts-hidden"))
                    return;

                if (forward) {
                    $t.slideUp();
                } else {
                    $t.slideDown(function() {
                        enable_options($t.find('.choices > li'));
                    });
                }
            }
        });
    }
    HideQuestionRule.showQuestions = true;
    HideQuestionRule.showOptions = false;
    HideQuestionRule.prototype.isExclusive = false;
    HideQuestionRule.prototype.isFuture = false;
    HideQuestionRule.prototype.name = "HideQuestionRule";

    function ShowOptionsRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,
            isFuture: false,

            init: function($survey, last_participation_data) {
            },

            activate: function($survey, $question) {
                var old = this.active;
                this.active = is_active($survey, $question, this);
                return old !== this.active;
            },

            apply: function($survey, target, forward) {
                var selectors = self.objectOptions.map(function(o){return '#option-'+o}).join(',');
                var $t = $survey.find(selectors);

                if (forward) {
                    $t.each(function() {
                        var $o = $(this);
                        $o.slideDown(function () {
                            enable_options($o.find('.choices > li'));
                        });
                    });
                } else {
                    $t.each(function() {
                        $(this).slideUp();
                    });
                }
            }
        });
    }
    ShowOptionsRule.showQuestions = true;
    ShowOptionsRule.showOptions = true;
    ShowOptionsRule.prototype.isExclusive = false;
    ShowOptionsRule.prototype.isFuture = false;
    ShowOptionsRule.prototype.name = "ShowOptionsRule";

    function HideOptionsRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,
            isFuture: false,

            init: function($survey, last_participation_data) {
            },

            activate: function($survey, $question) {
                var old = this.active;
                this.active = is_active($survey, $question, this);
                return old !== this.active;
            },

            apply: function($survey, target, forward) {
                var selectors = self.objectOptions.map(function(o){return '#option-'+o}).join(',');
                var $t = $survey.find(selectors);

                if (forward) {
                    $t.each(function() {
                        var $o = $(this);
                        if ($o.is(':visible')) {
                            $o.slideUp();
                        }
                    });
                } else {
                    $t.each(function() {
                        var $o = $(this);
                        if (!$o.is(':visible')) {
                            $o.slideDown(function () {
                                enable_options($o.find('.choices > li'));
                            });
                        }
                    });
                }

            }
        });
    }
    HideOptionsRule.showQuestions = true;
    HideOptionsRule.showOptions = true;
    HideOptionsRule.prototype.isExclusive = false;
    HideOptionsRule.prototype.isFuture = false;
    HideOptionsRule.prototype.name = "HideOptionsRule";

    function CheckOptionsRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,
            isFuture: false,

            init: function($survey, last_participation_data) {
            },

            activate: function($survey, $question) {
                var old = this.active;
                this.active = is_active($survey, $question, this);
                return this.active === true && old === false;
            },

            apply: function($survey, target, forward) {
                if (!this.active)
                    return;

                var selectors = self.objectOptions.map(function(o){return '#option-'+o+' :input'}).join(',');
                var options = $survey.find(selectors).prop('checked', true);
                options.trigger('change', { synthetic: true });
            }
        });
    }
    CheckOptionsRule.showQuestions = true;
    CheckOptionsRule.showOptions = true;
    CheckOptionsRule.prototype.isExclusive = false;
    CheckOptionsRule.prototype.isFuture = false;
    CheckOptionsRule.prototype.name = "CheckOptionsRule";

    function UncheckOptionsRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,
            isFuture: false,

            init: function($survey, last_participation_data) {
            },

            activate: function($survey, $question) {
                var old = this.active;
                this.active = is_active($survey, $question, this);
                return this.active === true && old === false;
            },

            apply: function($survey, target, forward) {
                if (!this.active)
                    return;

                var selectors = self.objectOptions.map(function(o){return '#option-'+o+' :input'}).join(',');
                var options = $survey.find(selectors).prop('checked', false);
                options.trigger('change', { synthetic: true });
            }
        });
    }
    UncheckOptionsRule.showQuestions = true;
    UncheckOptionsRule.showOptions = true;
    UncheckOptionsRule.prototype.isExclusive = false;
    UncheckOptionsRule.prototype.isFuture = false;
    UncheckOptionsRule.prototype.name = "UncheckOptionsRule";

    function ExclusiveRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: null,
            isExclusive: true,
            isFuture: false,

            init: function($survey, last_participation_data) {
                self.subjectOptions.forEach(function(optionId) {
                    $("#option-" + optionId + " :input").addClass("exclusive");
                });
            },

            activate: function($survey, $question, evt) {
                var old = this.active;
                this.active = is_active($survey, $question, this);
                return this.active === true &&  old === false;
            },

            apply: function($survey, target, forward) {
                if (!this.active)
                    return;

                var so = this.subjectOptions;
                var extra = { synthetic: true };
                $survey.find("#question-"+this.subjectQuestion+" :checked").each(function() {
                    var oid = parseInt(($(this).closest("li").attr("id") || '').replace("option-",""));
                    if (so.indexOf(oid) < 0)
                        $(this).prop('checked', false).trigger('change', extra);
                });
            }
        });
    }
    ExclusiveRule.showQuestions = false;
    ExclusiveRule.showOptions = false;
    ExclusiveRule.prototype.isExclusive = true;
    ExclusiveRule.prototype.isFuture = false;
    ExclusiveRule.prototype.name = "ExclusiveRule";

    function FutureFillRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,
            isFuture: true,

            init: function($survey, last_participation_data) {
                this.last_participation_data = last_participation_data;
            },

            activate: function($survey, $question, evt) {
                this.active = false;
                if (was_filled($survey, this.subjectQuestion, this.subjectOptions, this.last_participation_data))
                    this.active = true;
                return this.active;
            },

            apply: function($survey, checked, forward) {
                if (!this.active)
                    return;

                var object_names = get_question_data_names($survey, this.objectQuestion, this.objectOptions);
                jQuery.each(object_names, function(i, object_name) {
                    var object_data = self.last_participation_data[object_name];
                    form_element_fill($survey.find('[name='+object_name+']'), object_data).trigger('change', { synthetic: true });
                });
            }
        });
    }
    FutureFillRule.showQuestions = true;
    FutureFillRule.showOptions = true;
    FutureFillRule.prototype.isExclusive = false;
    FutureFillRule.prototype.isFuture = true;
    FutureFillRule.prototype.name = "FutureFillRule";

    function FutureShowQuestionRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,
            isFuture: true,

            init: function($survey, last_participation_data) {
                this.last_participation_data = last_participation_data;
            },

            activate: function($survey, $question, evt) {
                this.active = false;
                if (was_filled($survey, this.subjectQuestion, this.subjectOptions, this.last_participation_data))
                    this.active = true;
                return this.active;
            },

            apply: function($survey, target, forward) {
                var $t = $survey.find("#question-"+this.objectQuestion);

                if (!$t.hasClass("starts-hidden") || !this.active)
                    return;

                if (forward) {
                    enable_options($t.show().find('.choices > li'));
                }
            }
        });
    }
    FutureShowQuestionRule.showQuestions = true;
    FutureShowQuestionRule.showOptions = false;
    FutureShowQuestionRule.prototype.isExclusive = false;
    FutureShowQuestionRule.prototype.isFuture = true;
    FutureShowQuestionRule.prototype.name = "FutureShowQuestionRule";

    function FutureHideQuestionRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,
            isFuture: true,

            init: function($survey, last_participation_data) {
                this.last_participation_data = last_participation_data;
            },

            activate: function($survey, $question, evt) {
                this.active = false;
                if (was_filled($survey, this.subjectQuestion, this.subjectOptions, this.last_participation_data))
                    this.active = true;
                return this.active;
            },

            apply: function($survey, target, forward) {
                var $t = $survey.find("#question-"+this.objectQuestion);

                if ($t.hasClass("starts-hidden") || !this.active)
                    return;

                if (forward) {
                    $t.hide();
                }
            }
        });
    }
    FutureHideQuestionRule.showQuestions = true;
    FutureHideQuestionRule.showOptions = false;
    FutureHideQuestionRule.prototype.isExclusive = false;
    FutureHideQuestionRule.prototype.isFuture = true;
    FutureHideQuestionRule.prototype.name = "FutureHideQuestionRule";

    function FutureShowOptionsRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,
            isFuture: true,

            init: function($survey, last_participation_data) {
                this.last_participation_data = last_participation_data;
            },

            activate: function($survey, $question, evt) {
                this.active = false;
                if (was_filled($survey, this.subjectQuestion, this.subjectOptions, this.last_participation_data))
                    this.active = true;
                return this.active;
            },

            apply: function($survey, target, forward) {
                var selectors = self.objectOptions.map(function(o){return '#option-'+o}).join(',');
                var $t = $survey.find(selectors);

                if (forward) {
                    $t.each(function() {
                        var $o = $(this);

                        if ($o.hasClass("starts-hidden")) {
                            enable_options($o.show().find('.choices > li'));
                        }
                    });
                }
            }
        });
    }
    FutureShowOptionsRule.showQuestions = true;
    FutureShowOptionsRule.showOptions = true;
    FutureShowOptionsRule.prototype.isExclusive = false;
    FutureShowOptionsRule.prototype.isFuture = true;
    FutureShowOptionsRule.prototype.name = "FutureShowOptionsRule";

    function FutureHideOptionsRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,
            isFuture: true,

            init: function($survey, last_participation_data) {
                this.last_participation_data = last_participation_data;
            },

            activate: function($survey, $question, evt) {
                this.active = false;
                if (was_filled($survey, this.subjectQuestion, this.subjectOptions, this.last_participation_data))
                    this.active = true;
                return this.active;
            },

            apply: function($survey, target, forward) {
                var selectors = self.objectOptions.map(function(o){return '#option-'+o}).join(',');
                var $t = $survey.find(selectors);

                if (forward) {
                    $t.each(function() {
                        var $o = $(this);

                        if (!$o.hasClass("starts-hidden")) {
                            $o.hide();
                        }
                    });
                }
            }
        });
    }
    FutureHideOptionsRule.showQuestions = true;
    FutureHideOptionsRule.showOptions = true;
    FutureHideOptionsRule.prototype.isExclusive = false;
    FutureHideOptionsRule.prototype.isFuture = true;
    FutureHideOptionsRule.prototype.name = "FutureHideOptionsRule";

    function FillRule(subjectQuestion, subjectOptions, objectQuestion, objectOptions, opts) {
        var self = this;

        // Public methods.

        $.extend(this, opts, {
            subjectQuestion: subjectQuestion,
            subjectOptions: subjectOptions,
            objectQuestion: objectQuestion,
            objectOptions: objectOptions,
            objectSignature: get_target_signature(objectQuestion, objectOptions),
            isExclusive: false,

            init: function($survey, last_participation_data) {
                self.last_participation_data = last_participation_data;
            },

            activate: function($survey, $question, evt) {
                var old = this.active;
                this.active = is_active($survey, $question, this);
                return this.active === true && old === false;
            },

            apply: function($survey, target, forward) {
                if (!this.active || $survey.is('.error'))
                    return;
                var object_names = get_question_data_names($survey, this.objectQuestion, this.objectOptions);
                $.each(object_names, function(i, object_name) {
                    var object_data = self.last_participation_data[object_name];
                    form_element_fill($survey.find('[name='+object_name+']'), object_data).trigger('change', { synthetic: true });
                });
            }
        });
    }
    FillRule.showQuestions = true;
    FillRule.showOptions = true;
    FillRule.prototype.isExclusive = false;
    FillRule.prototype.isFuture = false;
    FillRule.prototype.name = "FillRule";

    // MODULE INITIALIZATION

    window.wok.pollster.rules = {
        "ShowQuestion": ShowQuestionRule,
        "HideQuestion": HideQuestionRule,
        "ShowOptions": ShowOptionsRule,
        "HideOptions": HideOptionsRule,
        "CheckOptions": CheckOptionsRule,
        "UncheckOptions": UncheckOptionsRule,
        "Exclusive": ExclusiveRule,
        "Fill": FillRule,
        "FutureFill": FutureFillRule,
        "FutureShowQuestion": FutureShowQuestionRule,
        "FutureHideQuestion": FutureHideQuestionRule,
        "FutureShowOptions": FutureShowOptionsRule,
        "FutureHideOptions": FutureHideOptionsRule
    };

})(jQuery);
