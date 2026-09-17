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

      function addRow(){
        counter++;
        var html = tmpl.innerHTML.split('@@IDX@@').join(counter);
        var row = document.createElement('div');
        row.className = 'repeat-row';
        row.innerHTML = html;
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

      if(addBtn) addBtn.addEventListener('click', addRow);
      repeatGroupAdders[groupId] = addRow;
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

  document.addEventListener('DOMContentLoaded', function(){
    var form = document.getElementById('reg-form');
    if(!form) return;

    bindChoiceStyling(document);
    bindReveals(document);
    bindRepeatGroups(document);

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
