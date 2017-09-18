/**
 * Created by jeroen on 23-1-2017.
 * general function for all datatables, including copy and csv export.
 * make sure your table has the class ".datatable"
 * When using dropdowns in columheaders, append a <br /> to the header like: <th>NAME<br /></th>
 */

var options;
var dt;
var table;
var responsive = (window.innerWidth < 1000); //init value

var MPDataTable = function (cols, dropdownColumns) {
    //definition of the buttons
    var buttonCommon = {
        //function to strip the dropdowns of the headers, to not show the dropdown values in the csv/copy
        exportOptions: {
            format: {
                header: function (data, row, column, node) {
                    // get the part of 'data' (the table header) up to the first "<" which is the html start tag.
                    return data.substring(0, data.indexOf("<"));
                },
                body: function (data, row, column, node) {
                    //make a domain+URL from the hidden column with the url
                    if (cols[column] !== null && cols[column]["prependDomain"] === true) {
                        return window.location.origin + data;
                    } else {
                        var obj = $("<div />").html(data);
                        if (obj[0].firstChild.nodeName === "UL") {
                            //a list of values, get all li's and merge them
                            var txt = '';
                            obj.children().children().each(function (d, j) {
                                txt += (j.innerText.trim() + " + ");
                            });
                            return txt.slice(0, -3);
                        } else {
                            //normal text, make sure commas are removed.
                            return obj.text().trim();
                        }
                    }
                }
            }
        }
    };
    var buttons = ['copyHtml5','csvHtml5'];
    //make responsive enable/disable button on narrow screens.
    if (window.innerWidth < 1000) {
        buttons.push({
            "text": responsive ? "Disable responsive view" : "Enable responsive view",
            "action": function () {
                dt.destroy();
                responsive = !responsive;
                options.responsive = responsive;
                options.buttons[2].text = responsive ? "Disable responsive view" : "Enable responsive view";
                dt = table.DataTable(options);
                if (options.responsive) {
                    table.addClass("responsive");
                } else {
                    table.removeClass("responsive");
                }
            }
        })
    }
    //default options. Global var for other functions to modify them.
    options = {
        //default page length
        "pageLength": 100,
        //order for the dt items to appear
        "dom": 'Blfrtip',
        //responsive table layout
        "responsive": responsive,
        //custom buttons on top of the table
        "buttons": buttons,
        //function to store settings in uri
        "stateSave": true,
        "stateSaveCallback": function (settings, data) {
            //function to store sorting and filtering in the URI
            var store = {
                "s": data.start,   //offset
                "l": data.length,  //#entries
                "f": encodeURIComponent(data.search.search), //global search/find
                "o": btoa(JSON.stringify(data.order[0]))  //asc or desc order
            };
            var s, i;
            for (i = 0; i < dropdownColumns.length; i++) {
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
                //only add if not yet added (for reinitialization, and only add if header contains a <br /> tag
                var id = "dt-select-dropdown-" + currentValue;
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

    //executed on load of the page.
    //set custom sort options from url GET params
    var i;
    options["searchCols"] = [];
    //make null array for the dropdowncolumns options
    for (i = 0; i < options.columns.length; i++) {
        options["searchCols"].push(null);
    }
    var query = window.location.search.substring(1);
    var vars = query.split("&"); //GET strings.
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
                case 'o':   //order as base64 array
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
    table = $('.datatable');
    dt = table.DataTable(options);
    //do not sort the table when clicking a select.
    $("th>select").click(function () {
        return false;
    })
};