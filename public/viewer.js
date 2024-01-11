// Copyright 2022 The Google Research Authors.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * This file contains the JavaScript code for MQM Viewer.
 */

/**
 * Raw data read from the data file. Each entry is an array with 10 entries,
 * in this order (slightly different from the original order in the TSV data,
 * as we keep the fields in their more natural presentation order, as used in
 * the HTML table we display):
 *
 *     0: system, 1: doc, 2: docSegId, 3: globalSegId, 4: source, 5: target,
 *     6: rater, 7: category, 8: severity, 9: metadata
 *
 * The docSegId field is the 1-based index of the segment within the doc.
 *
 * The globalSegId field is an arbitrary, application-specific segment
 * identifier. If such an identifier is not needed or available, then set this
 * field to some constant value, such as 0.
 *
 * The last field, "metadata", is an object that includes the timestamp of
 * the rating, any note the rater may have left, and other metadata.
 *
 * There is a special severity, "HOTW-test", reserved for hands-on-the-wheel
 *   test results. These are test sentences in which a deliberate error is
 *   injected, just to help the rater stay on task. The test result is captured
 *   by category = "Found" or "Missed" and there is a note in the metadata that
 *   captures the injected error.
 */
let mqmData = [];

/**
 * mqmDataFiltered has exactly the same format as mqmData, except that it
 * is limited to the current filters in place.
 */
let mqmDataFiltered = [];

/** Array indices in each mqmData */
const MQM_DATA_SYSTEM = 0;
const MQM_DATA_DOC = 1;
const MQM_DATA_DOC_SEG_ID = 2;
const MQM_DATA_GLOBAL_SEG_ID = 3;
const MQM_DATA_SOURCE = 4;
const MQM_DATA_TARGET = 5;
const MQM_DATA_RATER = 6;
const MQM_DATA_CATEGORY = 7;
const MQM_DATA_SEVERITY = 8;
const MQM_DATA_METADATA = 9;
const MQM_DATA_NUM_PARTS = 10;

/**
 * If TSV data was supplied (instead of being chosen from a file), then it is
 * saved here (for possible downloading).
 */
let mqmTSVData = "";

/**
 * The following mqmStats* objects are all keyed by something from:
 * ({mqmTotal} or {system} or {rater}). Each keyed object is itself an object
 * mapping from doc and docSegId to an entry representing
 * the information for that segment. For instance, let `x` be the keyed
 * object, then `x["doc1"]["2"]` is the entry for the segment with
 * doc == "doc1" and docSegId == "2". Each entry for a segment is itself an
 * array, one entry per rater. Each entry for a rater is an object tracking
 * scores, errors, and their breakdowns.
 *
 * Each object is recomputed for any filtering applied to the data.
 */
let mqmStats = {};
let mqmStatsBySystem = {};
let mqmStatsByRater = {};
let mqmStatsBySystemRater = {};
let mqmStatsBySevCat = {};

/** Events timing info for current filtered data. **/
let mqmEvents = {};

/** Max number of segments to show. **/
let mqmLimit = 200;

/** Clause built by helper menus, for appending to the filter expression **/
let mqmClause = "";

/** UI elements for clause-builder. */
let mqmClauseKey;
let mqmClauseInclExcl;
let mqmClauseSev;
let mqmClauseCat;
let mqmClauseAddAnd;
let mqmClauseAddOr;

/** Selected system names for system-v-system comparison. */
let mqmSysVSys1;
let mqmSysVSys2;

/** A distinctive name used as the key for aggregate stats. */
const mqmTotal = "_MQM_TOTAL_";

/**
 * Bootstrap sampling is used to compute 95% confidence intervals.
 * Currently only system MQM scores are supported.
 * Samples are obtained incrementally, i.e., each `mqmShowCI` call samples
 * a given number of times until 1000 samples are collected.
 */
/** Total Number of document-level samples to collect. */
const mqmNumSamples = 1000;

/**
 * Number of document-level samples per `mqmShowCI` call.
 * Make sure that this number can divide `mqmNumSamples`.
 */
const mqmNumSamplesPerCall = 200;

/**
 * Document-level info used for bootstrap sampling.
 * This is keyed by the system name.
 */
let mqmDocs = {};

/**
 * Bootstrap samples already collected by previous calls.
 * This is keyed by the system name.
 */
let mqmSampledScores = {};

/**
 * This stores the return from `setTimeout` call for incrementally obtaining
 * bootstrap samples.
 */
let mqmCIComputation = null;

/**
 * Scoring weights. Each weight has a name and a regular expression pattern
 * for matching <severity>:<category>[/<subcategory>] (case-insensitively).
 * The weights are tried out in the sequence shown and for a given annotation,
 * the first matching weight is used. While you can interactively change these
 * for experimentation, you should set this default array to values suitable
 * for your application. The best place to do this is in your own version of
 * mqm-viewer.html.
 *
 * The "name" fields should be unique, short (<= 10 characters), and composed
 * only of [a-zA-Z.-].
 */
let mqmDefaultWeights = [
  {
    name: "AccCri",
    weight: 20,
    pattern: "critical:.*accuracy",
  },
  {
    name: "AccMaj",
    weight: 10,
    pattern: "major:.*accuracy",
  },
  {
    name: "AccMin",
    weight: 2,
    pattern: "minor:.*accuracy",
  },
  {
    name: "FluCri",
    weight: 10,
    pattern: "critical:.*fluency",
  },
  {
    name: "FluMaj",
    weight: 5,
    pattern: "major:.*fluency",
  },
  {
    name: "FluMin",
    weight: 1,
    pattern: "minor:.*fluency",
  },
  {
    name: "TerCri",
    weight: 15,
    pattern: "critical:.*terminology",
  },
  {
    name: "TerMaj",
    weight: 7.5,
    pattern: "major:.*terminology",
  },
  {
    name: "TerMin",
    weight: 1.5,
    pattern: "minor:.*terminology",
  },
  {
    name: "StyCri",
    weight: 5,
    pattern: "critical:.*style",
  },
  {
    name: "StyMaj",
    weight: 2.5,
    pattern: "major:.*style",
  },
  {
    name: "StyMin",
    weight: 0.5,
    pattern: "minor:.*style",
  },
];

/**
 * MQM Scores can be sliced along a second dimension, which is typically
 * Accuracy/Fluency, but can be customized in any desired manner. The
 * slicing is done by matching the pattern regular expressions
 * case-insensitively in order to find the first matching slice. Similarly
 * as with mqmDefaultWeights, you may want to override these defaults in
 * your own application.
 *
 * See comment above mqmDefaultWeights for requirements on the "name" field.
 */
let mqmDefaultSlices = [
  {
    name: "Accuracy",
    pattern: "accuracy",
  },
  {
    name: "Fluency",
    pattern: "fluency",
  },
  {
    name: "Terminology",
    pattern: "terminology",
  },
  {
    name: "Style",
    pattern: "style",
  },
];

/**
 * mqmWeights and mqmSlices are set from current settings in
 * mqmParseScoreSettings() and mqmResetSettings().
 */
let mqmWeights = [];
let mqmSlices = [];

/**
 * Score aggregates include 'weighted-" and "slice-" prefixed scores. The names
 * beyond the prefixes are taken from the "name" field in mqmWeights and
 * mqmSlices.
 */
const MQM_SCORE_WEIGHTED_PREFIX = "weighted-";
const MQM_SCORE_SLICE_PREFIX = "slice-";

/**
 * Arrays of names of currently being displayed score components, sorted in
 * decreasing score order.
 */
let mqmScoreWeightedFields = [];
let mqmScoreSliceFields = [];

/**
 * Scoring unit. If false, segments are used for scoring. If true, scores
 * are computed per "100 source characters".
 */
let mqmCharScoring = false;

/**
 * The field and header ID to sort the score table rows by. By default, sort by
 * overall MQM score. `mqmSortReverse` indicates whether it is sorted in
 * ascending order (false, default) or descending order (true).
 */
let mqmSortByField = "score";
let mqmSortByHeaderId = "mqm-score-th";
let mqmSortReverse = false;

/**
 * Listener for changes to the input field that specifies the limit on
 * the number of rows shown.
 */
function setMqmLimit() {
  const limitElt = document.getElementById("mqm-limit");
  const limit = limitElt.value.trim();
  if (limit > 0) {
    mqmLimit = limit;
    mqmShow();
  } else {
    limitElt.value = mqmLimit;
  }
}

/**
 * This function returns an integer if s is an integer, otherwise returns s.
 * @param {string} s
 * @return {number|string}
 */
function mqmMaybeParseInt(s) {
  const temp = parseInt(s);
  if (!isNaN(temp) && "" + temp == s) {
    return temp;
  }
  return s;
}

/**
 * This sorts 10-column MQM data by fields in the order globalSegId, doc,
 *     docSegId, system, rater, severity, category.
 * @param {!Array<!Array>} data The MQM-10-column data to be sorted.
 */
function mqmSortData(data) {
  data.sort((e1, e2) => {
    let diff = 0;
    /** globalSegId/docSegId can be non-numeric */
    const globalSegId1 = mqmMaybeParseInt(e1[MQM_DATA_GLOBAL_SEG_ID]);
    const globalSegId2 = mqmMaybeParseInt(e2[MQM_DATA_GLOBAL_SEG_ID]);
    const docSegId1 = mqmMaybeParseInt(e1[MQM_DATA_DOC_SEG_ID]);
    const docSegId2 = mqmMaybeParseInt(e2[MQM_DATA_DOC_SEG_ID]);
    if (globalSegId1 < globalSegId2) {
      diff = -1;
    } else if (globalSegId1 > globalSegId2) {
      diff = 1;
    } else if (e1[MQM_DATA_DOC] < e2[MQM_DATA_DOC]) {
      diff = -1;
    } else if (e1[MQM_DATA_DOC] > e2[MQM_DATA_DOC]) {
      diff = 1;
    } else if (docSegId1 < docSegId2) {
      diff = -1;
    } else if (docSegId1 > docSegId2) {
      diff = 1;
    } else if (e1[MQM_DATA_SYSTEM] < e2[MQM_DATA_SYSTEM]) {
      diff = -1;
    } else if (e1[MQM_DATA_SYSTEM] > e2[MQM_DATA_SYSTEM]) {
      diff = 1;
    } else if (e1[MQM_DATA_RATER] < e2[MQM_DATA_RATER]) {
      diff = -1;
    } else if (e1[MQM_DATA_RATER] > e2[MQM_DATA_RATER]) {
      diff = 1;
    } else if (e1[MQM_DATA_SEVERITY] < e2[MQM_DATA_SEVERITY]) {
      diff = -1;
    } else if (e1[MQM_DATA_SEVERITY] > e2[MQM_DATA_SEVERITY]) {
      diff = 1;
    } else if (e1[MQM_DATA_CATEGORY] < e2[MQM_DATA_CATEGORY]) {
      diff = -1;
    } else if (e1[MQM_DATA_CATEGORY] > e2[MQM_DATA_CATEGORY]) {
      diff = 1;
    }
    return diff;
  });
}

/**
 * If obj does not have an array property named key, creates an empty array.
 * Pushes val into the obj[key] array.
 * @param {!Object} obj
 * @param {string} key
 * @param {string} val
 */
function mqmAddToArray(obj, key, val) {
  if (!obj.hasOwnProperty(key)) obj[key] = [];
  obj[key].push(val);
}

/**
 * Aggregates mqmData, collecting all data for a particular segment translation
 *     (i.e., for a given (doc, docSegId, globalSegId) triple) into a
 *     "segment" object that has the following properties:
 *         {cats,sevs,sevcats}By{Rater,System}.
 *     Each of these properties is an object keyed by system or rater, with the
 *     values being arrays of strings that are categories, severities,
 *     and <sev>[/<cat>], * respectively.
 *
 * Appends each aggregated segment object as the last column (index 10) to each
 *     mqmData[*] array for that segment.
 */
function mqmAddSegmentAggregations() {
  let segment = null;
  let currDoc = "";
  let currDocSegId = -1;
  let currGlobalSegId = -1;
  let currStart = -1;
  for (let i = 0; i < mqmData.length; i++) {
    const parts = mqmData[i];
    const system = parts[MQM_DATA_SYSTEM];
    const doc = parts[MQM_DATA_DOC];
    const docSegId = parts[MQM_DATA_DOC_SEG_ID];
    const globalSegId = parts[MQM_DATA_GLOBAL_SEG_ID];
    const rater = parts[MQM_DATA_RATER];
    const category = parts[MQM_DATA_CATEGORY];
    const severity = parts[MQM_DATA_SEVERITY];
    if (
      currDoc == doc &&
      currDocSegId == docSegId &&
      currGlobalSegId == globalSegId
    ) {
      console.assert(segment != null, i);
    } else {
      if (segment != null) {
        console.assert(currStart >= 0, segment);
        for (let j = currStart; j < i; j++) {
          mqmData[j].push(segment);
        }
      }
      segment = {
        catsBySystem: {},
        catsByRater: {},
        sevsBySystem: {},
        sevsByRater: {},
        sevcatsBySystem: {},
        sevcatsByRater: {},
      };
      currDoc = doc;
      currDocSegId = docSegId;
      currGlobalSegId = globalSegId;
      currStart = i;
    }
    mqmAddToArray(segment.catsBySystem, system, category);
    mqmAddToArray(segment.catsByRater, rater, category);
    mqmAddToArray(segment.sevsBySystem, system, severity);
    mqmAddToArray(segment.sevsByRater, rater, severity);
    const sevcat = severity + (category ? "/" + category : "");
    mqmAddToArray(segment.sevcatsBySystem, system, sevcat);
    mqmAddToArray(segment.sevcatsByRater, rater, sevcat);
  }
  if (segment != null) {
    console.assert(currStart >= 0, segment);
    for (let j = currStart; j < mqmData.length; j++) {
      mqmData[j].push(segment);
    }
  }
}

