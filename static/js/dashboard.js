(function(){
  var dataEl = document.getElementById('registrations-data');
  var metaEl = document.getElementById('questions-meta');
  if(!dataEl || !metaEl) return;

  var REGISTRATIONS = JSON.parse(dataEl.textContent);
  var QUESTIONS = JSON.parse(metaEl.textContent);

  var insightQuestions = QUESTIONS.filter(function(q){ return q.show_in_insights; });
  var filterQuestions = QUESTIONS.filter(function(q){ return q.quick_filter; });
  var tableQuestions = QUESTIONS.filter(function(q){ return q.show_in_table; });

  var activeFilter = 'all';
  var searchTerm = '';
  var openId = null;

  function questionById(id){
    return QUESTIONS.filter(function(q){ return String(q.id) === String(id); })[0];
  }

  // Registration-supplied values (names, free-text answers, city, etc.) get
  // concatenated into innerHTML throughout this file — escape at every such
  // insertion point so a malicious answer renders as inert text instead of
  // being parsed as HTML/script. Never skip this for "internal" values
  // either (question labels, option labels) — cheap, and removes the whole
  // bug class rather than relying on guessing which fields are trusted.
  function esc(value){
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function badge(value){
    if(value === 'Yes') return '<span class="badge yes">Yes</span>';
    if(value === 'No') return '<span class="badge no">No</span>';
    return '<span class="badge no">—</span>';
  }

  // ---- Insights: one bar-chart card per question flagged show_in_insights ----
  function computeDistribution(question){
    var counts = {};

    if(question.type === 'repeatable_group'){
      var subq = (question.sub_questions || []).filter(function(s){ return s.type === 'single_choice'; })[0];
      if(!subq) return [];
      (subq.options || []).forEach(function(o){ counts[o.label] = 0; });
      REGISTRATIONS.forEach(function(r){
        (r.answers[question.id] || []).forEach(function(row){
          var val = row[subq.id];
          if(val) counts[val] = (counts[val] || 0) + 1;
        });
      });
    } else if(question.type === 'multi_choice'){
      (question.options || []).forEach(function(o){ counts[o.label] = 0; });
      REGISTRATIONS.forEach(function(r){
        (r.answers[question.id] || []).forEach(function(v){ counts[v] = (counts[v] || 0) + 1; });
      });
    } else if(question.type === 'single_choice' || question.type === 'boolean'){
      if(question.type === 'boolean'){ counts['Yes'] = 0; counts['No'] = 0; }
      else (question.options || []).forEach(function(o){ counts[o.label] = 0; });
      REGISTRATIONS.forEach(function(r){
        var v = r.answers[question.id];
        if(v) counts[v] = (counts[v] || 0) + 1;
      });
    } else {
      REGISTRATIONS.forEach(function(r){
        var v = (r.answers[question.id] || '').toString().trim() || 'Not provided';
        counts[v] = (counts[v] || 0) + 1;
      });
    }

    return Object.keys(counts).map(function(k){ return { label: k, count: counts[k] }; })
      .sort(function(a, b){ return b.count - a.count; });
  }

  function renderBars(entries){
    var max = entries.reduce(function(m, e){ return Math.max(m, e.count); }, 1);
    return entries.map(function(e){
      var pct = Math.round((e.count / max) * 100);
      return ''
        + '<div class="bar-row">'
        +   '<div class="bar-name">' + esc(e.label) + '</div>'
        +   '<div class="bar-track"><div class="bar-fill" style="width:' + pct + '%;"></div></div>'
        +   '<div class="bar-count">' + e.count + '</div>'
        + '</div>';
    }).join('');
  }

  function renderInsights(){
    var container = document.getElementById('insights');
    if(!insightQuestions.length){
      container.innerHTML = '';
      return;
    }
    container.innerHTML = insightQuestions.map(function(q){
      var entries = computeDistribution(q);
      var body = entries.length ? renderBars(entries) : '<p class="insight-sub" style="margin:0;">No data yet.</p>';
      return ''
        + '<div class="insight-card">'
        +   '<h2>' + esc(q.short_label) + '</h2>'
        +   '<p class="insight-sub">Across all registrations.</p>'
        +   body
        + '</div>';
    }).join('');
  }

  // ---- Stats ----
  var hasChildrenGroup = QUESTIONS.some(function(q){ return q.type === 'repeatable_group' && q.counts_as_attendees; });
  var headcountFilterQuestions = QUESTIONS.filter(function(q){ return q.quick_filter && q.quick_filter_sums_attendees; });

  function renderStats(){
    var households = REGISTRATIONS.length;
    var attendees = REGISTRATIONS.reduce(function(sum, r){ return sum + (r.attendee_count || 0); }, 0);
    var children = REGISTRATIONS.reduce(function(sum, r){ return sum + (r.child_count || 0); }, 0);

    var stats = [
      { value: households, label: 'Registrations' },
      { value: attendees, label: 'Total attendees' },
    ];
    if(hasChildrenGroup){
      stats.push({ value: children, label: 'Total children' });
    }
    headcountFilterQuestions.forEach(function(q){
      stats.push({ value: quickFilterCount(q), label: q.short_label });
    });

    document.getElementById('stats').innerHTML = stats.map(function(s){
      return '<div class="stat-card"><div class="value">' + esc(s.value) + '</div><div class="stat-label">' + esc(s.label) + '</div></div>';
    }).join('');
  }

  // ---- Filtering / search ----
  function matchesQuickFilter(r, q){
    var v = r.answers[q.id];
    if(q.type === 'boolean' || q.type === 'single_choice') return v === 'Yes';
    if(Array.isArray(v)) return v.length > 0;
    return !!v;
  }

  function matchesFilter(r){
    if(activeFilter === 'all') return true;
    var q = questionById(activeFilter);
    return q ? matchesQuickFilter(r, q) : true;
  }

  function matchesSearch(r){
    if(!searchTerm) return true;
    var haystack = [r.full_name, r.email, r.phone];
    QUESTIONS.forEach(function(q){
      var v = r.answers[q.id];
      if(typeof v === 'string') haystack.push(v);
    });
    return haystack.join(' ').toLowerCase().indexOf(searchTerm.toLowerCase()) !== -1;
  }

  // ---- Table cell + detail rendering ----
  function cellValue(r, q){
    var v = r.answers[q.id];
    if(q.type === 'repeatable_group') return (v || []).length + '';
    if(q.type === 'multi_choice') return (v || []).length + ' of ' + (q.options || []).length;
    if(q.type === 'boolean') return badge(v);
    if(Array.isArray(v)) return esc(v.join(', '));
    return esc(v || '—');
  }

  function detailValue(r, q){
    if(q.type === 'repeatable_group'){
      var rows = r.answers[q.id] || [];
      if(!rows.length) return '<span class="v">—</span>';
      var chips = rows.map(function(row){
        var parts = (q.sub_questions || []).map(function(sq){ return row[sq.id]; }).filter(Boolean);
        return '<span class="chip">' + esc(parts.join(' · ')) + '</span>';
      }).join('');
      return '<div class="chips">' + chips + '</div>';
    }
    if(q.type === 'multi_choice'){
      var vals = r.answers[q.id] || [];
      if(!vals.length) return '<span class="v">—</span>';
      return '<div class="chips">' + vals.map(function(v){ return '<span class="chip">' + esc(v) + '</span>'; }).join('') + '</div>';
    }
    if(q.type === 'boolean') return '<p class="v">' + badge(r.answers[q.id]) + '</p>';
    return '<p class="v">' + esc(r.answers[q.id] || '—') + '</p>';
  }

  function renderDetail(r){
    var items = [
      { k: 'Email', html: '<p class="v">' + esc(r.email) + '</p>' },
      { k: 'Phone', html: '<p class="v">' + esc(r.phone) + '</p>' },
    ];
    QUESTIONS.forEach(function(q){
      items.push({ k: q.label, html: detailValue(r, q) });
    });
    return items.map(function(item){
      var wide = item.html.indexOf('chips') !== -1;
      return '<div class="detail-item"' + (wide ? ' style="grid-column: 1 / -1;"' : '') + '><p class="k">' + esc(item.k) + '</p>' + item.html + '</div>';
    }).join('');
  }

  function renderTable(){
    var filtered = REGISTRATIONS.filter(function(r){ return matchesFilter(r) && matchesSearch(r); });

    document.getElementById('result-count').textContent =
      filtered.length + (filtered.length === 1 ? ' registration' : ' registrations') + ' shown';

    var headEl = document.getElementById('table-head');
    headEl.innerHTML = '<div class="cell name">Name</div><div class="cell">Attendees</div>'
      + tableQuestions.map(function(q){ return '<div class="cell">' + esc(q.short_label) + '</div>'; }).join('')
      + '<div class="cell">Submitted</div><div style="width:20px;"></div>';

    if(!filtered.length){
      document.getElementById('table-body').innerHTML = '<div class="empty-state">No registrations match your search or filter.</div>';
      return;
    }

    document.getElementById('table-body').innerHTML = filtered.map(function(r){
      var isOpen = openId === r.id;
      return ''
        + '<div class="row' + (isOpen ? ' open' : '') + '" data-id="' + r.id + '">'
        +   '<div class="cell name" data-label="Name"><span class="cell-value">' + esc(r.full_name) + '<span class="sub-email">' + esc(r.email) + '</span></span></div>'
        +   '<div class="cell" data-label="Attendees"><span class="cell-value">' + esc(r.attendee_count) + '</span></div>'
        +   tableQuestions.map(function(q){
              return '<div class="cell" data-label="' + esc(q.short_label) + '"><span class="cell-value">' + cellValue(r, q) + '</span></div>';
            }).join('')
        +   '<div class="cell" data-label="Submitted"><span class="cell-value">' + esc(r.submitted) + '</span></div>'
        +   '<div class="chevron"></div>'
        + '</div>'
        + '<div class="detail' + (isOpen ? ' open' : '') + '" id="detail-' + r.id + '"><div><div class="detail-inner">' + renderDetail(r) + '</div></div></div>';
    }).join('');

    document.querySelectorAll('.row').forEach(function(rowEl){
      rowEl.addEventListener('click', function(){
        var id = Number(rowEl.getAttribute('data-id'));
        openId = openId === id ? null : id;
        renderTable();
      });
    });
  }

  function quickFilterCount(q){
    var matching = REGISTRATIONS.filter(function(r){ return matchesQuickFilter(r, q); });
    return q.quick_filter_sums_attendees
      ? matching.reduce(function(sum, r){ return sum + (r.attendee_count || 0); }, 0)
      : matching.length;
  }

  function renderFilterPills(){
    var container = document.getElementById('filters');
    var pills = ['<button class="filter-btn active" data-filter="all">All (' + REGISTRATIONS.length + ')</button>']
      .concat(filterQuestions.map(function(q){
        return '<button class="filter-btn" data-filter="' + esc(q.id) + '">' + esc(q.short_label) + ' (' + quickFilterCount(q) + ')</button>';
      }));
    container.innerHTML = pills.join('');

    container.querySelectorAll('.filter-btn').forEach(function(btn){
      btn.addEventListener('click', function(){
        container.querySelectorAll('.filter-btn').forEach(function(b){ b.classList.remove('active'); });
        btn.classList.add('active');
        activeFilter = btn.getAttribute('data-filter');
        renderTable();
      });
    });
  }

  document.getElementById('search-input').addEventListener('input', function(e){
    searchTerm = e.target.value;
    renderTable();
  });

  document.getElementById('clear-btn').addEventListener('click', function(){
    document.getElementById('search-input').value = '';
    searchTerm = '';
    activeFilter = 'all';
    document.querySelectorAll('.filter-btn').forEach(function(b){ b.classList.remove('active'); });
    document.querySelector('.filter-btn[data-filter="all"]').classList.add('active');
    renderTable();
  });

  renderStats();
  renderInsights();
  renderFilterPills();
  renderTable();
})();
