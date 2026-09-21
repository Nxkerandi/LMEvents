(function(){
  var metaEl = document.getElementById('event-meta-data');
  var dataEl = document.getElementById('registrations-data');
  if(!metaEl || !dataEl) return;

  var EVENT_META = JSON.parse(metaEl.textContent);
  var REGISTRATIONS = JSON.parse(dataEl.textContent);

  var eventInfo = {};
  EVENT_META.forEach(function(e){ eventInfo[e.short.toLowerCase()] = e; });

  var PAGE_SIZE = 25;
  var currentPage = 1;
  var activeQuickFilter = 'all';
  var sortState = { key: 'full_name', dir: 'asc' };

  function esc(value){
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function renderStats(data){
    document.getElementById('statRegistrants').textContent = data.length;
    document.getElementById('statAttending').textContent = data.reduce(function(s, r){ return s + (r.total || 0); }, 0);
    document.getElementById('statMeals').textContent = data.filter(function(r){ return r.meal; }).reduce(function(s, r){ return s + (r.total || 0); }, 0);
    document.getElementById('statChildren').textContent = data.filter(function(r){ return r.children; }).length;
  }

  function renderSessionBars(data, filterKey){
    var eventsToShow = filterKey === 'all' ? Object.keys(eventInfo) : [filterKey];
    var wrap = document.getElementById('sessionBars');
    wrap.innerHTML = eventsToShow.map(function(evKey){
      var info = eventInfo[evKey];
      if(!info) return '';
      var subset = data.filter(function(r){ return r.event_short.toLowerCase() === evKey; });
      var counts = {};
      info.session_order.forEach(function(label){ counts[label] = 0; });
      subset.forEach(function(r){
        (r.sessions || []).forEach(function(s){ counts[s] = (counts[s] || 0) + (r.total || 0); });
      });
      var max = Math.max.apply(null, Object.keys(counts).map(function(k){ return counts[k]; }).concat([1]));
      var rows = info.session_order.map(function(label){
        var count = counts[label] || 0;
        var pct = Math.round((count / max) * 100);
        return ''
          + '<div class="session-row">'
          +   '<span class="s-label">' + esc(label) + '</span>'
          +   '<span class="s-track"><span class="s-fill" style="width:' + pct + '%"></span></span>'
          +   '<span class="s-count">' + count + '</span>'
          + '</div>';
      }).join('');
      return ''
        + '<div class="event-group">'
        +   '<p class="event-group-title"><span class="event-tag ' + evKey + '">' + esc(info.short) + '</span> ' + esc(info.name) + '</p>'
        +   '<div class="session-bars-inner">' + rows + '</div>'
        + '</div>';
    }).join('');
  }

  function renderLocationBars(data){
    var wrap = document.getElementById('locationBars');
    var counts = {};
    data.forEach(function(r){
      var city = (r.city || '').trim() || 'Not provided';
      counts[city] = (counts[city] || 0) + 1;
    });
    var entries = Object.keys(counts).map(function(k){ return { label: k, count: counts[k] }; })
      .sort(function(a, b){ return b.count - a.count; });
    if(entries.length === 0){
      wrap.innerHTML = '<p class="panel-sub" style="margin:0;">No data yet.</p>';
      return;
    }
    var max = entries.reduce(function(m, e){ return Math.max(m, e.count); }, 1);
    wrap.innerHTML = entries.map(function(e){
      var pct = Math.round((e.count / max) * 100);
      return ''
        + '<div class="session-row">'
        +   '<span class="s-label">' + esc(e.label) + '</span>'
        +   '<span class="s-track"><span class="s-fill" style="width:' + pct + '%"></span></span>'
        +   '<span class="s-count">' + e.count + '</span>'
        + '</div>';
    }).join('');
  }

  function renderPagination(total){
    var wrap = document.getElementById('pagination');
    var pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));
    if(total === 0){
      wrap.innerHTML = '';
      return;
    }
    var start = (currentPage - 1) * PAGE_SIZE + 1;
    var end = Math.min(currentPage * PAGE_SIZE, total);
    wrap.innerHTML = ''
      + '<p class="page-info">Showing ' + start + '–' + end + ' of ' + total + '</p>'
      + '<div class="page-btns">'
      +   '<button type="button" class="page-btn" id="prevPageBtn"' + (currentPage <= 1 ? ' disabled' : '') + '>Previous</button>'
      +   '<button type="button" class="page-btn" id="nextPageBtn"' + (currentPage >= pageCount ? ' disabled' : '') + '>Next</button>'
      + '</div>';
    var prevBtn = document.getElementById('prevPageBtn');
    var nextBtn = document.getElementById('nextPageBtn');
    if(prevBtn) prevBtn.addEventListener('click', function(){ currentPage--; renderTable(lastFiltered); });
    if(nextBtn) nextBtn.addEventListener('click', function(){ currentPage++; renderTable(lastFiltered); });
  }

  var lastFiltered = [];

  function renderTable(data){
    lastFiltered = data;
    var body = document.getElementById('tableBody');
    var empty = document.getElementById('emptyState');
    if(data.length === 0){
      body.innerHTML = '';
      empty.style.display = 'block';
      renderPagination(0);
      return;
    }
    empty.style.display = 'none';
    var pageCount = Math.max(1, Math.ceil(data.length / PAGE_SIZE));
    if(currentPage > pageCount) currentPage = pageCount;
    var pageData = data.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);
    body.innerHTML = pageData.map(function(r){
      var sessionTags = (r.sessions || []).map(function(s){ return '<span class="tag">' + esc(s.split(', ')[0]) + '</span>'; }).join('');
      return ''
        + '<tr' + (r.cancelled ? ' class="cancelled"' : '') + '>'
        +   '<td class="name-cell">' + esc(r.full_name) + (r.cancelled ? ' <span class="badge no">Cancelled</span>' : '') + '</td>'
        +   '<td><span class="event-tag ' + r.event_short.toLowerCase() + '">' + esc(r.event_short) + '</span></td>'
        +   '<td>' + esc(r.email) + '<div class="sub-cell">' + esc(r.phone) + '</div></td>'
        +   '<td><div class="session-tags">' + sessionTags + '</div></td>'
        +   '<td class="numeric"><span class="count-pill">' + esc(r.total) + '</span></td>'
        +   '<td><span class="badge ' + (r.children ? 'yes' : 'no') + '">' + (r.children ? 'Yes' : 'No') + '</span></td>'
        +   '<td><span class="badge ' + (r.meal ? 'yes' : 'no') + '">' + (r.meal ? 'Yes' : 'No') + '</span></td>'
        +   '<td class="edit-cell"><a class="edit-link" href="/registrations/' + r.id + '/edit/">Edit</a></td>'
        + '</tr>';
    }).join('');
    renderPagination(data.length);
  }

  function sortRows(rows){
    var key = sortState.key;
    var dir = sortState.dir === 'asc' ? 1 : -1;
    var sorted = rows.slice();
    sorted.sort(function(a, b){
      var av = a[key], bv = b[key];
      if(typeof av === 'boolean') av = av ? 1 : 0;
      if(typeof bv === 'boolean') bv = bv ? 1 : 0;
      if(typeof av === 'string') av = av.toLowerCase();
      if(typeof bv === 'string') bv = bv.toLowerCase();
      if(av < bv) return -1 * dir;
      if(av > bv) return 1 * dir;
      return 0;
    });
    return sorted;
  }

  function updateSortHeaders(){
    document.querySelectorAll('th.sortable').forEach(function(th){
      var key = th.getAttribute('data-sort');
      var arrow = th.querySelector('.sort-arrow');
      if(arrow) arrow.remove();
      th.classList.toggle('sort-active', key === sortState.key);
      if(key === sortState.key){
        var span = document.createElement('span');
        span.className = 'sort-arrow';
        span.textContent = sortState.dir === 'asc' ? '↑' : '↓';
        th.appendChild(span);
      }
    });
  }

  function baseFilters(){
    var q = document.getElementById('searchInput').value.trim().toLowerCase();
    var evKey = document.getElementById('eventFilter').value;
    return REGISTRATIONS.filter(function(r){
      var matchesEvent = evKey === 'all' || r.event_short.toLowerCase() === evKey;
      var matchesSearch = !q
        || r.full_name.toLowerCase().indexOf(q) !== -1
        || r.email.toLowerCase().indexOf(q) !== -1
        || (r.city || '').toLowerCase().indexOf(q) !== -1;
      return matchesEvent && matchesSearch;
    });
  }

  function renderPillBar(){
    document.querySelectorAll('.pill-btn').forEach(function(btn){
      btn.classList.toggle('active', btn.getAttribute('data-quick-filter') === activeQuickFilter);
    });
  }

  function currentFilters(){
    var base = baseFilters();
    var evKey = document.getElementById('eventFilter').value;
    var filtered = base.filter(function(r){
      if(activeQuickFilter === 'children') return r.children;
      if(activeQuickFilter === 'meal') return r.meal;
      if(activeQuickFilter === 'cancelled') return r.cancelled;
      return true;
    });
    return { base: base, filtered: sortRows(filtered), evKey: evKey };
  }

  function refresh(){
    currentPage = 1;
    var result = currentFilters();
    // Cancelled registrations stay visible in the table (dimmed, so staff
    // can find and restore them) but never count toward stats or insight
    // bars — unless you're specifically looking at the Cancelled pill,
    // where seeing their totals is the point.
    var statsData = activeQuickFilter === 'cancelled'
      ? result.filtered
      : result.filtered.filter(function(r){ return !r.cancelled; });
    renderStats(statsData);
    renderSessionBars(statsData, result.evKey);
    renderLocationBars(statsData);
    renderPillBar();
    updateSortHeaders();
    renderTable(result.filtered);
  }

  // Deep-link support: /preparing-the-home-for-home/dashboard/?event=tn
  // pre-selects that event, e.g. from the "Dashboard" link on a specific
  // event's row in the staff events list.
  var requestedEvent = new URLSearchParams(window.location.search).get('event');
  if(requestedEvent && eventInfo[requestedEvent.toLowerCase()]){
    document.getElementById('eventFilter').value = requestedEvent.toLowerCase();
  }

  refresh();

  document.getElementById('searchInput').addEventListener('input', refresh);
  document.getElementById('eventFilter').addEventListener('change', refresh);

  document.getElementById('pillBar').addEventListener('click', function(e){
    var btn = e.target.closest('.pill-btn');
    if(!btn) return;
    activeQuickFilter = btn.getAttribute('data-quick-filter');
    refresh();
  });

  document.querySelectorAll('th.sortable').forEach(function(th){
    th.addEventListener('click', function(){
      var key = th.getAttribute('data-sort');
      if(sortState.key === key){
        sortState.dir = sortState.dir === 'asc' ? 'desc' : 'asc';
      } else {
        sortState.key = key;
        sortState.dir = 'asc';
      }
      refresh();
    });
  });

  document.getElementById('exportBtn').addEventListener('click', function(){
    var filtered = currentFilters().filtered;
    var rows = [["Event", "Name", "Email", "Phone", "City", "Sessions", "Total Attending", "Children & Youth", "Sabbath Meal", "Submitted"]];
    filtered.forEach(function(r){
      var info = eventInfo[r.event_short.toLowerCase()];
      rows.push([
        info ? info.name : r.event_short, r.full_name, r.email, r.phone, r.city || '',
        (r.sessions || []).join(' | '), r.total,
        r.children ? 'Yes' : 'No', r.meal ? 'Yes' : 'No', r.submitted,
      ]);
    });
    var csv = rows.map(function(row){
      return row.map(function(v){ return '"' + String(v == null ? '' : v).replace(/"/g, '""') + '"'; }).join(',');
    }).join('\n');
    var blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = 'preparing-the-home-for-home-registrations.csv';
    a.click();
    URL.revokeObjectURL(url);
  });
})();