/**
 * Returns an array of column filter REs.
 * @return {!Array<!RegExp>}
 */
function mqmGetFilterREs() {
  const res = [];
  const filters = document.getElementsByClassName("mqm-filter-re");
  for (let i = 0; i < filters.length; i++) {
    const filter = filters[i].value.trim();
    const selectId = filters[i].id.replace(/filter/, "select");
    const sel = document.getElementById(selectId);
    if (sel) sel.value = filter;
    if (!filter) {
      res.push(null);
      continue;
    }
    const re = new RegExp(filter);
    res.push(re);
  }
  return res;
}

/**
 * Retains only the marked part in a segment, replacing the parts before/after
 *     (if they exist) with ellipsis. Used to show just the marked parts for
 *     source/target text segments when the full text has already been shown
 *     previously.
 * @param {string} s
 * @return {string}
 */
function mqmOnlyKeepSpans(s) {
  const start = s.indexOf("<span");
  const end = s.lastIndexOf("</span>");
  if (start >= 0 && end >= 0) {
    let sub = s.substring(start, end + 7);
    const MAX_CTX = 10;
    if (start > 0) {
      const ctx = Math.min(MAX_CTX, start);
      sub = s.substr(start - ctx, ctx) + sub;
      if (ctx < start) sub = "&hellip;" + sub;
    }
    if (end + 7 < s.length) {
      const ctx = Math.min(MAX_CTX, s.length - (end + 7));
      sub = sub + s.substr(end + 7, ctx);
      if (end + 7 + ctx < s.length) sub = sub + "&hellip;";
    }
    return sub;
  } else {
    return "&hellip;";
  }
}

/**
 * Short-cut function (convenient in filter expressions) for:
 *     "obj has array property prop that includes val"
 * @param {!Object} obj
 * @param {string} prop
 * @param {string} val
 * @return {boolean}
 */
function mqmIncl(obj, prop, val) {
  return obj.hasOwnProperty(prop) && obj[prop].includes(val);
}

/**
 * Short-cut function (convenient in filter expressions) for:
 *     "obj has array property prop that excludes val"
 * @param {!Object} obj
 * @param {string} prop
 * @param {string} val
 * @return {boolean}
 */
function mqmExcl(obj, prop, val) {
  return obj.hasOwnProperty(prop) && !obj[prop].includes(val);
}

/**
 * Clears mqmClause and disables associated buttons.
 */
function mqmClearClause() {
  mqmClause = "";
  mqmClauseKey.value = "";
  mqmClauseInclExcl.value = "includes";
  mqmClauseSev.value = "";
  mqmClauseCat.value = "";
  mqmClauseAddAnd.disabled = true;
  mqmClauseAddOr.disabled = true;
}

/**
 * Checks if filter expression clause is fully specified, enables "add"
 *     buttons if so.
 */
function mqmCheckClause() {
  mqmClause = "";
  mqmClauseAddAnd.disabled = true;
  mqmClauseAddOr.disabled = true;
  if (!mqmClauseKey.value) return;
  if (!mqmClauseSev.value && !mqmClauseCat.value) return;

  let sevcats = "segment.sevcats";
  let key = "";
  let err = mqmClauseSev.value + "/" + mqmClauseCat.value;
  if (!mqmClauseSev.value) {
    sevcats = "segment.cats";
    err = mqmClauseCat.value;
  }
  if (!mqmClauseCat.value) {
    sevcats = "segment.sevs";
    err = mqmClauseSev.value;
  }
  if (mqmClauseKey.value.startsWith("System: ")) {
    sevcats += "BySystem";
    key = mqmClauseKey.value.substr(8);
  } else {
    console.assert(
      mqmClauseKey.value.startsWith("Rater: "),
      mqmClauseKey.value,
    );
    sevcats += "ByRater";
    key = mqmClauseKey.value.substr(7);
  }
  const inclexcl =
    mqmClauseInclExcl.value == "excludes" ? "mqmExcl" : "mqmIncl";
  mqmClause = `${inclexcl}(${sevcats}, "${key}", "${err}")`;
  mqmClauseAddAnd.disabled = false;
  mqmClauseAddOr.disabled = false;
}

/**
 * Adds mqmClause with and/or to the filter expression.
 * @param {string} andor
 */
function mqmAddClause(andor) {
  if (!mqmClause) return;
  const elt = document.getElementById("mqm-filter-expr");
  let expr = elt.value.trim();
  if (expr) expr += " " + andor + " ";
  expr += mqmClause;
  elt.value = expr;
  mqmClearClause();
  mqmShow();
}

/**
 * Evaluates the JavaScript filterExpr on an mqmData[] row and returns true
 *     only if the filter passes.
 * @param {string} filterExpr
 * @param {!Array<string>} parts
 * @return {boolean}
 */
function mqmFilterExprPasses(filterExpr, parts) {
  if (!filterExpr.trim()) return true;
  try {
    return Function(
      '"use strict";' +
        `
     const system = arguments[MQM_DATA_SYSTEM];
     const doc = arguments[MQM_DATA_DOC];
     const docSegId = arguments[MQM_DATA_DOC_SEG_ID];
     const globalSegId = arguments[MQM_DATA_GLOBAL_SEG_ID];
     const source = arguments[MQM_DATA_SOURCE];
     const target = arguments[MQM_DATA_TARGET];
     const rater = arguments[MQM_DATA_RATER];
     const category = arguments[MQM_DATA_CATEGORY];
     const severity = arguments[MQM_DATA_SEVERITY];
     const metadata = arguments[MQM_DATA_METADATA];
     const segment = arguments[MQM_DATA_NUM_PARTS];` +
        "return (" +
        filterExpr +
        ")",
    )(
      parts[MQM_DATA_SYSTEM],
      parts[MQM_DATA_DOC],
      parts[MQM_DATA_DOC_SEG_ID],
      parts[MQM_DATA_GLOBAL_SEG_ID],
      parts[MQM_DATA_SOURCE],
      parts[MQM_DATA_TARGET],
      parts[MQM_DATA_RATER],
      parts[MQM_DATA_CATEGORY],
      parts[MQM_DATA_SEVERITY],
      parts[MQM_DATA_METADATA],
      parts[MQM_DATA_NUM_PARTS],
    );
  } catch (err) {
    document.getElementById("mqm-filter-expr-error").innerHTML = err;
    return false;
  }
}

/**
 * In the weights/slices settings table with the given element id, add a row.
 * @param {string} id
 * @param {number} cols The number of columns to use.
 */
function mqmSettingsAddRow(id, cols) {
  let html = "<tr>";
  for (let i = 0; i < cols; i++) {
    html += `
         <td><span contenteditable="true"
                  class="mqm-settings-editable"></span></td>`;
  }
  html += "</tr>";
  const elt = document.getElementById(id);
  const rowNum = document.getElementById(id + "-add-row").value ?? 1;
  /** The new row needs to be the 1-based position "rowNum" */
  const rows = elt.getElementsByTagName("tr");
  if (rows.length == 0 || rowNum <= 1) {
    elt.insertAdjacentHTML("afterbegin", html);
  } else {
    if (rowNum > rows.length) {
      rows[rows.length - 1].insertAdjacentHTML("afterend", html);
    } else {
      rows[rowNum - 1].insertAdjacentHTML("beforebegin", html);
    }
  }
}

/**
 * Displays settings tables for score weights and slices.
 */
function mqmSetUpScoreSettings() {
  const weightSettings = document.getElementById("mqm-settings-weights");
  weightSettings.innerHTML = "";
  for (let sc of mqmWeights) {
    sc.regex = new RegExp(sc.pattern, "i");
    weightSettings.insertAdjacentHTML(
      "beforeend",
      `
         <tr>
           <td><span contenteditable="true"
                    class="mqm-settings-editable">${sc.name}</span></td>
           <td><span contenteditable="true"
                    class="mqm-settings-editable">${sc.pattern}</span></td>
           <td><span contenteditable="true"
                    class="mqm-settings-editable">${sc.weight}</span></td>
         </tr>`,
    );
  }
  const sliceSettings = document.getElementById("mqm-settings-slices");
  sliceSettings.innerHTML = "";
  for (let sc of mqmSlices) {
    sc.regex = new RegExp(sc.pattern, "i");
    sliceSettings.insertAdjacentHTML(
      "beforeend",
      `
         <tr>
           <td><span contenteditable="true"
                    class="mqm-settings-editable">${sc.name}</span></td>
           <td><span contenteditable="true"
                    class="mqm-settings-editable">${sc.pattern}</span></td>
         </tr>`,
    );
  }
}

/**
 * Parses score weights/slices from the user-edited table identified by id.
 * If there are errors in parsing then they are displayed to the user in the
 * mqm-errors element and null is returned.
 * @param {string} id
 * @param {boolean} hasWeight True if this is the weights table.
 * @return {?Array<!Object>} Array of parsed weights/slices, or null if errors.
 */
function mqmParseScoreSettingsInner(id, hasWeight) {
  const nameChecker = new RegExp(/^[a-z0-9\.-]+$/i);
  const errorsFound = [];
  const rows = document.getElementById(id).getElementsByTagName("tr");
  const parsed = [];
  const names = {};
  for (let i = 0; i < rows.length; i++) {
    if (!rows[i].textContent.trim()) {
      /* Allow skipping blank lines */
      continue;
    }
    const parsedRow = {};
    const spans = rows[i].getElementsByTagName("span");
    console.assert(spans.length == 2 + (hasWeight ? 1 : 0), spans);
    parsedRow.name = spans[0].textContent.trim();
    if (!nameChecker.test(parsedRow.name)) {
      errorsFound.push(
        "The name [" +
          parsedRow.name +
          "] cannot be empty, must use characters [a-zA-Z0-9.-]",
      );
      continue;
    }
    if (names[parsedRow.name]) {
      errorsFound.push("The name [" + parsedRow.name + "] is a duplicate");
      continue;
    }
    parsedRow.pattern = spans[1].textContent.trim();
    try {
      parsedRow.regex = new RegExp(parsedRow.pattern, "i");
    } catch (err) {
      console.log(err);
      parsedRow.pattern = "";
    }
    if (!parsedRow.pattern) {
      errorsFound.push(
        "The pattern in row [" + parsedRow.name + "] is empty/invalid",
      );
      continue;
    }
    if (hasWeight) {
      parsedRow.weight = parseFloat(spans[2].textContent.trim());
      if (isNaN(parsedRow.weight) || parsedRow.weight < 0) {
        errorsFound.push(
          "The weight in row [" + parsedRow.name + "] is invalid",
        );
        continue;
      }
    }
    /* All good! */
    names[parsedRow.name] = true;
    parsed.push(parsedRow);
  }
  const errorsElt = document.getElementById("mqm-errors");
  for (let error of errorsFound) {
    errorsElt.insertAdjacentHTML("beforeend", `<div>${error}</div>\n`);
  }
  return errorsFound.length == 0 ? parsed : null;
}

/**
 * Parses score weights and slices from the user-edited settings tables. Sets
 * mqmWeights and mqmSlices if successful.
 * @return {boolean} True if the parsing was successful.
 */
function mqmParseScoreSettings() {
  const errors = document.getElementById("mqm-errors");
  errors.innerHTML = "";
  const newWeights = mqmParseScoreSettingsInner("mqm-settings-weights", true);
  const newSlices = mqmParseScoreSettingsInner("mqm-settings-slices", false);
  if (!newWeights || !newSlices) {
    return false;
  }
  mqmWeights = newWeights;
  mqmSlices = newSlices;
  return true;
}

/**
 * This checks if the annotation matches the pattern in the score weight/slice
 * component.
 * @param {!Object} sc Score component, with a regex property.
 * @param {string} sev Severity of the annotation.
 * @param {string} cat Category (and optional "/" + subcat.) of the annotation.
 * @return {boolean}
 */
function mqmMatchesScoreSplit(sc, sev, cat) {
  return sc.regex.test(sev + ":" + cat);
}

/**
 * Initializes and returns a rater stats object.
 * @param {string} rater
 * @return {!Object}
 */
function mqmInitRaterStats(rater) {
  return {
    rater: rater,
    score: 0,

    errorSpans: 0,
    numWithErrors: 0,

    hotwFound: 0,
    hotwMissed: 0,
  };
}

/**
 * Creates the key for a score weighted component or slices.
 * @param {string} name
 * @param {boolean=} isSlice
 * @return {string}
 */
function mqmScoreKey(name, isSlice = false) {
  return (isSlice ? MQM_SCORE_SLICE_PREFIX : MQM_SCORE_WEIGHTED_PREFIX) + name;
}

/**
 * Strips the prefix from a key for a score component (previously assembled by
 * mqmScoreKey).
 * @param {string} key
 * @return {string}
 */
