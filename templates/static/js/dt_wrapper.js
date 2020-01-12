/*
 * Bep Marketplace ELE
 * Copyright (c) 2016-2020 Kolibri Solutions
 * License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
 */

/**
 * Created by Jeroen 2016-2018, Marketplaces ELE. Kolibri Solutions
 * General init script for all datatables, including copy and csv export.
 * make sure your table has the class ".datatable" for styling with metroui
 * make sure values in cells in HTML are not wrapped in spaces, or select2 will fail display. HTMLminify fixes this.
 * make sure table is wrapped in div.double-scroll to enable horizontal scrolling
 * use $('table.datatable').dt_wrapper(yadcf_filters)
 * It is not possible to filter columns with 'searchable:false' in datatables.
 * Make sure to include the following files:
 * * jquery.dataTables.yadcf.js
 * * jquery.dataTables.yadcf.css
 * * buttons.html5.min.js
 * * dataTables.buttons.min.js
 * * datatables.min.js
 * * jquery.datatables.yadcf.js
 * * jquery.doubleScroll.js (for horizontal scrolling on top of table.)
 * * select2.min.js
 * * select2.min.css or custom.css
 * Possibly add checkboxes to dropdown: https://github.com/wasikuss/select2-multi-checkboxes

 /**
 * @summary     DataTables
 * @file        dt_wrapper.js
 * @author      Jeroen van Oorschot, Kolibri Solutions
 * @contact     kolibrisolutions.nl
 * @copyright   Copyright 2016-2018 Kolibri Solutions
 * @license: MIT
 */

(function ($) {
    $.fn.dt_wrapper = function (yadcf_filters, cols) {
        var buttonCommon = {
            //function to strip the dropdowns of the headers, to not show the dropdown values in the csv/copy
            exportOptions: {
                format: {
                    //modifier for table headers export
                    header: function (data, row, column, node) {
                        // get the part of 'data' (the table header) up to the first "<" which is the html start tag.
                        var t = data.indexOf("<");
                        if (t !== -1) {
                            return data.substring(0, t);
                        } else {
                            return data;
                        }
                    },
                    // modifier for table body export, foreach cell.
                    body: function (data, row, column, node) {
                        // non empty cells
                        if (data) {
                            var t = $("<span />").html(data);
                            if (t[0].firstChild.nodeName === "UL") {
                                // if the table cell contains a list
                                //a list of values, get all li's and merge them
                                var txt = '';
                                t.children().children().each(function (d, j) {
                                    txt += (j.innerText.trim() + " + ");
                                });
                                return txt.slice(0, -3);
                            } else {
                                //normal text, make sure commas are removed.
                                return t.text().trim().replace(/;/g, ',');
                            }
                        } else {
                            // replace empty cells with a bar.
                            return '-';
                        }
                    }
                }
                // specify which columns to include for csv/copy export buttons.
                // https://datatables.net/extensions/buttons/examples/html5/columns.html
                // columns: exportColumns
            }
        };
        // https://datatables.net/extensions/buttons/examples/html5/outputFormat-function.html
        // the buttons to show above the table. Uses 'buttonCommon' to clean the copy/csv output.
        var buttons = [
            $.extend(true, {}, buttonCommon, {
                extend: 'copyHtml5',
                className: 'button'
            }),
            $.extend(true, {}, buttonCommon, {
                extend: 'csvHtml5',
                fieldSeparator: ';',
                className: 'button'
            }),
            $.extend(true, {}, buttonCommon, {
                extend: 'print',
                className: 'button'
            })];
        if (yadcf_filters) {  //reset filters button
            buttons.push(
                $.extend(true, {}, buttonCommon, {
                    text: 'Clear filters',
                    action: function (e, tdt, node, config) {
                        yadcf.exResetAllFilters(tdt);  //reset all datatable filters
                        tdt.state.clear();  //to clear saved state of datatables
                    },
                    className: 'button'
                })
            );
            //Default options for yadcf
            var yadcf_default_options = {
                filter_reset_button_text: false,  //yadcf clear button
            };
            var yadcf_select_options = {
                select_type: 'select2',
                select_type_options: {
                    minimumResultsForSearch: 6,
                    placeholder: 'Click to filter..',
                    allowClear: false, //select2 clear button takes too much space
                    width: '100%',
                }
            };
            //add default options to each column with a filter.
            for (var i = 0; i < yadcf_filters.length; i++) {
                $.extend(yadcf_filters[i], yadcf_default_options);
                if (yadcf_filters[i]['filter_type'] === 'select' || yadcf_filters[i]['filter_type'] === 'multi_select') {
                    $.extend(yadcf_filters[i], yadcf_select_options);
                }
            }
        }

        //make all datatable options:
        //Default options.
        var dt_default_options = {
            //default page length
            "pageLength": 100,
            //order for the dt items to appear
            "dom": 'Blfrtip',
            //responsive table layout
            "responsive": false,
            //custom buttons on top of the table
            "buttons": buttons,
            // function to store settings in localstorage
            "stateSave": true
        };

        if (cols){
            //custom column options, like disable search, or custom column ordering
            dt_default_options['columns'] = cols;
        }

        var dt = this.DataTable(dt_default_options);  // other options can be set via data-* attributes on the table.
        if (yadcf_filters) {
            yadcf.init(dt, yadcf_filters);
        }

        //Include these lines after dt init to have a scrollbar on top of the table for horizontal scrolling.
        //also wrap the table.datatable in a div.double-scroll
        var d = $('.double-scroll');
        if (d.length) {
            d.doubleScroll({
                'contentElement': 'table',
                'resetOnWindowResize': true
            });
        }
        return dt; //allows for storing dt globally
    }
}(jQuery));
