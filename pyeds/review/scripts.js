// Created by Martin Strohalm
// Adapted from the original script by Mike Hall (www.brainjar.com)

// for IE
if (document.ELEMENT_NODE == null) {
    document.ELEMENT_NODE = 1;
    document.TEXT_NODE = 3;
}

// sort table
function sortTable() {

    var tbodyEl, tmpEl;
    var colIdx, minIdx;
    var i, j;
    var minVal, testVal;
    var cmp;

    // get parent table body
    tbodyEl = this.parentNode.parentNode.parentNode.tBodies.item(0);

    // get column index
    colIdx = this.cellIndex;

    // init sorter
    if (tbodyEl.reverseSort == null) {
        tbodyEl.reverseSort = new Array();
    }

    // reverse sorting
    if (colIdx == tbodyEl.lastColumn) {
        tbodyEl.reverseSort[colIdx] = ! tbodyEl.reverseSort[colIdx];
    }

    // remember current column
    tbodyEl.lastColumn = colIdx;

    // sort table
    for (i = 0; i < tbodyEl.rows.length - 1; i++) {

        minIdx = i;
        minVal = getTextValue(tbodyEl.rows[i].cells[colIdx]);

        // walk in other rows
        for (j = i + 1; j < tbodyEl.rows.length; j++) {

            testVal = getTextValue(tbodyEl.rows[j].cells[colIdx]);
            cmp = compareValues(minVal, testVal);

            // reverse sorting
            if (tbodyEl.reverseSort[colIdx]) {
                cmp = -cmp;
            }

            // set new minimum
            if (cmp > 0) {
                minIdx = j;
                minVal = testVal;
            }
        }

        // move row before
        if (minIdx > i) {
          tmpEl = tbodyEl.removeChild(tbodyEl.rows[minIdx]);
          tbodyEl.insertBefore(tmpEl, tbodyEl.rows[i]);
        }
    }

    return false;
}

// get node text
function getTextValue(el) {

    var i;
    var s;

    // concatenate values of text nodes
    s = "";
    for (i = 0; i < el.childNodes.length; i++) {
        if (el.childNodes[i].nodeType == document.TEXT_NODE) {
            s += el.childNodes[i].nodeValue;
        } else if (el.childNodes[i].nodeType == document.ELEMENT_NODE && el.childNodes[i].tagName == "BR") {
            s += " ";
        } else {
            s += getTextValue(el.childNodes[i]);
        }
    }

    return s;
}

// compare values
function compareValues(v1, v2) {

    var f1, f2;

    // lowercase values
    v1 = v1.toLowerCase();
    v2 = v2.toLowerCase();

    // try to convert values to floats
    if (!isNaN(v1) && !isNaN(v1)) {
        v1 = parseFloat(v1);
        v2 = parseFloat(v2);
    }

    // compare values
    if (v1 == v2) {
        return 0;
    } else if (v1 > v2) {
        return 1;
    } else {
        return -1;
    }
}

// assign sorting to valid table headers
window.addEventListener('load', function () {

    var tableEls = document.getElementsByClassName('sortable');
    for (i = 0; i < tableEls.length; i++) {

        var theadEls = tableEls[i].getElementsByTagName('thead');
        var thEls = theadEls[0].getElementsByTagName('th');

        for (j = 0; j < thEls.length; j++) {
            thEls[j].addEventListener('click', sortTable);
        }
    }
});
