/**
 * plugins/forms/index.js — Forms plugin.
 * Adds a contact form block and injects form handling script.
 */
'use strict';

const FormsPlugin = {
  id:      'forms',
  name:    'Forms',
  version: '1.0.0',

  settings: {
    endpoint:    '',      // POST endpoint for form submissions
    success_msg: 'Thank you! We\'ll be in touch.',
    error_msg:   'Something went wrong. Please try again.',
  },

  hooks: {
    afterRender(ctx) {
      if (!ctx.html) return;
      const s = ctx._pluginSettings?.forms || {};
      if (!s.endpoint) return;
      // Inject lightweight form handler
      const script = `<script>
(function(){
  document.querySelectorAll('form[data-wbs-form]').forEach(function(form){
    form.addEventListener('submit',function(e){
      e.preventDefault();
      var data=new FormData(form);
      fetch('${s.endpoint}',{method:'POST',body:data})
        .then(function(r){return r.ok?Promise.resolve():Promise.reject()})
        .then(function(){form.innerHTML='<p style="color:#10b981;font-weight:600">${s.success_msg}</p>'})
        .catch(function(){alert('${s.error_msg}')});
    });
  });
})();
</script>`;
      ctx.html = ctx.html.replace('</body>', script + '\n</body>');
    },
  },

  render() { return null; },
  validate(cfg) { return []; },
  onEnable(s)   { console.info('[Forms Plugin] enabled, endpoint:', s.endpoint); },
  onDisable()   { console.info('[Forms Plugin] disabled'); },
};

if (typeof WBS_SDK !== 'undefined') {
  WBS_SDK.registerPlugin(FormsPlugin);
}
