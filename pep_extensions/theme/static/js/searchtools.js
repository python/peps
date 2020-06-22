/*
 * searchtools.js
 * ~~~~~~~~~~~~~~~~
 *
 * Sphinx JavaScript utilities for the full-text search.
 *
 * :copyright: Copyright 2007-2020 by the Sphinx team, see AUTHORS.
 * :license: BSD, see LICENSE for details.
 *
 */


/**
 * Simple result scoring code.
 */
const Scorer = {
  // Implement the following function to further tweak the score for each result
  // The function takes a result array [filename, title, anchor, descr, score]
  // and returns the new score.
  /*
  score: function(result) {
    return result[4];
  },
  */

  // query matches the full name of an object
  objNameMatch: 11,
  // or matches in the last dotted part of the object name
  objPartialMatch: 6,
  // Additive scores depending on the priority of the object
  objPrio: {0:  15,   // used to be importantResults
            1:  5,   // used to be objectResults
            2: -5},  // used to be unimportantResults
  //  Used when the priority is not in the mapping.
  objPrioDefault: 0,

  // query found in title
  title: 15,
  partialTitle: 7,
  // query found in terms
  term: 5,
  partialTerm: 2
};


if (!splitQuery) {
  function splitQuery(query) {
    return query.split(/\s+/);
  }
}


const removeChildren = (elm) => {
  while (elm.lastChild) {
    elm.removeChild(elm.lastChild);
  }
}
/**
 * Search Module
 */