function mqmScoreKeyToName(key) {
  if (key.startsWith(MQM_SCORE_WEIGHTED_PREFIX)) {
    return key.substr(MQM_SCORE_WEIGHTED_PREFIX.length);
  } else if (key.startsWith(MQM_SCORE_SLICE_PREFIX)) {
    return key.substr(MQM_SCORE_SLICE_PREFIX.length);
  }
  return key;
}

/**
 * Appends stats from delta into raterStats.
 * @param {!Object} raterStats
 * @param {!Object} delta
 */
function mqmAddRaterStats(raterStats, delta) {
  raterStats.score += delta.score;
  for (sc of mqmWeights) {
    const key = mqmScoreKey(sc.name);
    if (delta[key]) {
      raterStats[key] = (raterStats[key] ?? 0) + delta[key];
    }
  }
  for (sc of mqmSlices) {
    const key = mqmScoreKey(sc.name, true);
    if (delta[key]) {
      raterStats[key] = (raterStats[key] ?? 0) + delta[key];
    }
  }
  raterStats.errorSpans += delta.errorSpans;
  raterStats.numWithErrors += delta.numWithErrors;
  raterStats.hotwFound += delta.hotwFound;
  raterStats.hotwMissed += delta.hotwMissed;
}

/**
 * Divides all metrics in raterStats by num.
 * @param {!Object} raterStats
 * @param {number} num
 */
function mqmAvgRaterStats(raterStats, num) {
  if (!num) return;
  raterStats.score /= num;
  for (sc of mqmWeights) {
    const key = mqmScoreKey(sc.name);
    if (raterStats[key]) {
      raterStats[key] /= num;
    }
  }
  for (sc of mqmSlices) {
    const key = mqmScoreKey(sc.name, true);
    if (raterStats[key]) {
      raterStats[key] /= num;
    }
  }
}

/**
 * Aggregates segment stats. This returns an object that has aggregate scores
 *     and these additional properties:
 *       numSegments
 *       numSrcChars
 *       numScoringUnits
 *       numRatings
 * @param {!Array} segs
 * @return {!Object}
 */
function mqmAggregateSegStats(segs) {
  const aggregates = mqmInitRaterStats("");
  if (!segs || !segs.length) {
    aggregates.score = Infinity;
    aggregates.numSegments = 0;
    aggregates.numSrcChars = 0;
    aggregates.numScoringUnits = 0;
    aggregates.numRatings = 0;
    return aggregates;
  }
  let totalSrcLen = 0;
  let ratings = 0;
  for (let raterStats of segs) {
    totalSrcLen += raterStats.srcLen;
    const allRaterStats = mqmInitRaterStats("");
    for (let r of raterStats) {
      mqmAddRaterStats(allRaterStats, r);
    }
    mqmAvgRaterStats(allRaterStats, raterStats.length);
    ratings += raterStats.length;
    mqmAddRaterStats(aggregates, allRaterStats);
  }
  aggregates.numSegments = segs.length;
  aggregates.numSrcChars = totalSrcLen;
  aggregates.numScoringUnits = mqmCharScoring
    ? aggregates.numSrcChars / 100
    : aggregates.numSegments;
  mqmAvgRaterStats(aggregates, aggregates.numScoringUnits);
  aggregates.numRatings = ratings;
  return aggregates;
}

/**
 * Samples from [0, max) for a specified number of times.
 * @param {number} max
 * @param {number} size
 * @return {!Array}
 */
function getRandomInt(max, size) {
  let samples = [];
  for (let i = 0; i < size; i++) {
    samples.push(Math.floor(Math.random() * max));
  }
  return samples;
}

/**
 * Prepare the document-level info prior to sampling.
 * For each document, we only need to keep track of two stats:
 * 1. The total number of segments in the document;
 * 2. The MQM scores (averaged over the number of segments).
 * These two stats are later used to compute a weighted average of MQM scores
 * to take into account the different total number of segments when we use
 * document-level sampling.
 * The input `statsBySystem` is an mqmStats* object keyed by the system name.
 * @param {!Object} statsBySystem
 */
function mqmPrepareDocScores(statsBySystem) {
  mqmDocs = {};
  for (system of Object.keys(statsBySystem)) {
    mqmDocs[system] = [];
    for (let doc of Object.values(statsBySystem[system])) {
      const segsInDoc = Object.values(doc);
      const a = mqmAggregateSegStats(segsInDoc);
      mqmDocs[system].push({
        score: a.score,
        numScoringUnits: a.numScoringUnits,
      });
    }
  }
}

/**
 * Implements the core logic to incrementally obtain bootstrap samples and
 * show confidence intervals. Each call will obtain `mqmNumberSamplesPerCall`
 * document-level samples. At the end of the call, CIs are shown if all samples
 * have been collected. Otherwise, call again to collect more.
 * The input `systems` is a (sorted) array of system names, in the same order
 * as rendered in HTML.
 * @param {!Array} systems
 */
function mqmShowCI(systems) {
  if (systems.length == 0) {
    mqmClearCIComputation();
    return;
  }
  for (system of systems) {
    if (!mqmSampledScores.hasOwnProperty(system)) {
      mqmSampledScores[system] = [];
    }
    const docs = mqmDocs[system];
    for (let i = 0; i < mqmNumSamplesPerCall; i++) {
      let indices = getRandomInt(docs.length, docs.length);
      let score = 0.0;
      let numScoringUnits = 0;
      for (let index of indices) {
        let doc = docs[index];
        score += doc["score"] * doc["numScoringUnits"];
        numScoringUnits += doc["numScoringUnits"];
      }
      mqmSampledScores[system].push(score / numScoringUnits);
    }
  }

  if (Object.values(mqmSampledScores)[0].length < mqmNumSamples) {
    // We need to collect more samples.
    mqmCIComputation = setTimeout(mqmShowCI, 200, systems);
  } else {
    // We can now show the confidence intervals.
    const lowerIdx = mqmNumSamples / 40;
    const upperIdx = mqmNumSamples - lowerIdx - 1;
    for (let [rowIdx, system] of systems.entries()) {
      mqmSampledScores[system].sort((a, b) => a - b);
      const lb = mqmSampledScores[system][lowerIdx];
      const ub = mqmSampledScores[system][upperIdx];
      const ci = `${lb.toFixed(3)} - ${ub.toFixed(3)}`;
      const spanId = `mqm-ci-${rowIdx}`;
      const ciSpan = document.getElementById(spanId);
      if (ciSpan) {
        ciSpan.innerHTML = ` (${ci})`;
      }
    }
    mqmClearCIComputation();
  }
}

/**
 * Clears all computed confidence interval-related information.
 */
function mqmClearCIComputation() {
  mqmCIComputation = null;
  mqmDocs = {};
  mqmSampledScores = {};
}

/**
 * Shows the table header for the MQM scores table. The score weighted
 * components and slices to display should be available in
 * mqmScoreWeightedFields and mqmScoreSliceFields.
 */
function mqmShowScoresHeader() {
  const mqmHelpText =
    `MQM score. When there are at least 5 documents after ` +
    `filtering, 95% confidence intervals for each system are also shown. ` +
    `Confidence intervals are estimated through bootstrap sampling ` +
    `for 1000 times on the document level. ` +
    `If there are less than 5 documents, N/A is shown instead.`;
  const mqmScoreWithCI =
    '<span id="mqm-score-heading">MQM Score' +
    '<sup class="mqm-help-icon">?</sup>' +
    "</span>";
  const header = document.getElementById("mqm-stats-thead");
  let html = `
       <tr>
         <th></th>
         <th title="Number of source characters">
           <b>#Characters</b>
         </th>
         <th title="Number of segments"><b>#Segments</b></th>
         <th title="Number of segment ratings"><b>#Ratings</b></th>
         <th id="mqm-score-th" title="${mqmHelpText}">${mqmScoreWithCI}</th>`;
  const scoreFields = mqmScoreWeightedFields
    .map((x) => MQM_SCORE_WEIGHTED_PREFIX + x)
    .concat(mqmScoreSliceFields.map((x) => MQM_SCORE_SLICE_PREFIX + x));
  for (let i = 0; i < scoreFields.length; i++) {
    const scoreKey = scoreFields[i];
    const scoreName = mqmScoreKeyToName(scoreKey);
    const partType = i < mqmScoreWeightedFields.length ? "weighted" : "slice";
    const cls = "mqm-stats-" + partType;
    const tooltip = "Score part: " + scoreName + "-" + partType;
    html += `
         <th id="mqm-${scoreKey}-th" class="mqm-score-th ${cls}"
             title="${tooltip}">
           <b>${scoreName}</b>
         </th>`;
  }
  html += `
         <th title="Average length of error span"><b>Error Span</b></th>
       </tr>`;
  header.innerHTML = html;

  /** Make columns clickable for sorting purposes. */

  const upArrow = '<span class="mqm-arrow mqm-arrow-up">&#129041;</span>';
  const downArrow = '<span class="mqm-arrow mqm-arrow-down">&#129043;</span>';
  for (const field of ["score"].concat(scoreFields)) {
    const headerId = `mqm-${field}-th`;
    const th = document.getElementById(headerId);
    th.insertAdjacentHTML("beforeend", ` ${upArrow}${downArrow}`);
    th.addEventListener("click", (e) => {
      // Click again for reversing order. Otherwise sort in ascending order.
      if (field == mqmSortByField) {
        mqmSortReverse = !mqmSortReverse;
      } else {
        mqmSortReverse = false;
      }
      mqmSortByField = field;
      mqmSortByHeaderId = headerId;
      mqmShow();
    });
  }
  mqmShowSortArrow();
}

/**
 * Appends MQM score details from the stats object to the table with the given
 * id.
 * @param {string} id
 * @param {string} title
 * @param {!Object} stats
 * @param {?Object=} aggregates
 */
function mqmShowScores(id, title, stats, aggregates = null) {
  const tbody = document.getElementById(id);
  if (title) {
    tbody.insertAdjacentHTML(
      "beforeend",
      '<tr><td colspan="15"><hr></td></tr>' +
        `<tr><td colspan="15"><b>${title}</b></td></tr>\n`,
    );
  }
  const keys = Object.keys(stats);
  if (!aggregates) {
    aggregates = {};
    for (let k of keys) {
      const segs = mqmGetSegStatsAsArray(stats[k]);
      aggregates[k] = mqmAggregateSegStats(segs);
    }
  }
  keys.sort(
    (k1, k2) =>
      (aggregates[k1][mqmSortByField] ?? 0) - aggregates[k2][mqmSortByField] ??
      0,
  );
  if (mqmSortReverse) {
    keys.reverse();
  }
  const scoreFields = ["score"]
    .concat(mqmScoreWeightedFields.map((x) => MQM_SCORE_WEIGHTED_PREFIX + x))
    .concat(mqmScoreSliceFields.map((x) => MQM_SCORE_SLICE_PREFIX + x));
  for (let [rowIdx, k] of keys.entries()) {
    const kDisp = k == mqmTotal ? "Total" : k;
    let rowHTML =
      `<tr><td>${kDisp}</td>` +
      `<td>${aggregates[k].numSrcChars}</td>` +
      `<td>${aggregates[k].numSegments}</td>` +
      `<td>${aggregates[k].numRatings}</td>`;
    if (!aggregates[k].numSegments || !aggregates[k].numRatings) {
      for (let i = 0; i < 12; i++) {
        rowHTML += "<td>-</td>";
      }
    } else {
      for (let s of scoreFields) {
        let content = aggregates[k].hasOwnProperty(s)
          ? aggregates[k][s].toFixed(3)
          : "-";
        if (title == "By system" && s == "score") {
          /**
           * Obtain and show confidence intervals for each system MQM score
           * when there are at least 5 documents after filtering. Otherwise,
           * show N/A instead.
           */
          if (Object.keys(stats[k]).length >= 5) {
            /**
             * Insert placeholder for the CI span. Span id is determined by
             * the order the systems are rendered in HTML. In this case, systems
             * are sorted by MQM score.
             */
            const spanId = `mqm-ci-${rowIdx}`;
            content += `<span class="mqm-ci" id=${spanId}> (-.--- - -.---)</span>`;
          } else {
            content += `<span class="mqm-ci"> (N/A)</span>`;
          }
        }
        const nameParts = s.split("-", 2);
        const cls =
          nameParts.length == 2
            ? ' class="mqm-stats-' + nameParts[0] + '"'
            : "";
        rowHTML += `<td${cls}>${content}</td>`;
      }
      let errorSpan = 0;
      if (aggregates[k].numWithErrors > 0) {
        errorSpan = aggregates[k].errorSpans / aggregates[k].numWithErrors;
      }
      rowHTML += `<td>${errorSpan.toFixed(1)}</td>`;
    }
    rowHTML += "</tr>\n";
    tbody.insertAdjacentHTML("beforeend", rowHTML);
  }
  // Incrementally collect samples and show confidence intervals.
  if (title == "By system") {
    mqmPrepareDocScores(stats);
    mqmShowCI(keys);
  }
}

/**
 * Shows the system x rater matrix of scores. The rows and columns are
 * ordered by total MQM score.
 */
