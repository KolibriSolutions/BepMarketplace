/**
 * Created by Jeroen 2016-2018, Marketplaces ELE. Kolibri Solutions
 * General init wrapper script for all datatables, including copy and csv export.
 * make sure your table has the class ".datatable"
 */

//global options, so this only works when only one .datatable on the page.
var options;    // datatable options. global to preserve on re-init (for responsive change).
var dt;         // used to dynamic update the datatable from local code.

/**
 * Function to transform all tables with class '.datatable' to a DataTable.
 * Features on top of default DataTables:
 * - Store/recall sorting/filtering settings in URL to share/bookmark a sorted table
 * - Dropdown selects in the table header, for any column supplied in dropdownColumns. (Append a <br /> after the header text)
 * - CSV/Copy buttons with datatables.buttons. Customize columns to export using exportColumns
 * - Export valid URLs to CSV/Copy by prepending the domain before exporting
 * - Add extra buttons with 'extraButtons'
 * - Responsive view for small screens
 * - Use with normal datatables-options using the customOptions argument
 * @param cols array of options for each column. At least a Null array with a null for each column.
 * @param dropdownColumns array of column indices. Each column index in this array gets a dropdown select.
 * @param exportColumns array of columns, or Column selector. Included columns are used for the export to csv/copy.
 * @param extraButtons extra buttons from DataTables.Buttons to include above the table.
 * @param customOptions custom DataTables options to extend the default options with.
 * @constructor
 */

