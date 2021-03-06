(function($) {

  /*
  READ FIRST


  This is where the derived value types are defined. Those that can be used to
  derive an extra data value from a question, when in the survey editor.

  This crappy code is full of copy paste. The juice should be squeezed out.

  Also, instead of sticking forks in your eyes while trying to find out how this
  whole thing work, here's an important bit of information:
  The relation between these derived values and the value types they apply to, is
  defined in the database. The table is: pollster_virtualoptiontype.

  */

    function TextRangeType(option, inf, sup, regex) {
        var self = this;

        $.extend(this, {
            option: option,
            match: function(val) {
                if (!inf && !sup)
                    return false;
                else if (!inf)
                    return val <= sup;
                else if (!sup)
                    return inf <= val;
                return inf <= val && val <= sup;
            }
        });
    }
    TextRangeType.isRange = true;
    TextRangeType.isRegularExpression = false;

    function NumericRangeType(option, inf, sup, regex) {
        var self = this;

        $.extend(this, {
            option: option,
            match: function(val) {
                val = parseFloat(val);
                inf = parseFloat(inf);
                sup = parseFloat(sup);
                if (isNaN(inf) && isNaN(sup))
                    return false;
                else if (isNaN(inf))
                    return val <= sup;
                else if (isNaN(sup))
                    return inf <= val;
                else
                    return inf <= val && val <= sup;
            }
        });
    }
    NumericRangeType.isRange = true;
    NumericRangeType.isRegularExpression = false;

    function DateRangeType(option, inf, sup, regex) {
        var self = this;

        $.extend(this, {
            option: option,
            match: function(val) {
                val = Date.parse(val);
                inf = Date.parse(inf);
                sup = Date.parse(sup);
                if (!inf && !sup)
                    return false;
                else if (!inf)
                    return val <= sup;
                else if (!sup)
                    return inf <= val;
                else
                    return inf <= val && val <= sup;
            }
        });
    }
    DateRangeType.isRange = true;
    DateRangeType.isRegularExpression = false;

    function DateYearsAgoType(option, inf, sup, regex) {
        var self = this;

        $.extend(this, {
            option: option,
            match: function(val) {
                val = Date.parse(val);
                inf = parseInt(inf);
                sup = parseInt(sup);

                if (!inf && !sup)
                    return false;
                else if (!inf)
                    return val <= new Date().addYears(-sup);
                else if (!sup)
                    return new Date().addYears(-inf) <= val;
                else
                    return new Date().addYears(-inf) <= val && val <= new Date().addYears(-sup);
            }
        });
    }
    DateYearsAgoType.isRange = true;
    DateYearsAgoType.isRegularExpression = false;


    function NumericYearsAgo(option, inf, sup, regex) {
        var self = this;
        $.extend(this, {
            option: option,
            match: function(val) {
                inf = parseInt(inf);
                sup = parseInt(sup);

                current_year = new Date().getFullYear();
                years_since_birth = current_year - val;

                if (!inf && !sup){
                  return false;
                }else if (!inf){
                  return  years_since_birth <= sup;
                }else if (!sup){
                  return years_since_birth >= inf;
                }
                return  years_since_birth >= inf && years_since_birth <= sup;
            }
        });
    }
    NumericYearsAgo.isRange = true;
    NumericYearsAgo.isRegularExpression = false;


    function YearMonthYearsAgoType(option, inf, sup, regex) {
        var self = this;


        $.extend(this, {
            option: option,
            match: function(val) {
            	val = Date.parse('1/'+val);

                inf = parseInt(inf);
                sup = parseInt(sup);

                var ret;
                if (!val)
                    ret = false;
                else if (!inf && !sup)
                    ret = false;
                else if (!inf)
                    ret = val <= new Date().addYears(-sup);
                else if (!sup)
                    ret = new Date().addYears(-inf) <= val;
                else
                    ret = new Date().addYears(-inf) <= val && val <= new Date().addYears(-sup);
                return ret;
            }
        });
    }
    YearMonthYearsAgoType.isRange = true;
    YearMonthYearsAgoType.isRegularExpression = false;

    function TimestampWeeksAgoType(option, inf, sup, regex) {
        var self = this;


        $.extend(this, {
            option: option,
            match: function(val) {
                val = Date.parse('1/'+val);
                inf = parseInt(inf);
                sup = parseInt(sup);
                if (!inf && !sup)
                    return false;
                else if (!inf)
                    return val <= new Date().addWeeks(-sup);
                else if (!sup)
                    return new Date().addWeeks(-inf) <= val;
                else
                    return new Date().addWeeks(-inf) <= val && val <= new Date().addWeeks(-sup);
            }
        });
    }
    TimestampWeeksAgoType.isRange = true;
    TimestampWeeksAgoType.isRegularExpression = false;

    function RegularExpressionType(option, inf, sup, regex) {
        var self = this;


        $.extend(this, {
            option: option,
            match: function(val) {
                return regex && new RegExp('^'+regex+'$').test(val);
            }
        });
    }
    RegularExpressionType.isRange = false;
    RegularExpressionType.isRegularExpression = true;

    // MODULE INITIALIZATION

    window.wok.pollster.virtualoptions = {
        "TextRange": TextRangeType,
        "NumericRange": NumericRangeType,
        "DateRange": DateRangeType,
        "RegularExpression": RegularExpressionType,
        "DateYearsAgo": DateYearsAgoType,
        "YearMonthYearsAgo": YearMonthYearsAgoType,
        "TimestampWeeksAgo": TimestampWeeksAgoType,
        "NumericYearsAgo": NumericYearsAgo
    };

})(jQuery);