const Search = {

  _index: null,
  _queued_query: null,
  _pulse_status: -1,

  htmlToText: function (htmlString) {
    const htmlElement = document.createElement('span');
    htmlElement.innerHTML = htmlString;
    removeElements(htmlElement.getElementsByClassName('headerlink'));
    const docContent = htmlElement.querySelector('[role="main"]');
    if (docContent === undefined) {
      console.warn("Content block not found. Sphinx search tries to obtain it " +
          "via '[role=main]'. Could you check your theme or template.");
      return "";
    }
    return docContent.textContent || docContent.innerText;
  },

  init: function () {
    const urlParams = new URLSearchParams(window.location.search);
    const query = urlParams.get("q");
    if (query) {
      document.querySelector('input[name="q"]').value = query;
      this.performSearch(query);
    }
  },

  setIndex: function (index) {
    let q;
    this._index = index;
    if ((q = this._queued_query) !== null) {
      this._queued_query = null;
      Search.query(q);
    }
  },

  hasIndex: function () {
    return this._index !== null;
  },

  deferQuery: function (query) {
    this._queued_query = query;
  },

  stopPulse: function () {
    this._pulse_status = 0;
  },

  startPulse: function () {
    if (this._pulse_status >= 0)
      return;

    function pulse() {
      let i;
      Search._pulse_status = (Search._pulse_status + 1) % 4;
      let dotString = '';
      for (i = 0; i < Search._pulse_status; i++)
        dotString += '.';
      Search.dots.innerText = dotString;
      if (Search._pulse_status > -1)
        window.setTimeout(pulse, 500);
    }

    pulse();
  },

  /**
   * perform a search for something (or wait until index is loaded)
   */
  performSearch: function (query) {
    const dotsSpan = document.createElement("span");
    const searchText = document.createElement("h2");
    searchText.textContent = _('Searching');
    const searchSummary = document.createElement("p");
    searchSummary.classList.add("search-summary")
    searchSummary.innerText = ""
    const searchList = document.createElement("ul");
    searchList.classList.add("search")

    // create the required interface elements
    this.out = document.getElementById("search-results");
    this.title = this.out.appendChild(searchText);
    this.dots = this.title.appendChild(dotsSpan)
    this.status = this.out.appendChild(searchSummary);
    this.output = this.out.appendChild(searchList);

    document.getElementById("search-progress").innerText = _('Preparing search...')
    this.startPulse();

    // index already loaded, the browser was quick!
    if (this.hasIndex())
      this.query(query);
    else
      this.deferQuery(query);
  },

  /**
   * execute search (requires search index to be loaded)
   */
  query: function (query) {
    let i;

    // stem the searchterms and add them to the correct list
    const stemmer = new Stemmer();
    const searchterms = [];
    const excluded = [];
    const hlterms = [];
    const tmp = splitQuery(query);
    const objectterms = [];
    for (i = 0; i < tmp.length; i++) {
      if (tmp[i] !== "") {
        objectterms.push(tmp[i].toLowerCase());
      }

      // stopwords array is from language_data.js
      if (stopwords.indexOf(tmp[i].toLowerCase()) !== -1 || tmp[i].match(/^\d+$/) ||
          tmp[i] === "") {
        // skip this "word"
        continue;
      }
      // stem the word
      let word = stemmer.stemWord(tmp[i].toLowerCase());
      // prevent stemmer from cutting word smaller than two chars
      if (word.length < 3 && tmp[i].length >= 3) {
        word = tmp[i];
      }
      let toAppend;
      // select the correct list
      if (word[0] === '-') {
        toAppend = excluded;
        word = word.substr(1);
      } else {
        toAppend = searchterms;
        hlterms.push(tmp[i].toLowerCase());
      }
      // only add if not already in the list
      if (!toAppend.includes(word))
        toAppend.push(word);
    }
    const highlightstring = '?highlight=' + encodeURIComponent(hlterms.join(" "));

    // console.debug('SEARCH: searching for:');
    // console.info('required: ', searchterms);
    // console.info('excluded: ', excluded);

    // prepare search
    const terms = this._index.terms;
    const titleterms = this._index.titleterms;

    // array of [filename, title, anchor, descr, score]
    let results = [];
    removeChildren(document.getElementById("search-progress"))

    // lookup as object
    for (i = 0; i < objectterms.length; i++) {
      const others = [].concat(objectterms.slice(0, i),
          objectterms.slice(i + 1, objectterms.length));
      results = results.concat(this.performObjectSearch(objectterms[i], others));
    }

    // lookup as search terms in fulltext
    results = results.concat(this.performTermsSearch(searchterms, excluded, terms, titleterms));

    // let the scorer override scores with a custom scoring function
    if (Scorer.score) {
      for (i = 0; i < results.length; i++)
        results[i][4] = Scorer.score(results[i]);
    }

    // now sort the results by score (in opposite order of appearance, since the
    // display function below uses pop() to retrieve items) and then
    // alphabetically
    results.sort(function (a, b) {
      let left = a[4];
      let right = b[4];
      if (left > right) {
        return 1;
      } else if (left < right) {
        return -1;
      } else {
        // same score: sort alphabetically
        left = a[1].toLowerCase();
        right = b[1].toLowerCase();
        return (left > right) ? -1 : ((left < right) ? 1 : 0);
      }
    });

    // for debugging
    //Search.lastresults = results.slice();  // a copy
    //console.info('search results:', Search.lastresults);

    const resultCount = results.length

    function displayNextItem() {
      const doc_builder = DOCUMENTATION_OPTIONS.BUILDER
      const docUrlRoot = DOCUMENTATION_OPTIONS.URL_ROOT
      const docFileSuffix = DOCUMENTATION_OPTIONS.FILE_SUFFIX
      const docLinkSuffix = DOCUMENTATION_OPTIONS.LINK_SUFFIX
      const docHasSource = DOCUMENTATION_OPTIONS.HAS_SOURCE

      // results left, load the summary and display it
      // this is intended to be dynamic (don't sub resultsCount)
      if (results.length) {
        const item = results.pop();

        let listItem = document.createElement("li")
        let requestUrl = "";
        let linkUrl = "";
        if (doc_builder === 'dirhtml') {
          // dirhtml builder
          let dirname = item[0] + '/';
          if (dirname.match(/\/index\/$/)) {
            dirname = dirname.substring(0, dirname.length - 6);
          } else if (dirname === 'index/') {
            dirname = '';
          }
          requestUrl = docUrlRoot + dirname;
          linkUrl = requestUrl;

        } else {
          // normal html builders
          requestUrl = docUrlRoot + item[0] + docFileSuffix;
          linkUrl = item[0] + docLinkSuffix;
        }
        let linkEl = document.createElement("a")
        linkEl.href = linkUrl + highlightstring + item[2]
        linkEl.innerHTML = item[1]
        listItem.appendChild(linkEl)
        if (item[3]) {
          let spanEl = document.createElement("span")
          spanEl.innerText = " (" + item[3] + ')'
          listItem.appendChild(spanEl)
          Search.output.appendChild(listItem);
          setTimeout(() => displayNextItem(), 5)
        } else if (docHasSource) {
          fetch(requestUrl)
              .then(responseData => responseData.text())
              .then(data => {
                if (data !== '' && data !== undefined) {
                  listItem.appendChild(Search.makeSearchSummary(data, searchterms, hlterms));
                }
                Search.output.appendChild(listItem);
                setTimeout(() => displayNextItem(), 5)
              })
        } else {
          // no source available, just display title
          Search.output.appendChild(listItem);
          setTimeout(() => displayNextItem(), 5)
        }
      }
      // search finished, update title and status message
      else {
        Search.stopPulse();
        Search.title.innerText = _('Search Results');
        if (!resultCount)
          Search.status.innerText = _('Your search did not match any documents. Please make sure that all words are spelled correctly and that you\'ve selected enough categories.');
        else
          Search.status.innerText = _('Search finished, found %s page(s) matching the search query.').replace('%s', resultCount);
      }
    }
    displayNextItem();
  },

  /**
   * search for object names
   */
  performObjectSearch: function (object, otherterms) {
    const filenames = this._index.filenames;
    const docnames = this._index.docnames;
    const objects = this._index.objects;
    const objnames = this._index.objnames;
    const titles = this._index.titles;

    let i;
    const results = [];

    for (let prefix in objects) {
      for (let name in objects[prefix]) {
        const fullname = (prefix ? prefix + '.' : '') + name;
        const fullnameLower = fullname.toLowerCase();
        if (fullnameLower.indexOf(object) > -1) {
          let score = 0;
          const parts = fullnameLower.split('.');
          // check for different match types: exact matches of full name or
          // "last name" (i.e. last dotted part)
          if (fullnameLower == object || parts[parts.length - 1] == object) {
            score += Scorer.objNameMatch;
            // matches in last name
          } else if (parts[parts.length - 1].indexOf(object) > -1) {
            score += Scorer.objPartialMatch;
          }
          const match = objects[prefix][name];
          const objname = objnames[match[1]][2];
          const title = titles[match[0]];
          // If more than one term searched for, we require other words to be
          // found in the name/title/description
          if (otherterms.length > 0) {
            const haystack = (prefix + ' ' + name + ' ' +
                objname + ' ' + title).toLowerCase();
            let allfound = true;
            for (i = 0; i < otherterms.length; i++) {
              if (haystack.indexOf(otherterms[i]) == -1) {
                allfound = false;
                break;
              }
            }
            if (!allfound) {
              continue;
            }
          }
          const descr = objname + _(', in ') + title;

          let anchor = match[3];
          if (anchor === '')
            anchor = fullname;
          else if (anchor == '-')
            anchor = objnames[match[1]][1] + '-' + fullname;
          // add custom score for some objects according to scorer
          if (Scorer.objPrio.hasOwnProperty(match[2])) {
            score += Scorer.objPrio[match[2]];
          } else {
            score += Scorer.objPrioDefault;
          }
          results.push([docnames[match[0]], fullname, '#' + anchor, descr, score, filenames[match[0]]]);
        }
      }
    }

    return results;
  },

  /**
   * search for full-text terms in the index
   */
  performTermsSearch: function (searchterms, excluded, terms, titleterms) {
    const docnames = this._index.docnames;
    const filenames = this._index.filenames;
    const titles = this._index.titles;

    let i, j, file;
    const fileMap = {};
    const scoreMap = {};
    const results = [];

    // perform the search on the required terms
    for (i = 0; i < searchterms.length; i++) {
      const word = searchterms[i];
      let files = [];
      const _o = [
        {files: terms[word], score: Scorer.term},
        {files: titleterms[word], score: Scorer.title}
      ];
      // add support for partial matches
      if (word.length > 2) {
        let w;
        for (w in terms) {
          if (w.match(word) && !terms[word]) {
            _o.push({files: terms[w], score: Scorer.partialTerm})
          }
        }
        for (w in titleterms) {
          if (w.match(word) && !titleterms[word]) {
            _o.push({files: titleterms[w], score: Scorer.partialTitle})
          }
        }
      }

      // no match but word was a required one
      if (_o.every(o => o.files === undefined)) {
        break;
      }
      // found search word in contents
      _o.forEach(o => {
        let _files = o.files;
        if (_files === undefined)
          return

        if (_files.length === undefined)
          _files = [_files];
        files = files.concat(_files);

        // set score for the word in each file to Scorer.term
        for (j = 0; j < _files.length; j++) {
          file = _files[j];
          if (!(file in scoreMap))
            scoreMap[file] = {};
          scoreMap[file][word] = o.score;
        }
      });

      // create the mapping
      for (j = 0; j < files.length; j++) {
        file = files[j];
        if (file in fileMap && fileMap[file].indexOf(word) === -1)
          fileMap[file].push(word);
        else
          fileMap[file] = [word];
      }
    }

    // now check if the files don't contain excluded terms
    for (file in fileMap) {
      let valid = true;

      // check if all requirements are matched
      const filteredTermCount = // as search terms with length < 3 are discarded: ignore
          searchterms.filter(function (term) {
            return term.length > 2
          }).length;
      if (
          fileMap[file].length != searchterms.length &&
          fileMap[file].length != filteredTermCount
      ) continue;

      // ensure that none of the excluded terms is in the search result
      for (i = 0; i < excluded.length; i++) {
        if (terms[excluded[i]] === file ||
            titleterms[excluded[i]] === file ||
            (terms[excluded[i]] || []).includes(file) ||
            (titleterms[excluded[i]] || []).includes(file)) {
          valid = false;
          break;
        }
      }

      // if we have still a valid result we can add it to the result list
      if (valid) {
        // select one (max) score for the file.
        // for better ranking, we should calculate ranking by using words statistics like basic tf-idf...
        const score = Math.max(...fileMap[file].map(w => scoreMap[file][w]))
        results.push([docnames[file], titles[file], '', null, score, filenames[file]]);
      }
    }
    return results;
  },

  /**
   * helper function to return a node containing the
   * search summary for a given text. keywords is a list
   * of stemmed words, hlwords is the list of normal, unstemmed
   * words. the first one is used to find the occurrence, the
   * latter for highlighting it.
   */
  makeSearchSummary: function (htmlText, keywords, hlwords) {
    const text = Search.htmlToText(htmlText);
    const textLower = text.toLowerCase();
    let start = 0;
    keywords.forEach(keyword => {
      const i = textLower.indexOf(keyword.toLowerCase());
      if (i > -1)
        start = i;
    })
    start = Math.max(start - 120, 0);
    const excerpt = ((start > 0) ? '...' : '') +
        text.substr(start, 240).trim() +
        ((start + 240 - text.length) ? '...' : '');
    let contextEl = document.createElement("div")
    contextEl.classList.add("context")
    contextEl.innerText = excerpt
    hlwords.forEach(hlword => {
      contextEl = highlightText(hlword, 'highlighted', contextEl);
    })
    return contextEl;
  }
};

ready(() => {
  Search.init();
});