var MPDataTable = function (cols, dropdownColumns, exportColumns, extraButtons, customOptions) {
    //definition of the buttons. All these buttons are overriden (removed) if customOptions['buttons'] is set.
    var buttonCommon = {
        //function to strip the dropdowns of the headers, to not show the dropdown values in the csv/copy
        exportOptions: {
            format: {
                //modifier for table headers export
                header: function (data, row, column, node) {
                    // get the part of 'data' (the table header) up to the first "<" which is the html start tag.
                    var i = data.indexOf("<");
                    if (i !== -1){
                        return data.substring(0, i);
                    }else{
                        return data;
                    }
                },
                // modifier for table body export, foreach cell.
                body: function (data, row, column, node) {
                    // non empty cells
                    if(data) {
                        //make a domain+URL from the hidden column with the url
                        if (cols[column] !== null && cols[column]["prependDomain"] === true) {
                            return window.location.origin + data;
                        } else {
                            // put the cell content to jquery object
                            var obj = $("<div />").html(data);
                            if (obj[0].firstChild.nodeName === "UL") {
                                // if the table cell contains a list
                                //a list of values, get all li's and merge them
                                var txt = '';
                                obj.children().children().each(function (d, j) {
                                    txt += (j.innerText.trim() + " + ");
                                });
                                return txt.slice(0, -3);
                            } else {
                                //normal text, make sure commas are removed.
                                return obj.text().trim().replace(/;/g, ',');
                            }
                        }
                    }else{
                        // replace empty cells with a bar.
                        return '-';
                    }
                }
            },
            // specify which columns to include for csv/copy export buttons.
            // https://datatables.net/extensions/buttons/examples/html5/columns.html
            columns: exportColumns
        }
    };
    // https://datatables.net/extensions/buttons/examples/html5/outputFormat-function.html
    // the buttons to show above the table. Uses 'buttonCommon' to clean the copy/csv output.
    var buttons = [
        //first button
        $.extend(true, {}, buttonCommon, {
            extend: 'copyHtml5'
        }),
        //second button
        $.extend(true, {}, buttonCommon, {
            extend: 'csvHtml5',
            fieldSeparator: ';'
        })
    ];
    //add the optional extrabuttons to the buttons.
    buttons.push(extraButtons);

    //Default options.
    options = {
        //default page length
        "pageLength": 100,
        //order for the dt items to appear
        "dom": 'Blfrtip',
        //responsive table layout
        "responsive": false,
        //custom buttons on top of the table
        "buttons": buttons,
        //function to store settings in uri
        "stateSave": true,
        "stateSaveCallback": function (settings, data) {
            //function to store sorting and filtering in the URI
            var store = {
                "s": data.start,   // start offset (for paging)
                "l": data.length,  // #entries on one page
                "f": encodeURIComponent(data.search.search), // global search/find
                "o": btoa(JSON.stringify(data.order[0]))     // column to order, asc or desc
            };
            var s, i;
            for (i = 0; i < dropdownColumns.length; i++) {  // selected dropdown for columns with dropdown.
                s = data.columns[dropdownColumns[i]].search.search;
                if (s !== '') {
                    store[dropdownColumns[i]] = encodeURIComponent(s.slice(1, -1));  //slice to strip the regex chars ^ and $
                }
            }
            //add the stored elements to the URL history
            window.history.pushState("", data.time, window.location.pathname + "?" + $.param(store));
        },
        //custom column options, like disable search
        "columns": cols,
        //function for the dropdown lists
        initComplete: function () {
            $(".dt-button").addClass("button"); //style the datatable button
            this.api().columns(dropdownColumns).every(function (currentValue) {
                var column = this;

                var id = "dt-select-dropdown-" + currentValue;
                // add a newline to the header, to put dropdowns below header text.
                if (column.header().children.length === 0) {
                    $('<br />').appendTo($(column.header()));
                }
                // add the dropdowns. Only add if header contains exactly one item ( the <br /> ); only add if not yet added (for reinitialization)
                if (column.header().children.length === 1) {
                    var select = $('<select id=' + id + '><option value=""></option></select>')
                        .appendTo($(column.header()));
                    //append the dropdowns, mark them selected if a stored value is applied to the selection
                    column.data().unique().sort().each(function (d, j) {
                        //only get the text inside the cell
                        d = $("<div />").html(d).text().trim();
                        if (column.search().replace(/\\/g, '') === '^' + d + '$') { //also match on backslash escaped chars
                            select.append('<option value="' + d + '" selected="selected">' + d + '</option>')
                        } else {
                            select.append('<option value="' + d + '">' + d + '</option>')
                        }
                    });
                }
                //Bind events
                $("#" + id).on('change', function () {
                    var val = $.fn.dataTable.util.escapeRegex(
                        $(this).val()
                    );
                    //the actual filter on change of the dropdown.
                    column
                        .search(val ? '^' + val + '$' : '', true, false)
                        .draw();
                });
            });
        }
    };

    //Extends the options that are passed in the argument. When conflicting, the options from the arguments are used.
    $.extend(options, customOptions);

    // executed on load of the page.
    // set custom sort options from url GET params, overrides previously set options.
    var i;
    options["searchCols"] = [];
    //make null array for the dropdowncolumns options
    for (i = 0; i < options.columns.length; i++) {
        options["searchCols"].push(null);
    }
    //GET strings, stored in URL.
    var vars = window.location.search.substring(1).split("&");
    var k, v, a;
    for (i = 0; i < vars.length; i++) {
        a = vars[i].split("=");
        k = a[0]; //key
        v = a[1]; //value
        if (v !== '') {
            v = decodeURIComponent(v);
            switch (k) {
                case 's':   //start offset
                    options['displayStart'] = v;
                    break;
                case 'l':   //length of page (#items)
                    options['pageLength'] = v;
                    break;
                case 'f':   //global search/find string
                    v = decodeURIComponent(v);  //The search string is twice URI encoded.
                    options['search'] = {'search': v};
                    break;
                case 'o':   //which column to order the table as base64 array
                    options['order'] = [JSON.parse(atob(v))];
                    break;
                default:    //custom column filters. Some checks to prevent injections
                    k = parseFloat(k); //k could be an index of a column to sort with a dropdown.
                    if (!isNaN(k) && isFinite(k)) {
                        if (dropdownColumns.indexOf(k) !== -1) { // only if the GET column is a column with dropdown.
                            v = "^" + decodeURIComponent(v) + "$"; //decode URI. searchstring is URI encoded twice.
                            options["searchCols"][k] = {'search': v, "regex": true, "smart": false};
                        }
                    }
                    break;
            }
        }
    }
    var table = $('.datatable');
    dt = table.DataTable(options); //global, because used outside this file.
    //do not sort the table when clicking a dropdown select.
    $("th>select").click(function () {
        return false;
    })
};