function mqmShowSystemRaterStats() {
  const table = document.getElementById("mqm-system-x-rater");

  const systems = Object.keys(mqmStatsBySystem);
  const systemAggregates = {};
  for (let sys of systems) {
    const segs = mqmGetSegStatsAsArray(mqmStatsBySystem[sys]);
    systemAggregates[sys] = mqmAggregateSegStats(segs);
  }

  const SORT_FIELD = "score";
  systems.sort(
    (sys1, sys2) =>
      systemAggregates[sys1][SORT_FIELD] - systemAggregates[sys2][SORT_FIELD],
  );

  const raters = Object.keys(mqmStatsByRater);
  const raterAggregates = {};
  for (let rater of raters) {
    const segs = mqmGetSegStatsAsArray(mqmStatsByRater[rater]);
    raterAggregates[rater] = mqmAggregateSegStats(segs);
  }
  raters.sort(
    (rater1, rater2) =>
      raterAggregates[rater1][SORT_FIELD] - raterAggregates[rater2][SORT_FIELD],
  );

  let html = `
     <thead>
       <tr>
         <th>System</th>
         <th>All raters</th>`;
  for (let rater of raters) {
    html += `
         <th>${rater}</th>`;
  }
  html += `
       </tr>
     </thead>
     <tbody>`;
  /**
   * State for detecting "out-of-order" raters. We say a rater is out-of-order
   * if their rating for a system is oppositely related to the previous
   * system's rating, when compared with the aggregate over all raters.
   */
  let lastAllRaters = 0;
  const lastForRater = {};
  for (let rater of raters) {
    lastForRater[rater] = 0;
  }
  for (let sys of systems) {
    const allRatersScore = systemAggregates[sys].score;
    html += `
       <tr><td>${sys}</td><td>${allRatersScore.toFixed(3)}</td>`;
    for (let rater of raters) {
      const segs = mqmGetSegStatsAsArray(
        mqmStatsBySystemRater[sys][rater] || {},
      );
      if (segs && segs.length > 0) {
        const aggregate = mqmAggregateSegStats(segs);
        const cls =
          (aggregate.score < lastForRater[rater] &&
            allRatersScore > lastAllRaters) ||
          (aggregate.score > lastForRater[rater] &&
            allRatersScore < lastAllRaters)
            ? ' class="mqm-out-of-order"'
            : "";
        html += `
             <td><span${cls}>${aggregate.score.toFixed(3)}</span></td>`;
        lastForRater[rater] = aggregate.score;
      } else {
        html += "<td>-</td>";
        /**
         * Ensure that the next score for this rater is marked as out-of-order
         * or not in some reasonable manner:
         */
        lastForRater[rater] = allRatersScore;
      }
    }
    lastAllRaters = allRatersScore;
    html += `
       </tr>`;
  }
  html += `
     </tbody>`;
  table.innerHTML = html;
}

/**
 * Sorter function where a & b are both a [doc, seg] pair.
 * @param {!Array<string|number>} a
 * @param {!Array<string|number>} b
 * @return {number} Comparison for sorting a & b.
 */
function mqmDocSegsSorter(a, b) {
  if (a[0] < b[0]) return -1;
  if (a[0] > b[0]) return 1;
  seg1 = mqmMaybeParseInt(a[1]);
  seg2 = mqmMaybeParseInt(b[1]);
  if (seg1 < seg2) return -1;
  if (seg1 > seg2) return 1;
  return 0;
}

/**
 * From a stats object that's keyed on doc and then on segs, extracts all
 * [doc, seg] pairs into an array, sorts the array, and returns it.
 * @param {!Object} stats
 * @return {!Array}
 */
function mqmGetDocSegs(stats) {
  const segs = [];
  for (let doc in stats) {
    const docstats = stats[doc];
    for (let docSeg in docstats) {
      segs.push([doc, docSeg]);
    }
  }
  return segs.sort(mqmDocSegsSorter);
}

/**
 * Makes a convenient key that captures a doc name and a docSegId.
 * @param {string} doc
 * @param {string|number} seg
 * @return {string}
 */
function mqmDocSegKey(doc, seg) {
  return doc + ":" + seg;
}

/**
 * Helper class for building a system-vs-system segment score differences
 * histogram. Call addSegment() on it multiple times to record segment
 * scores. Then call display().
 */
function MQMSysVSysHistBuilder() {
  /** @const {number} Width of a histogram bin, in MQM score units */
  this.BIN_WIDTH = 0.5;
  /** @const {number} Width of a histogram bin, in pixels */
  this.BIN_WIDTH_PIXELS = 15;
  /** @const {number} Width of half of the central "zero" bin, in pixels */
  this.ZERO_BIN_HALF_WIDTH_PIXELS = 3.5;

  this.LOG_MULTIPLIER = 1.0 / Math.LN2;
  this.LOG_UNIT_HEIGHT_PIXELS = 25;
  this.TOP_OFFSET_PIXELS = 49;
  this.BOTTOM_OFFSET_PIXELS = 50;

  this.COLORS = ["lightgreen", "lightblue"];
  this.COLOR_EQUAL = "lightgray";
  this.COLOR_OUTLINE = "black";
  this.COLOR_LEGEND = "black";
  this.COLOR_LABELS = "gray";
  this.COLOR_LINES = "lightgray";

  /**
   * @const {!Array<string>} Array of doc-seg keys for which both systems have
   *     the same segment score.
   */
  this.equals = [];
  /**
   * @const {!Array<!Object>} Pair of objects, each keyed by bin number. The
   *     0th object has bins where system 1 is better and the 1st object
   *     has bins where system 2 is better. Each bin has an array of doc-seg
   *     keys.
   */
  this.systemComp = [{}, {}];

  /**
   * @const {number} The largest (positive or negative) bin visible on the
   *     X-axis
   */
  this.maxBin = 1;
  /** @const {number} The largest count visible on the Y-axis */
  this.maxCount = 8;
}

/**
 * Adds a segment to the histogram, updating the appropriate bin.
 * @param {string} doc
 * @param {string|number} docSegId
 * @param {number} score1 The score for the first system
 * @param {number} score2 The score for the second system
 */
MQMSysVSysHistBuilder.prototype.addSegment = function (
  doc,
  docSegId,
  score1,
  score2,
) {
  if (score1 == score2) {
    this.equals.push(mqmDocSegKey(doc, docSegId));
    if (this.equals.length > this.maxCount) {
      this.maxCount = this.equals.length;
    }
    return;
  }
  const diff = Math.abs(score1 - score2);
  const diffBin = Math.floor(diff / this.BIN_WIDTH);
  const which = score1 < score2 ? this.systemComp[0] : this.systemComp[1];
  if (!which.hasOwnProperty(diffBin)) {
    which[diffBin] = [];
  }
  which[diffBin].push(mqmDocSegKey(doc, docSegId));
  if (diffBin > this.maxBin) {
    this.maxBin = diffBin;
  }
  if (which[diffBin].length > this.maxCount) {
    this.maxCount = which[diffBin].length;
  }
};

/**
 * Creates and returns an SVG rect.
 * @param {number} x
 * @param {number} y
 * @param {number} w
 * @param {number} h
 * @param {string} color
 * @return {!Element}
 */
MQMSysVSysHistBuilder.prototype.getRect = function (x, y, w, h, color) {
  const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
  rect.setAttributeNS(null, "x", x);
  rect.setAttributeNS(null, "y", y + this.TOP_OFFSET_PIXELS);
  rect.setAttributeNS(null, "width", w);
  rect.setAttributeNS(null, "height", h);
  rect.style.fill = color;
  rect.style.stroke = this.COLOR_OUTLINE;
  return rect;
};

/**
 * Creates a histogram bar with a given description, makes it clickable to
 * constrain the view to the docsegs passed.
 * @param {!Element} plot
 * @param {number} x
 * @param {number} y
 * @param {number} w
 * @param {number} h
 * @param {string} color
 * @param {string} desc
 * @param {!Array<string>} docsegs
 */
MQMSysVSysHistBuilder.prototype.makeHistBar = function (
  plot,
  x,
  y,
  w,
  h,
  color,
  desc,
  docsegs,
) {
  /**
   * Need to wrap the rect in a g (group) element to be able to show
   * the description when hovering ("title" attribute does not work with SVG
   * elements).
   */
  const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
  g.setAttributeNS(null, "class", "mqm-sys-v-sys-hist");
  g.insertAdjacentHTML(
    "beforeend",
    `<title>Click to see examples of ${desc}</title>`,
  );
  const rect = this.getRect(x, y, w, h, color);
  g.appendChild(rect);
  const viewingConstraints = {};
  for (let ds of docsegs) {
    viewingConstraints[ds] = true;
  }
  viewingConstraints.description = desc;
  viewingConstraints.color = color;
  g.addEventListener("click", (e) => {
    mqmShow(viewingConstraints);
  });
  plot.appendChild(g);
};

/**
 * Creates a line on the plot.
 * @param {!Element} plot
 * @param {number} x1
 * @param {number} y1
 * @param {number} x2
 * @param {number} y2
 * @param {string} color
 */
MQMSysVSysHistBuilder.prototype.makeLine = function (
  plot,
  x1,
  y1,
  x2,
  y2,
  color,
) {
  const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
  line.setAttributeNS(null, "x1", x1);
  line.setAttributeNS(null, "y1", y1 + this.TOP_OFFSET_PIXELS);
  line.setAttributeNS(null, "x2", x2);
  line.setAttributeNS(null, "y2", y2 + this.TOP_OFFSET_PIXELS);
  line.style.stroke = color;
  plot.appendChild(line);
};

/**
 * Writes some text on the plot.
 * @param {!Element} plot
 * @param {number} x
 * @param {number} y
 * @param {string} s
 * @param {string} color
 */
MQMSysVSysHistBuilder.prototype.makeText = function (plot, x, y, s, color) {
  const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
  text.setAttributeNS(null, "x", x);
  text.setAttributeNS(null, "y", y + this.TOP_OFFSET_PIXELS);
  text.innerHTML = s;
  text.style.fill = color;
  plot.appendChild(text);
};

/**
 * Returns height in pixels for a histogram bar with the given count.
 * @param {number} count
 * @return {number}
 */
MQMSysVSysHistBuilder.prototype.heightInPixels = function (count) {
  if (count == 0) return 0;
  return (
    this.LOG_UNIT_HEIGHT_PIXELS * (Math.log(count) * this.LOG_MULTIPLIER + 1)
  );
};

/**
 * Displays the histogram using the data collected through prior addSegment()
 * calls.
 */
MQMSysVSysHistBuilder.prototype.display = function () {
  /** Create some buffer space around the plot. */
  this.maxBin += 5;
  this.maxCount += 10;

  const plotHalfWidth =
    this.maxBin * this.BIN_WIDTH_PIXELS + this.ZERO_BIN_HALF_WIDTH_PIXELS;
  const plotWidth = 2 * plotHalfWidth;
  const plotHeight = this.heightInPixels(this.maxCount);
  const svgWidth = plotWidth;
  const svgHeight =
    plotHeight + (this.TOP_OFFSET_PIXELS + this.BOTTOM_OFFSET_PIXELS);
  const plot = document.getElementById("mqm-sys-v-sys-plot");
  plot.innerHTML = "";
  plot.setAttributeNS(null, "viewBox", `0 0 ${svgWidth} ${svgHeight}`);
  plot.setAttributeNS(null, "width", svgWidth);
  plot.setAttributeNS(null, "height", svgHeight);
  if (this.equals.length > 0) {
    /** Draw the middle "zero" bin */
    const h = this.heightInPixels(this.equals.length);
    this.makeHistBar(
      plot,
      plotHalfWidth - this.ZERO_BIN_HALF_WIDTH_PIXELS,
      plotHeight - h,
      2 * this.ZERO_BIN_HALF_WIDTH_PIXELS,
      h,
      this.COLOR_EQUAL,
      `${this.equals.length} segment(s) ` +
        `where both ${mqmSysVSys1} and ${mqmSysVSys2} have equal scores.`,
      this.equals,
    );
  }
  for (let s = 0; s < 2; s++) {
    const systemComp = this.systemComp[s];
    const betterSystem = s == 0 ? mqmSysVSys1 : mqmSysVSys2;
    const worseSystem = s == 0 ? mqmSysVSys2 : mqmSysVSys1;
    let totalSegs = 0;
    for (let binStr in systemComp) {
      const segs = systemComp[binStr];
      if (segs.length == 0) continue;
      const bin = parseInt(binStr);
      const h = this.heightInPixels(segs.length);
      let x = this.ZERO_BIN_HALF_WIDTH_PIXELS + bin * this.BIN_WIDTH_PIXELS;
      if (s == 1) {
        x += plotHalfWidth;
      } else {
        x = plotHalfWidth - x - this.BIN_WIDTH_PIXELS;
      }
      const desc =
        `${segs.length} segment(s) ` +
        `where ${betterSystem} is better than ${worseSystem} by a ` +
        "score difference in the range " +
        `(${bin * this.BIN_WIDTH}, ${(bin + 1) * this.BIN_WIDTH}].`;
      this.makeHistBar(
        plot,
        x,
        plotHeight - h,
        this.BIN_WIDTH_PIXELS,
        h,
        this.COLORS[s],
        desc,
        segs,
      );
      totalSegs += segs.length;
    }
    if (totalSegs > 0) {
      /* legend, shown in the area above the plot */
      const y = -38 + s * (this.BIN_WIDTH_PIXELS + 5);
      const x = 50;
      plot.appendChild(
        this.getRect(
          x,
          y,
          this.BIN_WIDTH_PIXELS,
          this.BIN_WIDTH_PIXELS,
          this.COLORS[s],
        ),
      );
      this.makeText(
        plot,
        x + this.BIN_WIDTH_PIXELS + 5,
        y + 14,
        `${totalSegs}: ${betterSystem} better`,
        this.COLOR_LEGEND,
      );
    }
  }
  /* y axis labels */
  this.makeLine(plot, 0, plotHeight, plotWidth, plotHeight, this.COLOR_LINES);
  this.makeText(plot, 5, plotHeight - 2, "0", this.COLOR_LABELS);
  for (let l = 1; l <= this.maxCount; l *= 2) {
    const h = this.heightInPixels(l);
    this.makeLine(
      plot,
      0,
      plotHeight - h,
      plotWidth,
      plotHeight - h,
      this.COLOR_LINES,
    );
    this.makeText(plot, 5, plotHeight - h - 2, "" + l, this.COLOR_LABELS);
  }
  /* x axis labels */
  this.makeLine(
    plot,
    plotHalfWidth,
    plotHeight,
    plotHalfWidth,
    plotHeight + 8,
    this.COLOR_LABELS,
  );
  this.makeText(
    plot,
    plotHalfWidth - 5,
    plotHeight + 20,
    "0",
    this.COLOR_LABELS,
  );
  for (let s = 0; s < 2; s++) {
    const bMax = this.maxBin * this.BIN_WIDTH;
    for (let b = 1; b < bMax; b++) {
      let x =
        this.ZERO_BIN_HALF_WIDTH_PIXELS +
        (b * this.BIN_WIDTH_PIXELS) / this.BIN_WIDTH;
      if (s == 1) {
        x += plotHalfWidth;
      } else {
        x = plotHalfWidth - x;
      }
      this.makeLine(plot, x, plotHeight, x, plotHeight + 8, this.COLOR_LABELS);
      const xval = s == 0 ? 0 - b : b;
      const xdelta = s == 0 ? 9 : 3;
      this.makeText(
        plot,
        x - xdelta,
        plotHeight + 20,
        "" + xval,
        this.COLOR_LABELS,
      );
    }
  }
  /* X-axis name */
  this.makeText(
    plot,
    plotHalfWidth - 80,
    plotHeight + 35,
    "MQM score difference",
    this.COLOR_LEGEND,
  );
};

