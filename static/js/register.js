(function(){
  // ---- Checked-state styling for choice pills/boxes ----
  function syncChoice(input){
    var wrapper = input.closest('.choice') || input.closest('.pill');
    if(!wrapper) return;
    if(input.type === 'radio'){
      document.querySelectorAll('input[name="' + CSS.escape(input.name) + '"]').forEach(function(r){
        var w = r.closest('.choice') || r.closest('.pill');
        if(w) w.classList.toggle('is-checked', r.checked);
      });
    } else {
      wrapper.classList.toggle('is-checked', input.checked);
    }
  }

  function bindChoiceStyling(root){
    root.querySelectorAll('.choice input, .pill input').forEach(function(input){
      input.addEventListener('change', function(){ syncChoice(input); });
    });
  }

  // ---- Conditional reveal: any field can depend on a prior boolean/choice question ----
  var repeatGroupAdders = {};

  function updateReveals(questionId, value){
    document.querySelectorAll('[data-depends-on="' + questionId + '"]').forEach(function(revealEl){
      var match = revealEl.getAttribute('data-depends-value') === value;
      revealEl.classList.toggle('open', match);

      // The reveal hides content via a 0-height/overflow:hidden wrapper,
      // not display:none — so a required field inside a closed reveal is
      // still "rendered" as far as the browser's native validation is
      // concerned, and silently blocks submission with no visible error
      // near an invisible field. Toggle `required` itself to match.
      revealEl.querySelectorAll('input, select, textarea').forEach(function(field){
        if(match){
          if(field.dataset.wasRequired === 'true') field.required = true;
        } else {
          if(field.required){ field.dataset.wasRequired = 'true'; field.required = false; }
        }
      });

      var container = revealEl.querySelector('[data-repeat-rows]');
      if(match){
        var groupId = revealEl.getAttribute('data-question-id');
        if(container && container.children.length === 0 && repeatGroupAdders[groupId]){
          repeatGroupAdders[groupId]();
        }
      } else if(container){
        container.innerHTML = '';
      }
    });
  }

  function bindReveals(root){
    root.querySelectorAll('[data-controls-reveal]').forEach(function(input){
      input.addEventListener('change', function(){
        updateReveals(input.getAttribute('data-question-id'), input.value);
      });
    });
    // initial state (e.g. re-rendering after a server-side validation error)
    root.querySelectorAll('[data-controls-reveal]:checked').forEach(function(input){
      updateReveals(input.getAttribute('data-question-id'), input.value);
    });
    // Any reveal still closed at this point (nothing checked yet, or this
    // question wasn't answered on a re-render after an error elsewhere in
    // the form) must not leave a required-but-hidden field able to
    // silently block submission.
    root.querySelectorAll('.reveal:not(.open)').forEach(function(revealEl){
      revealEl.querySelectorAll('input, select, textarea').forEach(function(field){
        if(field.required){ field.dataset.wasRequired = 'true'; field.required = false; }
      });
    });
  }

  // ---- Repeatable groups: clone a <template> row, wire remove buttons ----
  function bindRepeatGroups(root){
    root.querySelectorAll('[data-repeat-group]').forEach(function(groupEl){
      var groupId = groupEl.getAttribute('data-question-id');
      var container = groupEl.querySelector('[data-repeat-rows]');
      var tmpl = document.getElementById('tmpl-' + groupId);
      var addBtn = groupEl.querySelector('.add-row-btn');
      var counter = 0;

      function updateRemoveVisibility(){
        var rows = container.querySelectorAll('.repeat-row');
        rows.forEach(function(row){
          var btn = row.querySelector('.remove-row-btn');
          if(btn) btn.style.visibility = rows.length > 1 ? 'visible' : 'hidden';
        });
      }

      function addRow(prefillRow){
        counter++;
        var html = tmpl.innerHTML.split('@@IDX@@').join(counter);
        var row = document.createElement('div');
        row.className = 'repeat-row';
        row.innerHTML = html;
        if(prefillRow){
          row.querySelectorAll('input').forEach(function(input){
            var m = /^q_(\d+)_/.exec(input.name);
            if(!m) return;
            var value = prefillRow[m[1]];
            if(value == null) return;
            if(input.type === 'radio'){
              if(input.value === value) input.checked = true;
            } else {
              input.value = value;
            }
          });
          row.querySelectorAll('input:checked').forEach(syncChoice);
        }
        var removeBtn = row.querySelector('.remove-row-btn');
        if(removeBtn){
          removeBtn.addEventListener('click', function(){
            row.remove();
            updateRemoveVisibility();
          });
        }
        container.appendChild(row);
        bindChoiceStyling(row);
        updateRemoveVisibility();
      }

      if(addBtn) addBtn.addEventListener('click', function(){ addRow(); });
      repeatGroupAdders[groupId] = addRow;
    });
  }

  // ---- Pre-fill repeatable-group rows on the edit-registration page ----
  function prefillRepeatGroups(){
    var dataEl = document.getElementById('existing-repeat-rows');
    if(!dataEl) return;
    var answers = JSON.parse(dataEl.textContent);
    Object.keys(repeatGroupAdders).forEach(function(groupId){
      var rows = answers[groupId];
      if(!Array.isArray(rows) || !rows.length) return;
      rows.forEach(function(row){ repeatGroupAdders[groupId](row); });
    });
  }

  // ---- Required checkbox-group / repeatable-group validation on submit ----
  function validateRequiredGroups(form){
    var ok = true;
    form.querySelectorAll('.field[data-required-group]').forEach(function(fieldEl){
      var visible = fieldEl.offsetParent !== null;
      if(!visible){
        fieldEl.classList.remove('has-error');
        return;
      }
      var checked = fieldEl.querySelectorAll('input[type="checkbox"]:checked');
      var valid = checked.length > 0;
      fieldEl.classList.toggle('has-error', !valid);
      if(!valid) ok = false;
    });
    form.querySelectorAll('[data-repeat-group][data-required-group]').forEach(function(groupEl){
      var visible = groupEl.offsetParent !== null;
      if(!visible){
        groupEl.classList.remove('has-error');
        return;
      }
      var rows = groupEl.querySelectorAll('.repeat-row');
      var valid = rows.length > 0;
      groupEl.classList.toggle('has-error', !valid);
      if(!valid) ok = false;
    });
    return ok;
  }

  // ---- Live running total next to a quantity field (e.g. "$10 per meal") ----
  function bindCostTotals(root){
    root.querySelectorAll('input[data-cost-per-unit]').forEach(function(input){
      var rate = parseFloat(input.getAttribute('data-cost-per-unit')) || 0;
      var totalEl = root.querySelector('.cost-total[data-cost-for="' + input.id + '"]');
      if(!totalEl) return;
      function update(){
        var qty = parseInt(input.value, 10);
        var total = (isNaN(qty) || qty < 0) ? 0 : qty * rate;
        totalEl.textContent = 'Total: $' + total.toFixed(2);
      }
      input.addEventListener('input', update);
      update();
    });
  }

  document.addEventListener('DOMContentLoaded', function(){
    var form = document.getElementById('reg-form');
    if(!form) return;

    bindChoiceStyling(document);
    bindRepeatGroups(document);
    prefillRepeatGroups();
    bindReveals(document);
    bindCostTotals(document);

    form.addEventListener('submit', function(e){
      if(!validateRequiredGroups(form)){
        e.preventDefault();
        var firstError = form.querySelector('.has-error');
        if(firstError) firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
      }
      var btn = form.querySelector('button.submit');
      if(btn){
        btn.disabled = true;
        btn.textContent = 'Submitting…';
      }
    });
  });
})();