/**
 * Shows the system v system histogram of segment score differences.
 * @param {boolean=} refreshChoices Set to false when used for only changing the
 *     values picked for system1 or system2.
 */
function mqmShowSysVSys(refreshChoices = false) {
  const selectSys1 = document.getElementById("mqm-sys-v-sys-1");
  const selectSys2 = document.getElementById("mqm-sys-v-sys-2");
  if (refreshChoices) {
    /** We are showing the plot for new (or newly filtered) data. */
    selectSys1.innerHTML = "";
    selectSys2.innerHTML = "";
    const systems = Object.keys(mqmStatsBySystem);
    /**
     * If possible, use the previously set values. If possible, keep
     * system1 and system2 distinct from each other.
     */
    if (mqmSysVSys1 && !mqmStatsBySystem.hasOwnProperty(mqmSysVSys1)) {
      mqmSysVSys1 = "";
    }
    if (mqmSysVSys2 && !mqmStatsBySystem.hasOwnProperty(mqmSysVSys2)) {
      mqmSysVSys2 = "";
    }
    if (mqmSysVSys1 == mqmSysVSys2) {
      mqmSysVSys2 = "";
    }
    for (let system of systems) {
      if (!mqmSysVSys1) {
        mqmSysVSys1 = system;
      }
      if (!mqmSysVSys2 && system != mqmSysVSys1) {
        mqmSysVSys2 = system;
      }
      const option1 = document.createElement("option");
      option1.value = system;
      option1.innerHTML = system;
      if (system == mqmSysVSys1) {
        option1.selected = true;
      }
      selectSys1.insertAdjacentElement("beforeend", option1);
      const option2 = document.createElement("option");
      option2.value = system;
      option2.innerHTML = system;
      if (system == mqmSysVSys2) {
        option2.selected = true;
      }
      selectSys2.insertAdjacentElement("beforeend", option2);
    }
  }

  mqmSysVSys1 = selectSys1.value;
  mqmSysVSys2 = selectSys2.value;
  const docsegs1 = mqmGetDocSegs(mqmStatsBySystem[mqmSysVSys1] || {});
  const docsegs2 = mqmGetDocSegs(mqmStatsBySystem[mqmSysVSys2] || {});
  /**
   * Find common segments.
   */
  let i1 = 0;
  let i2 = 0;
  const docsegs12 = [];
  while (i1 < docsegs1.length && i2 < docsegs2.length) {
    const ds1 = docsegs1[i1];
    const ds2 = docsegs2[i2];
    const sort = mqmDocSegsSorter(ds1, ds2);
    if (sort < 0) {
      i1++;
    } else if (sort > 0) {
      i2++;
    } else {
      docsegs12.push(ds1);
      i1++;
      i2++;
    }
  }

  document.getElementById("mqm-sys-v-sys-xsegs").innerHTML = docsegs12.length;
  document.getElementById("mqm-sys-v-sys-1-segs").innerHTML = docsegs1.length;
  document.getElementById("mqm-sys-v-sys-2-segs").innerHTML = docsegs2.length;

  const histBuilder = new MQMSysVSysHistBuilder();
  for (let i = 0; i < docsegs12.length; i++) {
    const doc = docsegs12[i][0];
    const docSegId = docsegs12[i][1];
    const aggregate1 = mqmAggregateSegStats([
      mqmStatsBySystem[mqmSysVSys1][doc][docSegId],
    ]);
    const aggregate2 = mqmAggregateSegStats([
      mqmStatsBySystem[mqmSysVSys2][doc][docSegId],
    ]);
    histBuilder.addSegment(doc, docSegId, aggregate1.score, aggregate2.score);
  }
  histBuilder.display();
}

/**
 * Shows details of severity- and category-wise scores (from the
 *   mqmStatsBySevCat object) in the categories table.
 */
function mqmShowSevCatStats() {
  const stats = mqmStatsBySevCat;
  const systems = {};
  for (let severity in stats) {
    for (let category in stats[severity]) {
      for (let system in stats[severity][category]) {
        if (!systems[system]) systems[system] = 0;
        systems[system] += stats[severity][category][system];
      }
    }
  }
  const systemsList = Object.keys(systems);
  const colspan = systemsList.length || 1;
  const th = document.getElementById("mqm-sevcat-stats-th");
  th.colSpan = colspan;

  systemsList.sort((sys1, sys2) => systems[sys2] - systems[sys1]);
  const tbody = document.getElementById("mqm-sevcat-stats-tbody");

  let rowHTML = "<tr><td></td><td></td><td></td>";
  for (let system of systemsList) {
    rowHTML += `<td><b>${system == mqmTotal ? "Total" : system}</b></td>`;
  }
  rowHTML += "</tr>\n";
  tbody.insertAdjacentHTML("beforeend", rowHTML);

  const sevKeys = Object.keys(stats);
  sevKeys.sort();
  for (let severity of sevKeys) {
    tbody.insertAdjacentHTML(
      "beforeend",
      `<tr><td colspan="${3 + colspan}"><hr></td></tr>`,
    );
    const sevStats = stats[severity];
    const catKeys = Object.keys(sevStats);
    catKeys.sort((k1, k2) => sevStats[k2][mqmTotal] - sevStats[k1][mqmTotal]);
    for (let category of catKeys) {
      const row = sevStats[category];
      let rowHTML = `<tr><td>${severity}</td><td>${category}</td><td></td>`;
      for (let system of systemsList) {
        const val = row.hasOwnProperty(system) ? row[system] : "";
        rowHTML += `<td>${val ? val : ""}</td>`;
      }
      rowHTML += "</tr>\n";
      tbody.insertAdjacentHTML("beforeend", rowHTML);
    }
  }
}

/**
 * Shows all the stats.
 */
function mqmShowStats() {
  /**
   * Get aggregates for the overall stats. This lets us decide which score
   * splits have non-zero values and we show score columns for only those
   * splits.
   */
  const keys = Object.keys(mqmStats);
  const mqmStatsAggregates = {};
  for (let k of keys) {
    const segs = mqmGetSegStatsAsArray(mqmStats[k]);
    mqmStatsAggregates[k] = mqmAggregateSegStats(segs);
  }
  const overallStats = mqmStatsAggregates[mqmTotal];
  mqmScoreWeightedFields = [];
  mqmScoreSliceFields = [];
  for (let key in overallStats) {
    if (!overallStats[key]) continue;
    if (key.startsWith(MQM_SCORE_WEIGHTED_PREFIX)) {
      mqmScoreWeightedFields.push(mqmScoreKeyToName(key));
    } else if (key.startsWith(MQM_SCORE_SLICE_PREFIX)) {
      mqmScoreSliceFields.push(mqmScoreKeyToName(key));
    }
  }
  mqmScoreWeightedFields.sort(
    (k1, k2) =>
      (overallStats[MQM_SCORE_WEIGHTED_PREFIX + k2] ?? 0) -
      (overallStats[MQM_SCORE_WEIGHTED_PREFIX + k1] ?? 0),
  );
  mqmScoreSliceFields.sort(
    (k1, k2) =>
      (overallStats[MQM_SCORE_SLICE_PREFIX + k2] ?? 0) -
      (overallStats[MQM_SCORE_SLICE_PREFIX + k1] ?? 0),
  );
  /**
   * First show the scores table header with the sorted columns from
   * mqmScoreWeightedFields and mqmScoreSliceFields. Then add scores rows to
   * the table, for overall scores, then by system, and then by rater.
   */
  mqmShowScoresHeader();
  mqmShowScores("mqm-stats-tbody", "", mqmStats, mqmStatsAggregates);
  mqmShowScores("mqm-stats-tbody", "By system", mqmStatsBySystem);
  mqmShowScores("mqm-stats-tbody", "By rater", mqmStatsByRater);
  mqmShowSystemRaterStats();
  mqmShowSysVSys(true);
  mqmShowSevCatStats();
  //mqmShowEvents();
}

/**
 * Increments the counts statsArray[severity][category][system] and
 *   statsArray[severity][category][mqmTotal].
 * @param {!Object} statsArray
 * @param {string} system
 * @param {string} category
 * @param {string} severity
 */
function mqmAddSevCatStats(statsArray, system, category, severity) {
  if (!statsArray.hasOwnProperty(severity)) {
    statsArray[severity] = {};
  }
  if (!statsArray[severity].hasOwnProperty(category)) {
    statsArray[severity][category] = {};
    statsArray[severity][category][mqmTotal] = 0;
  }
  if (!statsArray[severity][category].hasOwnProperty(system)) {
    statsArray[severity][category][system] = 0;
  }
  statsArray[severity][category][mqmTotal]++;
  statsArray[severity][category][system]++;
}

/**
 * Adds UI events and timings from metadata into events.
 * @param {!Object} events
 * @param {!Object} metadata
 */
function mqmAddEvents(events, metadata) {
  if (!metadata.timing) {
    return;
  }
  for (let e of Object.keys(metadata.timing)) {
    if (!events.hasOwnProperty(e)) {
      events[e] = {
        count: 0,
        timeMS: 0,
      };
    }
    events[e].count += metadata.timing[e].count;
    events[e].timeMS += metadata.timing[e].timeMS;
  }
}

/**
 * Given a lowercase severity (lsev) & category (lcat), returns true if it is
 *   the "Non-translation" error, allowing for underscore/dash variation and
 *   a possible trailing exclamation mark. Non-translation may have been marked
 *   as a severity or as a category.
 * @param {string} lsev
 * @param {string} lcat
 * @return {boolean}
 */
function mqmIsNonTrans(lsev, lcat) {
  return (
    lsev.startsWith("non-translation") ||
    lsev.startsWith("non_translation") ||
    lcat.startsWith("non-translation") ||
    lcat.startsWith("non_translation")
  );
}

/**
 * Given a lowercase category (lcat), returns true if it is an accuracy error.
 * @param {string} lcat
 * @return {boolean}
 */
function mqmIsAccuracy(lcat) {
  return lcat.startsWith("accuracy") || lcat.startsWith("terminology");
}

/**
 * Given text containing marked spans, returns the length of the spanned parts.
 * @param {string} s
 * @return {number}
 */
function mqmSpanLength(s) {
  let offset = 0;
  let span = 0;
  let index = 0;
  while ((index = s.indexOf('<span class="mqm-m', offset)) >= offset) {
    offset = index + 1;
    let startSpan = s.indexOf(">", offset);
    if (startSpan < 0) break;
    startSpan += 1;
    const endSpan = s.indexOf("</span>", startSpan);
    if (endSpan < 0) break;
    console.assert(startSpan <= endSpan, startSpan, endSpan);
    span += endSpan - startSpan;
    offset = endSpan + 7;
  }
  return span;
}

/**
 * Updates stats with an error of (category, severity). The weighted score
 * component to use is the first matching one in mqmWeights[]. Similarly, the
 * slice to attribute the score to is the first matching one in mqmSlices[].
 * @param {!Object} stats
 * @param {string} category
 * @param {string} severity
 * @param {number} span
 */
function mqmAddErrorStats(stats, category, severity, span) {
  const lcat = category.toLowerCase().trim();
  if (lcat == "no-error" || lcat == "no_error") {
    return;
  }

  const lsev = severity.toLowerCase().trim();
  if (lsev == "hotw-test" || lsev == "hotw_test") {
    if (lcat == "found") {
      stats.hotwFound++;
    } else if (lcat == "missed") {
      stats.hotwMissed++;
    }
    return;
  }
  if (lsev == "unrateable") {
    stats.unrateable++;
    return;
  }
  if (lsev == "neutral") {
    return;
  }

  if (span > 0) {
    /* There is a scoreable error span.  */
    stats.numWithErrors++;
    stats.errorSpans += span;
  }

  let score = 0;
  for (let sc of mqmWeights) {
    if (mqmMatchesScoreSplit(sc, lsev, lcat)) {
      score = sc.weight;
      stats.score += score;
      break;
    }
  }
  if (score > 0) {
    for (let sc of mqmSlices) {
      if (mqmMatchesScoreSplit(sc, lsev, lcat)) {
        const key = mqmScoreKey(sc.name, true);
        stats[key] = (stats[key] ?? 0) + score;
        break;
      }
    }
  }
}

/**
 * Returns the last element of array a.
 * @param {!Array<T>} a
 * @return {T}
 * @template T
 */
function mqmArrayLast(a) {
  return a[a.length - 1];
}

/**
 * Returns the segment stats keyed by doc and docSegId. This will
 * create an empty array if the associated segment stats array doesn't exist.
 * @param {!Object} statsByDocAndDocSegId
 * @param {string} doc
 * @param {string} docSegId
 * @return {!Array}
 */
function mqmGetSegStats(statsByDocAndDocSegId, doc, docSegId) {
  if (!statsByDocAndDocSegId.hasOwnProperty(doc)) {
    statsByDocAndDocSegId[doc] = {};
  }
  if (!statsByDocAndDocSegId[doc].hasOwnProperty(docSegId)) {
    statsByDocAndDocSegId[doc][docSegId] = [];
  }
  return statsByDocAndDocSegId[doc][docSegId];
}

/**
 * Flattens the nested stats object into an array of segment stats.
 * @param {!Object} statsByDocAndDocSegId
 * @return {!Array}
 */
function mqmGetSegStatsAsArray(statsByDocAndDocSegId) {
  let arr = [];
  for (let doc of Object.keys(statsByDocAndDocSegId)) {
    let statsByDocSegId = statsByDocAndDocSegId[doc];
    for (let docSegId of Object.keys(statsByDocSegId)) {
      arr.push(statsByDocSegId[docSegId]);
    }
  }
  return arr;
}

/**
 * Shows up or down arrow to show which field is used for sorting.
 */
function mqmShowSortArrow() {
  // Remove existing active arrows first.
  const active = document.querySelector(".mqm-arrow-active");
  if (active) active.classList.remove("mqm-arrow-active");

  // Highlight the appropriate arrow for the sorting field.
  const className = mqmSortReverse ? "mqm-arrow-down" : "mqm-arrow-up";
  const arrow = document.querySelector(`#${mqmSortByHeaderId} .${className}`);
  arrow.classList.add("mqm-arrow-active");
}

/**
 * Updates the display to show the segment data and scores according to the
 * current filters.
 * @param {?Object=} viewingConstraints Optional dict of doc:seg to view. When
 *     not null, only these segments are shown. When not null, this parameter
 *     object should have two additional properties:
 *       description: Shown to the user, describing the constrained view.
 *       color: A useful identifying color that highlights the description.
 */
function mqmShow(viewingConstraints = null) {
  document.body.style.cursor = "wait";

  // Cancel existing CI computation when a new `mqmShow` is called.
  if (mqmCIComputation) {
    clearTimeout(mqmCIComputation);
    mqmClearCIComputation();
  }

  const tbody = document.getElementById("mqm-tbody");
  tbody.innerHTML = "";
  document.getElementById("mqm-stats-tbody").innerHTML = "";
  document.getElementById("mqm-sevcat-stats-tbody").innerHTML = "";

  mqmStats = {};
  mqmStats[mqmTotal] = {};
  mqmStatsBySystem = {};
  mqmStatsByRater = {};
  mqmStatsBySystemRater = {};
  mqmDataFiltered = [];

  mqmStatsBySevCat = {};
  mqmEvents = {};

  let shown = 0;
  const filterExpr = document.getElementById("mqm-filter-expr").value.trim();
  document.getElementById("mqm-filter-expr-error").innerHTML = "";
  const filters = document.getElementsByClassName("mqm-filter-re");
  const filterREs = mqmGetFilterREs();
  let lastRow = null;
  let currSegStats = [];
  let currSegStatsBySys = [];
  let currSegStatsByRater = [];
  let currSegStatsBySysRater = [];

  const viewingConstraintsDesc = document.getElementById(
    "mqm-viewing-constraints",
  );
  if (viewingConstraints) {
    viewingConstraintsDesc.innerHTML =
      "View limited to " +
      viewingConstraints.description +
      " Click on this text to remove this constraint.";
    viewingConstraintsDesc.style.backgroundColor = viewingConstraints.color;
    viewingConstraintsDesc.style.display = "";
  } else {
    viewingConstraintsDesc.innerHTML = "";
    viewingConstraintsDesc.style.display = "none";
  }

  for (let rowId = 0; rowId < mqmData.length; rowId++) {
    const parts = mqmData[rowId];
    let match = true;
    for (let i = 0; i < 9; i++) {
      if (filterREs[i] && !filterREs[i].test(parts[i])) {
        match = false;
        break;
      }
    }
    if (!match) {
      continue;
    }
    if (!mqmFilterExprPasses(filterExpr, parts)) {
      continue;
    }

    mqmDataFiltered.push(parts);

    const system = parts[MQM_DATA_SYSTEM];
    const rater = parts[MQM_DATA_RATER];
    const doc = parts[MQM_DATA_DOC];
    const docSegId = parts[MQM_DATA_DOC_SEG_ID];
    const sameAsLast =
      lastRow &&
      system == lastRow[MQM_DATA_SYSTEM] &&
      doc == lastRow[MQM_DATA_DOC] &&
      docSegId == lastRow[MQM_DATA_DOC_SEG_ID] &&
      parts[MQM_DATA_GLOBAL_SEG_ID] == lastRow[MQM_DATA_GLOBAL_SEG_ID];

    if (!sameAsLast) {
      currSegStats = mqmGetSegStats(mqmStats[mqmTotal], doc, docSegId);
      if (!mqmStatsBySystem.hasOwnProperty(system)) {
        mqmStatsBySystem[system] = {};
      }
      currSegStatsBySys = mqmGetSegStats(
        mqmStatsBySystem[system],
        doc,
        docSegId,
      );
      currSegStats.srcLen = parts.srcLen;
      currSegStatsBySys.srcLen = parts.srcLen;
    }

    if (!sameAsLast || rater != lastRow[MQM_DATA_RATER]) {
      currSegStats.push(mqmInitRaterStats(rater));
      currSegStatsBySys.push(mqmInitRaterStats(rater));
      if (!mqmStatsByRater.hasOwnProperty(rater)) {
        /** New rater. **/
        mqmStatsByRater[rater] = {};
      }
      currSegStatsByRater = mqmGetSegStats(
        mqmStatsByRater[rater],
        doc,
        docSegId,
      );
      currSegStatsByRater.push(mqmInitRaterStats(rater));
      currSegStatsByRater.srcLen = parts.srcLen;

      if (!mqmStatsBySystemRater.hasOwnProperty(system)) {
        mqmStatsBySystemRater[system] = {};
      }
      if (!mqmStatsBySystemRater[system].hasOwnProperty(rater)) {
        mqmStatsBySystemRater[system][rater] = {};
      }
      currSegStatsBySysRater = mqmGetSegStats(
        mqmStatsBySystemRater[system][rater],
        doc,
        docSegId,
      );
      currSegStatsBySysRater.push(mqmInitRaterStats(rater));
      currSegStatsBySysRater.srcLen = parts.srcLen;
    }
    const span =
      mqmSpanLength(parts[MQM_DATA_SOURCE]) +
      mqmSpanLength(parts[MQM_DATA_TARGET]);
    mqmAddErrorStats(
      mqmArrayLast(currSegStats),
      parts[MQM_DATA_CATEGORY],
      parts[MQM_DATA_SEVERITY],
      span,
    );
    mqmAddErrorStats(
      mqmArrayLast(currSegStatsBySys),
      parts[MQM_DATA_CATEGORY],
      parts[MQM_DATA_SEVERITY],
      span,
    );
    mqmAddErrorStats(
      mqmArrayLast(currSegStatsByRater),
      parts[MQM_DATA_CATEGORY],
      parts[MQM_DATA_SEVERITY],
      span,
    );
    mqmAddErrorStats(
      mqmArrayLast(currSegStatsBySysRater),
      parts[MQM_DATA_CATEGORY],
      parts[MQM_DATA_SEVERITY],
      span,
    );

    mqmAddSevCatStats(
      mqmStatsBySevCat,
      system,
      parts[MQM_DATA_CATEGORY],
      parts[MQM_DATA_SEVERITY],
    );
    mqmAddEvents(mqmEvents, parts[MQM_DATA_METADATA]);

    lastRow = parts;

    if (
      viewingConstraints &&
      !viewingConstraints[mqmDocSegKey(doc, docSegId)]
    ) {
      continue;
    }
    if (shown >= mqmLimit) {
      continue;
    }
    let rowHTML = "";
    for (let i = 0; i < MQM_DATA_METADATA; i++) {
      let val = parts[i];
      let cls = 'class="mqm-val"';
      if (i == MQM_DATA_SOURCE || i == MQM_DATA_TARGET) {
        cls = "";
        if (sameAsLast) {
          val = mqmOnlyKeepSpans(val);
        }
      }
      if (i == MQM_DATA_RATER && parts[MQM_DATA_METADATA].timestamp) {
        /* There is a timestamp, but it might have been stringified */
        const timestamp = parseInt(parts[MQM_DATA_METADATA].timestamp, 10);
        val +=
          '<br><span class="mqm-timestamp">' +
          new Date(timestamp).toLocaleString() +
          "</span>";
      }
      if (i == MQM_DATA_CATEGORY && parts[MQM_DATA_METADATA].note) {
        /* There is a note */
        val +=
          '<br><span class="mqm-note">' +
          parts[MQM_DATA_METADATA].note +
          "</span>";
      }
      rowHTML += `<td ${cls} id="mqm-val-${shown}-${i}">` + val + "</td>\n";
    }
    tbody.insertAdjacentHTML(
      "beforeend",
      `<tr class="mqm-row" id="mqm-row-${rowId}">${rowHTML}</tr>\n`,
    );
    for (let i = 0; i < MQM_DATA_METADATA; i++) {
      if (i == MQM_DATA_SOURCE || i == MQM_DATA_TARGET) continue;
      const v = document.getElementById(`mqm-val-${shown}-${i}`);
      v.addEventListener("click", (e) => {
        filters[i].value = "^" + parts[i] + "$";
        mqmShow();
      });
    }
    shown++;
  }
  mqmShowStats();
  document.body.style.cursor = "auto";
}

/**
 * Replaces <v>...</v> with a span element of class cls.
 * @param {string} text
 * @param {string} cls
 * @return {string}
 */
function mqmMarkSpan(text, cls) {
  text = text.replace(/<v>/, `<span class="${cls}">`);
  text = text.replace(/<\/v>/, "</span>");
  return text;
}

/**
 * Clears all filters.
 */
function mqmClearFilters() {
  const filters = document.getElementsByClassName("mqm-filter-re");
  for (let i = 0; i < filters.length; i++) {
    filters[i].value = "";
  }
  document.getElementById("mqm-filter-expr").value = "";
  document.getElementById("mqm-filter-expr-error").innerHTML = "";
}

/**
 * Clears all filters and shows stats again.
 */
function mqmClearFiltersAndShow() {
  mqmClearFilters();
  mqmShow();
}

/**
 * For the column named by "what", sets the filter to the currently picked
 * value from its drop-down list.
 * @param {string} what
 */
function mqmPick(what) {
  const filters = document.getElementsByClassName("mqm-filter-re");
  let index = -1;
  const exp = "mqm-filter-" + what;
  for (let i = 0; i < filters.length; i++) {
    if (filters[i].id == exp) {
      index = i;
      break;
    }
  }
  if (index < 0) return;
  const sel = document.getElementById("mqm-select-" + what);
  if (!sel) return;
  filters[index].value = sel.value;
  mqmShow();
}

/**
 * Populates the column drop-down lists and filter-expression builder with
 * unique values.
 */
function mqmSetSelectOptions() {
  const options = [{}, {}, {}, {}, null, null, {}, {}, {}];
  for (let parts of mqmData) {
    for (let i = 0; i < 9; i++) {
      if (i == 4 || i == 5) continue;
      options[i][parts[i].trim()] = true;
    }
  }
  const selects = [
    document.getElementById("mqm-select-system"),
    document.getElementById("mqm-select-doc"),
    document.getElementById("mqm-select-doc-seg-id"),
    document.getElementById("mqm-select-global-seg-id"),
    null,
    null,
    document.getElementById("mqm-select-rater"),
    document.getElementById("mqm-select-category"),
    document.getElementById("mqm-select-severity"),
  ];
  for (let i = 0; i < MQM_DATA_METADATA; i++) {
    if (i == MQM_DATA_SOURCE || i == MQM_DATA_TARGET) continue;
    const opt = options[i];
    let html = '<option value=""></option>\n';
    for (let o in opt) {
      if (!o) continue;
      html += `<option value="^${o}$">${o}</option>\n`;
    }
    selects[i].innerHTML = html;
  }

  /**
   * Populate filter clause builder's selects:
   */
  mqmClauseKey = document.getElementById("mqm-clause-key");
  let html = '<option value=""></option>\n';
  for (let sys in options[MQM_DATA_SYSTEM]) {
    html += `<option value="System: ${sys}">System: ${sys}</option>\n`;
  }
  for (let rater in options[MQM_DATA_RATER]) {
    html += `<option value="Rater: ${rater}">Rater: ${rater}</option>\n`;
  }
  mqmClauseKey.innerHTML = html;

  mqmClauseInclExcl = document.getElementById("mqm-clause-inclexcl");

  mqmClauseCat = document.getElementById("mqm-clause-cat");
  html = '<option value=""></option>\n';
  for (let cat in options[MQM_DATA_CATEGORY]) {
    html += `<option value="${cat}">${cat}</option>\n`;
  }
  mqmClauseCat.innerHTML = html;

  mqmClauseSev = document.getElementById("mqm-clause-sev");
  html = '<option value=""></option>\n';
  for (let sev in options[MQM_DATA_SEVERITY]) {
    html += `<option value="${sev}">${sev}</option>\n`;
  }
  mqmClauseSev.innerHTML = html;

  mqmClauseAddAnd = document.getElementById("mqm-clause-add-and");
  mqmClauseAddOr = document.getElementById("mqm-clause-add-or");
  mqmClearClause();
}

/**
 * Sets mqmTSVData from the passed TSV data string or array of strings, and
 * parses it into mqmData.
 * @param {string|!Array<string>} tsvData
 */
function mqmSetData(tsvData) {
  const errors = document.getElementById("mqm-errors");
  errors.innerHTML = "";
  if (Array.isArray(tsvData)) {
    let allTsvData = "";
    for (let tsvDataItem of tsvData) {
      if (!tsvDataItem) continue;
      if (allTsvData && !allTsvData.endsWith("\n")) {
        allTsvData += "\n";
      }
      allTsvData += tsvDataItem;
    }
    tsvData = allTsvData;
  }
  if (!tsvData) {
    errors.innerHTML = "Empty data passed to mqmSetData()";
    return;
  }
  mqmTSVData = tsvData;
  mqmClearFilters();
  mqmData = [];
  const data = mqmTSVData.split("\n");
  for (let line of data) {
    if (!line.trim()) {
      continue;
    }
    if (line.toLowerCase().indexOf("system\tdoc\t") >= 0) {
      /**
       * Skip header line. It may be present anywhere, as we may be looking
       * at data concatenated from multiple files.
       */
      continue;
    }
    const parts = line.split("\t");

    let metadata = {};
    if (parts.length < MQM_DATA_METADATA) {
      errors.insertAdjacentHTML("beforeend", `Could not parse: ${line}`);
      continue;
    } else if (parts.length == MQM_DATA_METADATA) {
      /** TSV data is missing the last metadata column. Create it. */
      parts.push(metadata);
    } else {
      /** Extract comment if into metadata, if there is one. */
      metadata = {};
      const note = parts[MQM_DATA_METADATA].trim();
      if (note) {
        metadata["note"] = note;
      }

      parts[MQM_DATA_METADATA] = metadata;
    }
    /** Move "Rater" down from its position in the TSV data. */
    const temp = parts[4];
    parts[MQM_DATA_SOURCE] = parts[5];
    parts[MQM_DATA_TARGET] = parts[6];
    parts[MQM_DATA_RATER] = temp;
    let spanClass = "mqm-neutral";
    const severity = parts[MQM_DATA_SEVERITY].toLowerCase();
    if (
      severity == "major" ||
      severity.startsWith("non-translation") ||
      severity.startsWith("non_translation")
    ) {
      spanClass = "mqm-major";
    } else if (severity == "minor") {
      spanClass = "mqm-minor";
    } else if (severity == "trivial") {
      spanClass = "mqm-trivial";
    } else if (severity == "critical") {
      spanClass = "mqm-critical";
    }

    /**
     * Count all characters, including spaces, in src/tgt length, excluding
     * the span-marking <v> and </v> tags.
     */
    parts.srcLen = parts[MQM_DATA_SOURCE].replace(/<\/?v>/g, "").length;
    parts.tgtLen = parts[MQM_DATA_TARGET].replace(/<\/?v>/g, "").length;
    parts[MQM_DATA_SOURCE] = mqmMarkSpan(parts[MQM_DATA_SOURCE], spanClass);
    parts[MQM_DATA_TARGET] = mqmMarkSpan(parts[MQM_DATA_TARGET], spanClass);
    mqmData.push(parts);
  }
  mqmSortData(mqmData);
  mqmAddSegmentAggregations();
  mqmSetSelectOptions();
  mqmShow();
}

/**
 * Opens and reads the data file(s) picked by the user and calls mqmSetData().
 */
function mqmOpenFiles() {
  document.body.style.cursor = "wait";
  mqmClearFilters();
  const errors = document.getElementById("mqm-errors");
  errors.innerHTML = "";
  const filesElt = document.getElementById("mqm-file");
  const numFiles = filesElt.files.length;
  if (numFiles <= 0) {
    errors.innerHTML = "No files were selected";
    return;
  }
  let erroneousFile = "";
  try {
    const filesData = [];
    let filesRead = 0;
    for (let i = 0; i < numFiles; i++) {
      filesData.push("");
      const f = filesElt.files[i];
      erroneousFile = f.name;
      const fr = new FileReader();
      fr.onload = (evt) => {
        erroneousFile = f.name;
        filesData[i] = fr.result;
        filesRead++;
        if (filesRead == numFiles) {
          mqmSetData(filesData);
        }
      };
      fr.readAsText(f);
    }
  } catch (err) {
    let errString =
      err + (errnoeousFile ? " (file with error: " + erroneousFile + ")" : "");
    errors.innerHTML = errString;
    filesElt.value = "";
  }
}

/**
 * Fetches MQM data from the given URLs and calls mqmSetData().
 * @param {!Array<string>} urls
 */
function mqmFetchUrls(urls) {
  const errors = document.getElementById("mqm-errors");
  errors.innerHTML = "Loading MQM data from " + urls.length + " URL(s)...";
  const cleanUrls = [];
  for (let url of urls) {
    const trimmedUrl = url.trim();
    if (trimmedUrl) cleanUrls.push(trimmedUrl);
  }
  if (cleanUrls.length == 0) {
    errors.innerHTML = "No non-empty URLs found";
    return;
  }
  let numResponses = 0;
  const tsvData = [];
  const finisher = () => {
    if (numResponses == cleanUrls.length) {
      mqmSetData(tsvData);
    }
  };
  for (let url of cleanUrls) {
    fetch(url, {
      mode: "cors",
      credentials: "include",
    })
      .then((response) => response.text())
      .then((result) => {
        tsvData.push(result);
        numResponses++;
        finisher();
      })
      .catch((error) => {
        errors.insertAdjacentHTML("beforeend", error);
        console.log(error);
        numResponses++;
        finisher();
      });
  }
}

/**
 * Returns the currently filtered MQM data in TSV format. The filtered
 * data is available in the mqmDataFiltered array. This function reorders
 * the columns (from "source, target, rater" to "rater, source, target")
 * before splicing them into TSV format.
 * @return {string}
 */
function mqmGetFilteredTSVData() {
  let tsvData = "";
  for (let row of mqmDataFiltered) {
    const tsvOrderedRow = [];
    for (let i = 0; i < MQM_DATA_NUM_PARTS; i++) {
      tsvOrderedRow[i] = row[i];
    }
    /** Move "Rater" up from its position in mqmDataFiltered. */
    tsvOrderedRow[4] = row[MQM_DATA_RATER];
    tsvOrderedRow[5] = row[MQM_DATA_SOURCE];
    tsvOrderedRow[6] = row[MQM_DATA_TARGET];
    tsvData += tsvOrderedRow.join("\t") + "\n";
  }
  return tsvData;
}

/**
 * Returns currently filtered scores data aggregated as specified, in TSV
 * format, with aggregation-dependent fields as follows.
 *     aggregation='system': system, score.
 *     aggregation='document': system, doc, score.
 *     aggregation='segment': system, doc, docSegId, score.
 *     aggregation='rater': system, doc, docSegId, rater, score.
 * @param {string} aggregation Should be one of:
 *     'rater', 'segment', 'document', 'system'.
 * @return {string}
 */
function mqmGetScoresTSVData(aggregation) {
  /**
   * We use a fake 10-column mqm-data array (with score kept in the last
   * column) to sort the data in the right order using mqmSortData().
   */
  const data = [];
  const FAKE_FIELD = "--MQM-FAKE-FIELD--";
  if (aggregation == "system") {
    for (let system in mqmStatsBySystem) {
      const segs = mqmGetSegStatsAsArray(mqmStatsBySystem[system]);
      aggregate = mqmAggregateSegStats(segs);
      dataRow = Array(10).fill(FAKE_FIELD);
      dataRow[MQM_DATA_SYSTEM] = system;
      dataRow[MQM_DATA_METADATA] = aggregate.score;
      data.push(dataRow);
    }
  } else if (aggregation == "document") {
    for (let system in mqmStatsBySystem) {
      const stats = mqmStatsBySystem[system];
      for (let doc in stats) {
        const docStats = stats[doc];
        const segs = mqmGetSegStatsAsArray({ doc: docStats });
        aggregate = mqmAggregateSegStats(segs);
        dataRow = Array(10).fill(FAKE_FIELD);
        dataRow[MQM_DATA_SYSTEM] = system;
        dataRow[MQM_DATA_DOC] = doc;
        dataRow[MQM_DATA_METADATA] = aggregate.score;
        data.push(dataRow);
      }
    }
  } else if (aggregation == "segment") {
    for (let system in mqmStatsBySystem) {
      const stats = mqmStatsBySystem[system];
      for (let doc in stats) {
        const docStats = stats[doc];
        for (let seg in docStats) {
          const docSegStats = docStats[seg];
          const segs = mqmGetSegStatsAsArray({ doc: { seg: docSegStats } });
          aggregate = mqmAggregateSegStats(segs);
          dataRow = Array(10).fill(FAKE_FIELD);
          dataRow[MQM_DATA_SYSTEM] = system;
          dataRow[MQM_DATA_DOC] = doc;
          dataRow[MQM_DATA_DOC_SEG_ID] = seg;
          dataRow[MQM_DATA_METADATA] = aggregate.score;
          data.push(dataRow);
        }
      }
    }
  } /* (aggregation == 'rater') */ else {
    for (let system in mqmStatsBySystemRater) {
      for (let rater in mqmStatsBySystemRater[system]) {
        const stats = mqmStatsBySystemRater[system][rater];
        for (let doc in stats) {
          const docStats = stats[doc];
          for (let seg in docStats) {
            const docSegStats = docStats[seg];
            const segs = mqmGetSegStatsAsArray({ doc: { seg: docSegStats } });
            aggregate = mqmAggregateSegStats(segs);
            dataRow = Array(10).fill(FAKE_FIELD);
            dataRow[MQM_DATA_SYSTEM] = system;
            dataRow[MQM_DATA_DOC] = doc;
            dataRow[MQM_DATA_DOC_SEG_ID] = seg;
            dataRow[MQM_DATA_RATER] = rater;
            dataRow[MQM_DATA_METADATA] = aggregate.score;
            data.push(dataRow);
          }
        }
      }
    }
  }
  mqmSortData(data);
  /** remove FAKE_FIELD columns */
  let tsvData = "";
  for (let i = 0; i < data.length; i++) {
    const trimmedRow = [];
    for (let entry of data[i]) {
      if (entry != FAKE_FIELD) {
        trimmedRow.push(entry);
      }
    }
    tsvData += trimmedRow.join("\t") + "\n";
  }
  return tsvData;
}

/**
 * Applies updated settings for scoring.
 */
function mqmUpdateSettings() {
  const unit = document.getElementById("mqm-scoring-unit").value;
  mqmCharScoring = unit == "characters";
  const unitDisplay = document.getElementById("mqm-scoring-unit-display");
  if (unitDisplay) {
    unitDisplay.innerHTML = mqmCharScoring ? "100 source chars" : "segment";
  }

  if (mqmParseScoreSettings()) {
    mqmSetUpScoreSettings();
  }
  mqmShow();
}

/**
 * Resets scoring settings to their default values.
 */
function mqmResetSettings() {
  document.getElementById("mqm-scoring-unit").value = "segments";
  mqmWeights = JSON.parse(JSON.stringify(mqmDefaultWeights));
  mqmSlices = JSON.parse(JSON.stringify(mqmDefaultSlices));
  mqmSortByField = "score";
  mqmSortByHeaderId = "mqm-score-th";
  mqmSortReverse = false;
  mqmSetUpScoreSettings();
  mqmUpdateSettings();
}

/**
 * Replaces the HTML contents of elt with the HTML needed to render the
 *     MQM Viewer. If tsvDataOrUrls is not null, then it can be MQM TSV-data,
 *     or a CSV list of URLs from which to fetch MQM TSV-data.
 * @param {!Element} elt
 * @param {string=} tsvDataOrCsvUrls
 * @param {boolean=} showFileOpener
 */
function mqmCreateViewer(elt, tsvDataOrCsvUrls = "", showFileOpener = false) {
  const tooltip =
    "Regular expressions are used case-insensitively. " +
    "Click on the Apply button after making changes.";
  let settings = `
     <details class="mqm-settings"
         title="Change scoring weights, slices, units.">
       <summary>Settings</summary>
       <div class="mqm-settings-panel">
         <div class="mqm-settings-row">
           Scoring units:
           <select id="mqm-scoring-unit" onchange="mqmUpdateSettings()">
             <option value="segments">Segments</option>
             <option value="characters">100 source characters</option>
           </select>
         </div>
         <div class="mqm-settings-row">
            Note: Changes to the following tables of weights and slices only
            take effect after clicking on <b>Apply!</b>
         </div>
         <div class="mqm-settings-row" title="${tooltip}">
           Ordered list of <i>weights</i> to apply to error patterns:
           <button onclick="mqmSettingsAddRow('mqm-settings-weights', 3)"
               >Add new row</button> as row <input type="text" maxlength="2"
               class="mqm-input"
               id="mqm-settings-weights-add-row" size=2 placeholder="1"/>
           <table class="mqm-table mqm-settings-panel">
             <thead>
               <tr>
                 <th>Weight name</th>
                 <th>Regular expression to match
                     <i>severity:category[/subcategory]</i></th>
                 <th>Weight</th>
               </tr>
             </thead>
             <tbody id="mqm-settings-weights">
             </tbody>
           </table>
         </div>
         <div class="mqm-settings-row" title="${tooltip}">
           Ordered list of interesting <i>slices</i> of error patterns:
           <button onclick="mqmSettingsAddRow('mqm-settings-slices', 2)"
               >Add new row</button> as row <input type="text" maxlength="2"
               class="mqm-input"
               id="mqm-settings-slices-add-row" size=2 placeholder="1"/>
           <table class="mqm-table mqm-settings-panel">
             <thead>
               <tr>
                 <th>Slice name</th>
                 <th>Regular expression to match
                     <i>severity:category[/subcategory]</i></th>
               </tr>
             </thead>
             <tbody id="mqm-settings-slices">
             </tbody>
           </table>
         </div>
         <div class="mqm-settings-row">
           <button id="mqm-reset-settings" title="Restore default settings"
               onclick="mqmResetSettings()">Restore defaults</button>
           <button id="mqm-apply-setttings" title="Apply weight/slice settings"
               onclick="mqmUpdateSettings()">Apply!</button>
         </div>
       </div>
     </details>`;

  let header = `
   <div class="mqm-header">
   <span class="mqm-title"></span>
     ${settings}
     <span class="mqm-header-right">`;
  if (showFileOpener) {
    header += `
       <b>Open MQM data file(s) (10-column TSV format):</b>
       <input id="mqm-file" accept=".tsv" onchange="mqmOpenFiles()"
           type="file" multiple></input>`;
  }
  header += `
     </span>
   </div>`;

  elt.innerHTML = `
   ${header}
   <div id="mqm-errors"></div>
   <table class="mqm-table mqm-numbers-table" id="mqm-stats">
     <thead id=mqm-stats-thead>
     </thead>
     <tbody id="mqm-stats-tbody">
     </tbody>
   </table>
 
   <br>
 
   <details>
     <summary
         title="Click to see a System x Rater matrix of scores highlighting individual system-rater scores that seem out of order">
       <span class="mqm-section">
         System &times; Rater scores
       </span>
     </summary>
     <table
         title="Systems and raters are sorted using total MQM score. A highlighted entry means this rater's rating of this system is contrary to the aggregate of all raters' ratings, when compared with the previous system."
         class="mqm-table mqm-numbers-table" id="mqm-system-x-rater">
     </table>
   </details>
 
   <br>
 
   <details>
     <summary
         title="Click to see a System vs System histogram of segment score differences">
       <span class="mqm-section">
         System vs System segment score differences histogram
       </span>
     </summary>
     <div class="mqm-sys-v-sys" id="mqm-sys-v-sys">
       <div class="mqm-sys-v-sys-header">
         <label>
           <b>System 1:</b>
           <select id="mqm-sys-v-sys-1" onchange="mqmShowSysVSys()"></select>
         </label>
         <span id="mqm-sys-v-sys-1-segs"></span> segment(s).
         <label>
           <b>System 2:</b>
           <select id="mqm-sys-v-sys-2" onchange="mqmShowSysVSys()"></select>
         </label>
         <span id="mqm-sys-v-sys-2-segs"></span> segment(s)
         (<span id="mqm-sys-v-sys-xsegs"></span> common).
         The Y-axis uses a log scale.
       </div>
       <svg class="mqm-sys-v-sys-plot" zoomAndPan="disable"
           id="mqm-sys-v-sys-plot">
       </svg>
     </div>
   </details>
 
   <br>
 
   <details>
     <summary title="Click to see error severity / category counts">
       <span class="mqm-section">
         Error severities and categories
       </span>
     </summary>
     <table class="mqm-table" id="mqm-sevcat-stats">
       <thead>
         <tr>
           <th title="Error severity"><b>Severity</b></th>
           <th title="Error category"><b>Category</b></th>
           <th> </th>
           <th id="mqm-sevcat-stats-th"
               title="Number of occurrences"><b>Count</b></th>
         </tr>
       </thead>
       <tbody id="mqm-sevcat-stats-tbody">
       </tbody>
     </table>
   </details>
 
   <br>
 
   <details>
     <summary title="Click to see advanced filtering options and documentation">
       <span class="mqm-section">
         Filters
         <button
             title="Clear all column filters and JavaScript filter expression"
             onclick="mqmClearFiltersAndShow()">Clear all filters</button>
       </span>
     </summary>
 
     <ul class="mqm-filters">
       <li>
         You can click on any System/Doc/ID/Rater/Category/Severity (or pick
         from the drop-down list under the column name) to set its <b>column
         filter</b> to that specific value.
       </li>
       <li>
         You can provide <b>column filter</b> regular expressions for filtering
         one or more columns, in the input fields provided under the column
         names.
       </li>
       <li>
         You can create sophisticated filters (involving multiple columns, for
         example) using a <b>JavaScript filter expression</b>:
         <br>
         <input class="mqm-input" id="mqm-filter-expr"
         title="Provide a JavaScript boolean filter expression (and press Enter)"
             onchange="mqmShow()" type="text" size="150">
         </input>
         <div id="mqm-filter-expr-error" class="mqm-filter-expr-error"></div>
         <br>
         <ul>
           <li>This allows you to filter using any expression
               involving the columns. It can use the following
               variables: <b>system</b>, <b>doc</b>, <b>globalSegId</b>,
               <b>docSegId</b>, <b>rater</b>, <b>category</b>, <b>severity</b>,
               <b>source</b>, <b>target</b>.
           </li>
           <li>
             Filter expressions also have access to an aggregated <b>segment</b>
             variable that is an object with the following properties:
             <b>segment.catsBySystem</b>,
             <b>segment.catsByRater</b>,
             <b>segment.sevsBySystem</b>,
             <b>segment.sevsByRater</b>,
             <b>segment.sevcatsBySystem</b>,
             <b>segment.sevcatsByRater</b>.
             Each of these properties is an object
             keyed by system or rater, with the values being arrays of strings.
             The "sevcats*" values look like "Minor/Fluency/Punctuation" or
             are just the same as severities if categories are empty. This
             segment-level aggregation allows you to select specific segments
             rather than just specific error ratings.
           </li>
           <li><b>Example</b>: globalSegId > 10 || severity == 'Major'</li>
           <li><b>Example</b>: target.indexOf('thethe') >= 0</li>
           <li><b>Example</b>:
             segment.sevsBySystem['System-42'].includes('Major')</li>
           <li><b>Example</b>:
             JSON.stringify(segment.sevcatsBySystem).includes('Major/Fl')</li>
           <li>
             You can add segment-level filtering clauses (AND/OR) using this
             <b>helper</b> (which uses convenient shortcut functions
             mqmIncl()/mqmExcl() for checking that a rating exists and
             has/does-not-have a value):
             <div>
               <select onchange="mqmCheckClause()"
                 id="mqm-clause-key"></select>
               <select onchange="mqmCheckClause()"
                 id="mqm-clause-inclexcl">
                 <option value="includes">has error</option>
                 <option value="excludes">does not have error</option>
               </select>
               <select onchange="mqmCheckClause()"
                 id="mqm-clause-sev"></select>
               <select onchange="mqmCheckClause()"
                 id="mqm-clause-cat"></select>
               <button onclick="mqmAddClause('&&')" disabled
                 id="mqm-clause-add-and">Add AND clause</button>
               <button onclick="mqmAddClause('||')" disabled
                 id="mqm-clause-add-or">Add OR clause</button>
             </div>
           </li>
         </ul>
         <br>
       </li>
       <li title="Limit this to at most a few thousand to avoid OOMs!">
         <b>Limit</b> the number of rows shown to:
         <input size="6" maxlength="6" type="text" id="mqm-limit" value="2000"
             onchange="setMqmLimit()">
         </input>
       </li>
     </ul>
   </details>
 
   <br>
 
   <span class="mqm-section">Rated Segments</span>
   <span id="mqm-viewing-constraints" onclick="mqmShow()"></span>
   <table class="mqm-table" id="mqm-table">
     <thead id="mqm-thead">
       <tr id="mqm-head-row">
         <th id="mqm-th-system" title="System name">
           System
           <br>
           <input class="mqm-input mqm-filter-re" id="mqm-filter-system"
               title="Provide a regexp to filter (and press Enter)"
               onchange="mqmShow()" type="text" placeholder=".*" size="10">
           </input>
           <br>
           <select onchange="mqmPick('system')"
               class="mqm-select" id="mqm-select-system"></select>
         </th>
         <th id="mqm-th-doc" title="Document name">
           Document
           <br>
           <input class="mqm-input mqm-filter-re" id="mqm-filter-doc"
               title="Provide a regexp to filter (and press Enter)"
               onchange="mqmShow()" type="text" placeholder=".*" size="10">
           </input>
           <br>
           <select onchange="mqmPick('doc')"
               class="mqm-select" id="mqm-select-doc"></select>
         </th>
         <th id="mqm-th-doc-seg-id" title="ID of the segment
             within its document">
           Local Segment
           <br>
           <input class="mqm-input mqm-filter-re" id="mqm-filter-doc-seg-id"
               title="Provide a regexp to filter (and press Enter)"
               onchange="mqmShow()" type="text" placeholder=".*" size="4">
           </input>
           <br>
           <select onchange="mqmPick('doc-seg-id')"
               class="mqm-select" id="mqm-select-doc-seg-id"></select>
         </th>
         <th id="mqm-th-global-seg-id" title="ID of the segment across
             all documents">
           Global Segment
           <br>
           <input class="mqm-input mqm-filter-re" id="mqm-filter-global-seg-id"
               title="Provide a regexp to filter (and press Enter)"
               onchange="mqmShow()" type="text" placeholder=".*" size="4">
           </input>
           <br>
           <select onchange="mqmPick('global-seg-id')"
               class="mqm-select" id="mqm-select-global-seg-id"></select>
         </th>
         <th id="mqm-th-source" title="Source text of segment">
           Source
           <br>
           <input class="mqm-input mqm-filter-re" id="mqm-filter-source"
               title="Provide a regexp to filter (and press Enter)"
               onchange="mqmShow()" type="text" placeholder=".*" size="10">
           </input>
         </th>
         <th id="mqm-th-target" title="Translated text of segment">
           Target
           <br>
           <input class="mqm-input mqm-filter-re" id="mqm-filter-target"
               title="Provide a regexp to filter (and press Enter)"
               onchange="mqmShow()" type="text" placeholder=".*" size="10">
           </input>
         </th>
         <th id="mqm-th-rater" title="Rater who evaluated">
           Rater
           <br>
           <input class="mqm-input mqm-filter-re" id="mqm-filter-rater"
               title="Provide a regexp to filter (and press Enter)"
               onchange="mqmShow()" type="text" placeholder=".*" size="10">
           </input>
           <br>
           <select onchange="mqmPick('rater')"
               class="mqm-select" id="mqm-select-rater"></select>
         </th>
         <th id="mqm-th-category" title="Error category">
           Category
           <br>
           <input class="mqm-input mqm-filter-re" id="mqm-filter-category"
               title="Provide a regexp to filter (and press Enter)"
               onchange="mqmShow()" type="text" placeholder=".*" size="10">
           </input>
           <br>
           <select onchange="mqmPick('category')"
               class="mqm-select" id="mqm-select-category"></select>
         </th>
         <th id="mqm-th-severity" title="Error severity">
           Severity
           <br>
           <input class="mqm-input mqm-filter-re" id="mqm-filter-severity"
               title="Provide a regexp to filter (and press Enter)"
               onchange="mqmShow()" type="text" placeholder=".*" size="10">
           </input>
           <br>
           <select onchange="mqmPick('severity')"
               class="mqm-select" id="mqm-select-severity"></select>
         </th>
       </tr>
     </thead>
     <tbody id="mqm-tbody">
     </tbody>
   </table>
   `;
  elt.className = "mqm";
  elt.scrollIntoView();

  mqmResetSettings();

  if (tsvDataOrCsvUrls) {
    if (tsvDataOrCsvUrls.indexOf("\t") >= 0) {
      mqmSetData(tsvDataOrCsvUrls);
    } else {
      mqmFetchUrls(tsvDataOrCsvUrls.split(","));
    }
  }
}
