/**
 * app.js — Visual Website Builder (Wix/Framer lite)
 * Alpine.js — click-to-edit, inline text, image upload, multi-page URL preview
 */
'use strict';

// ═══════════════════════════════════════════════════════════════════════════
// UTILS
// ═══════════════════════════════════════════════════════════════════════════

const clone = v => JSON.parse(JSON.stringify(v));

function debounce(fn, ms) {
  let t;
  return function(...a) { clearTimeout(t); t = setTimeout(() => fn.apply(this, a), ms); };
}

function createToast(msg, type = 'success', ms = 3500) {
  const c = { success:'#10b981', error:'#ef4444', info:'#6c63ff', warning:'#f59e0b' };
  const t = document.createElement('div');
  t.style.cssText = `position:fixed;bottom:1.5rem;right:1.5rem;z-index:99999;
    padding:.75rem 1.25rem;border-radius:.75rem;font-size:.875rem;font-weight:600;
    color:#fff;background:${c[type]||c.success};box-shadow:0 8px 24px rgba(0,0,0,.18);
    animation:wbsIn .3s ease;pointer-events:none;max-width:320px;line-height:1.4`;
  t.textContent = msg;
  if (!document.getElementById('wbs-anim')) {
    const s = document.createElement('style'); s.id='wbs-anim';
    s.textContent='@keyframes wbsIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}@keyframes wbsOut{from{opacity:1}to{opacity:0;transform:translateY(8px)}}';
    document.head.appendChild(s);
  }
  document.body.appendChild(t);
  const rm = () => { t.style.animation='wbsOut .3s ease forwards'; setTimeout(()=>t.remove(),300); };
  const timer = setTimeout(rm, ms);
  return () => { clearTimeout(timer); rm(); };
}

function injectThemeVars(primary, secondary, font) {
  const toRgb = h => { h=h.replace('#',''); return [parseInt(h.slice(0,2),16),parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)]; };
  const [pr,pg,pb] = toRgb(primary);
  const [sr,sg,sb] = toRgb(secondary);
  const css = `:root{--primary:${primary};--secondary:${secondary};--primary-rgb:${pr},${pg},${pb};--secondary-rgb:${sr},${sg},${sb}}`;
  let el = document.getElementById('wbs-theme');
  if (!el) { el=document.createElement('style'); el.id='wbs-theme'; document.head.appendChild(el); }
  el.textContent = css;
  let fl = document.getElementById('wbs-font');
  if (!fl) { fl=document.createElement('link'); fl.id='wbs-font'; fl.rel='stylesheet'; document.head.appendChild(fl); }
  fl.href = `https://fonts.googleapis.com/css2?family=${font.replace(/ /g,'+')}:wght@400;500;600;700;800&display=swap`;
}

function pushThemeToFrame(frame, primary, secondary) {
  try {
    const toRgb = h => { h=h.replace('#',''); return [parseInt(h.slice(0,2),16),parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)]; };
    const [pr,pg,pb] = toRgb(primary);
    const [sr,sg,sb] = toRgb(secondary);
    const css = `:root{--primary:${primary};--secondary:${secondary};--primary-rgb:${pr},${pg},${pb};--secondary-rgb:${sr},${sg},${sb}}`;
    frame.contentWindow.postMessage({ type:'wbs-theme', css }, '*');
  } catch(e) {}
}


// ═══════════════════════════════════════════════════════════════════════════
// CONSTANTS (same as before — omitted for brevity, kept in full)
// ═══════════════════════════════════════════════════════════════════════════

const ALL_SECTIONS = ['hero','stats','features','testimonials','cta','about_story','services','portfolio','blog','contact','pricing','team','faq'];

const TEMPLATES = [
  {name:'NovaTech',emoji:'🚀',desc:'SaaS startup',primary:'#6c63ff',secondary:'#f50057',site_name:'NovaTech',tagline:'Build the Future Faster Than Ever'},
  {name:'GreenLeaf',emoji:'🌿',desc:'Eco/nature',primary:'#2e7d32',secondary:'#ffc107',site_name:'GreenLeaf',tagline:'Grow Sustainably, Scale Naturally'},
  {name:'OceanWave',emoji:'🌊',desc:'Tech/blue',primary:'#0277bd',secondary:'#00bcd4',site_name:'OceanWave',tagline:'Ride the Wave of Innovation'},
  {name:'SunsetStudio',emoji:'🎨',desc:'Creative agency',primary:'#e65100',secondary:'#f50057',site_name:'SunsetStudio',tagline:'Where Creativity Meets Technology'},
  {name:'DarkForge',emoji:'⚙️',desc:'Developer tool',primary:'#bb86fc',secondary:'#03dac6',site_name:'DarkForge',tagline:'Forge the Future in the Dark'},
  {name:'GoldRush',emoji:'💰',desc:'Finance/premium',primary:'#b8860b',secondary:'#8b0000',site_name:'GoldRush',tagline:'Premium Solutions for Premium Results'}
];

const DEFAULT_CONFIG = {
  site_name:'NovaTech',tagline:'Build the Future Faster Than Ever',
  description:'Cutting-edge software solutions that help businesses scale, innovate, and lead.',
  cta_text:'Start Free Trial',cta_link:'contact.html',
  primary_color:'#6c63ff',secondary_color:'#f50057',font:'Inter',
  pages:{
    home:{title:'Home',file:'index.html',sections:['hero','stats','features','testimonials','cta']},
    about:{title:'About',file:'about.html',sections:['about_story','cta']},
    services:{title:'Services',file:'services.html',sections:['services','cta']},
    portfolio:{title:'Portfolio',file:'portfolio.html',sections:['portfolio']},
    blog:{title:'Blog',file:'blog.html',sections:['blog']},
    contact:{title:'Contact',file:'contact.html',sections:['contact']},
    pricing:{title:'Pricing',file:'pricing.html',sections:['pricing']},
    team:{title:'Team',file:'team.html',sections:['team']},
    faq:{title:'FAQ',file:'faq.html',sections:['faq']},
    testimonials:{title:'Testimonials',file:'testimonials.html',sections:['testimonials']}
  },
  features:{dark_mode:true,animations:true,blog:true,portfolio_filter:true,pricing_toggle:true,scroll_progress:true,back_to_top:true,newsletter:true,counter_animation:true},
  plugins:{google_analytics:{enabled:false,tracking_id:'G-XXXXXXXXXX'},whatsapp:{enabled:false,phone:'919876543210',message:'Hello!'},newsletter_popup:{enabled:false,delay_seconds:5,title:'Get Updates',subtitle:'No spam.'}},
  content:{
    stats:[{value:10000,suffix:'+',label:'Happy Clients'},{value:500,suffix:'+',label:'Projects Shipped'},{value:99,suffix:'.9%',label:'Uptime SLA'},{value:24,suffix:'/7',label:'Support'}],
    features:[{icon:'⚡',title:'Lightning Performance',desc:'Sub-100ms response times globally.'},{icon:'🔒',title:'Enterprise Security',desc:'SOC 2 Type II certified.'},{icon:'📈',title:'Auto Scaling',desc:'Handle traffic spikes effortlessly.'},{icon:'🤖',title:'AI-Powered Insights',desc:'Real-time analytics with AI.'},{icon:'🔗',title:'200+ Integrations',desc:'Connect with Slack, GitHub, Stripe.'},{icon:'🌍',title:'Global CDN',desc:'Deploy to 50+ edge locations.'}],
    testimonials:[{initials:'SC',name:'Sarah Chen',role:'CTO, TechFlow Inc.',quote:'NovaTech cut our deployment time by 80%.'},{initials:'MJ',name:'Marcus Johnson',role:'Lead Engineer, StartupX',quote:"The best developer experience I've had in 10 years."},{initials:'AP',name:'Aisha Patel',role:'VP Engineering, ScaleUp',quote:'We migrated 50+ microservices in a weekend.'}],
    services:[{icon:'☁️',title:'Cloud Infrastructure',desc:'Deploy on our globally distributed edge network.',features:['50+ global edge locations','99.99% uptime SLA','Auto-scaling']},{icon:'🤖',title:'AI & Machine Learning',desc:'Integrate powerful AI capabilities.',features:['Pre-built model library','Custom fine-tuning','Real-time inference API']},{icon:'🔒',title:'Security & Compliance',desc:'Enterprise-grade security.',features:['End-to-end encryption','SOC 2 certified','GDPR & HIPAA ready']}],
    team:[{initials:'AK',name:'Alex Kim',role:'CEO & Co-founder',bio:'Former Google SWE.'},{initials:'SR',name:'Sofia Rodriguez',role:'CTO & Co-founder',bio:'Ex-Stripe infrastructure lead.'},{initials:'JL',name:'James Liu',role:'Head of Design',bio:'Previously at Figma.'},{initials:'MP',name:'Maya Patel',role:'VP Engineering',bio:'10+ years at Amazon and Airbnb.'}],
    faq:[{q:'How long does it take to get started?',a:'You can be up and running in under 5 minutes.'},{q:'Do you offer a free plan?',a:'Yes! Our free plan includes 3 projects, 100GB bandwidth.'},{q:'Is my data secure?',a:'Yes. We are SOC 2 Type II certified.'}],
    pricing:[{tier:'Starter',price_monthly:0,price_yearly:0,desc:'Perfect for side projects.',featured:false,features:['3 projects','100 GB bandwidth','Community support'],missing:['Custom domains','Team seats']},{tier:'Pro',price_monthly:49,price_yearly:39,desc:'For growing teams.',featured:true,features:['Unlimited projects','1 TB bandwidth','Email support','Custom domains','5 team seats'],missing:[]},{tier:'Enterprise',price_monthly:'Custom',price_yearly:'Custom',desc:'For large teams.',featured:false,features:['Everything in Pro','Unlimited bandwidth','Dedicated support','SSO / SAML'],missing:[]}],
    blog_posts:[{seed:'b1',tag:'Design',date:'May 1, 2025',datetime:'2025-05-01',title:'The Future of Web Design',excerpt:'Exploring trends that will shape the web.',author:'Sarah Chen',initials:'SC'},{seed:'b2',tag:'Tech',date:'Apr 20, 2025',datetime:'2025-04-20',title:'Building Scalable APIs',excerpt:'Best practices for designing APIs.',author:'Mike Ross',initials:'MR'},{seed:'b3',tag:'Business',date:'Apr 10, 2025',datetime:'2025-04-10',title:'Growth Hacking for Startups',excerpt:'Proven strategies to accelerate growth.',author:'Priya Patel',initials:'PP'}],
    portfolio_items:[{seed:'p1',title:'E-Commerce Platform',category:'web',cat_label:'Web Design'},{seed:'p2',title:'Brand Identity',category:'brand',cat_label:'Branding'},{seed:'p3',title:'Mobile Banking App',category:'mobile',cat_label:'Mobile'},{seed:'p4',title:'SaaS Dashboard',category:'saas',cat_label:'SaaS'}]
  }
};


// ═══════════════════════════════════════════════════════════════════════════
// ALPINE COMPONENT
// ═══════════════════════════════════════════════════════════════════════════

document.addEventListener('alpine:init', () => {
  Alpine.data('builder', () => ({

    // ── Core state ──────────────────────────────────────────────────────────
    cfg:             clone(DEFAULT_CONFIG),
    activeTab:       'Setup',
    contentTab:      'Features',
    previewPage:     'home',
    previewDevice:   'desktop',
    sectionPage:     'home',
    currentSections: [],
    hiddenSections:  {},
    disabledPages:   [],
    exportMode:      'static',
    showTemplates:   false,
    templates:       TEMPLATES,
    availableSections: ALL_SECTIONS,

    // ── Visual editor state ─────────────────────────────────────────────────
    previewMode:     'srcdoc',   // 'srcdoc' | 'url'
    projectId:       'default',
    selectedSection: null,       // { id, name } — section clicked in iframe
    selectedSectionName: '',
    showImageUpload: false,
    uploadTarget:    null,       // { section, src } — image being replaced
    uploadedImages:  [],         // [{ url, filename }]

    // ── Async flags ─────────────────────────────────────────────────────────
    previewing:  false,
    exporting:   false,
    saving:      false,
    uploading:   false,
    busy:        false,

    // ── Preview ─────────────────────────────────────────────────────────────
    previewHtml:     '',
    previewUrl:      '',
    _lastKey:        '',

    // ── History ─────────────────────────────────────────────────────────────
    _history:    [],
    _historyIdx: -1,
    get canUndo() { return this._historyIdx > 0; },
    get canRedo() { return this._historyIdx < this._history.length - 1; },

    // ── Drag ────────────────────────────────────────────────────────────────
    _dragIdx: null,

    // ── Toast ────────────────────────────────────────────────────────────────
    _rmToast: null,

    // ════════════════════════════════════════════════════════════════════════
    // INIT
    // ════════════════════════════════════════════════════════════════════════

    init() {
      this._loadLocal();
      this._pushHistory();
      this.loadSectionPage();
      injectThemeVars(this.cfg.primary_color, this.cfg.secondary_color, this.cfg.font);

      this.debouncedPreview = debounce(() => this._buildPreview(), 700);

      // Listen for messages from preview iframe (bridge script)
      window.addEventListener('message', e => this._onFrameMessage(e));

      // Keyboard shortcuts
      document.addEventListener('keydown', e => {
        const mod = e.ctrlKey || e.metaKey;
        if (mod && e.key==='z' && !e.shiftKey) { e.preventDefault(); this.undo(); }
        if (mod && (e.key==='y' || (e.key==='z' && e.shiftKey))) { e.preventDefault(); this.redo(); }
        if (mod && e.key==='s') { e.preventDefault(); this.saveProject(); }
        if (e.key==='Escape') { this.selectedSection=null; this.selectedSectionName=''; }
      });

      setTimeout(() => this._buildPreview(), 400);
    },

    // ════════════════════════════════════════════════════════════════════════
    // IFRAME MESSAGE HANDLER (bridge → parent)
    // ════════════════════════════════════════════════════════════════════════

    _onFrameMessage(e) {
      const d = e.data;
      if (!d || !d.type) return;

      switch(d.type) {
        case 'wbs-select':
          // Section clicked in preview
          this.selectedSection     = d.id;
          this.selectedSectionName = d.section;
          // Switch editor to the relevant content tab
          this._focusTabForSection(d.section);
          break;

        case 'wbs-deselect':
          this.selectedSection     = null;
          this.selectedSectionName = '';
          break;

        case 'wbs-action':
          this._handleSectionAction(d.action, d.id);
          break;

        case 'wbs-text-edit':
          // Inline text was edited — sync back to config
          this._syncTextEdit(d);
          break;

        case 'wbs-image-click':
          // Alt+click on image — open upload panel
          this.uploadTarget    = { section: d.section, src: d.src };
          this.showImageUpload = true;
          break;
      }
    },

    _focusTabForSection(sectionName) {
      const map = {
        hero:'Setup', stats:'Content', features:'Content',
        testimonials:'Content', services:'Content', team:'Content',
        pricing:'Content', faq:'Content', blog:'Content',
        portfolio:'Content', contact:'Setup', cta:'Setup',
        about_story:'Setup'
      };
      const contentMap = {
        features:'Features', testimonials:'Testimonials', team:'Team',
        pricing:'Pricing', stats:'Stats', faq:'FAQ'
      };
      const tab = map[sectionName] || 'Content';
      this.activeTab = tab;
      if (tab === 'Content' && contentMap[sectionName]) {
        this.contentTab = contentMap[sectionName];
      }
    },

    _handleSectionAction(action, sectionId) {
      // Find section index in currentSections by matching id pattern
      const idx = this.currentSections.findIndex(s => sectionId.startsWith(s));
      if (idx === -1) return;

      switch(action) {
        case 'duplicate': this.duplicateSection(idx); break;
        case 'hide':      this.toggleSectionVisibility(this.currentSections[idx]); break;
        case 'delete':    this.removeSection(idx); break;
      }
    },

    _syncTextEdit(d) {
      // Best-effort: update tagline/description/cta_text based on tag
      if (!d.text) return;
      const t = d.text.trim();
      if (d.tag === 'H1' && d.section?.includes('hero')) {
        // Don't overwrite — tagline is split across lines
      } else if (d.tag === 'P' && d.section?.includes('hero')) {
        this.cfg.description = t;
      }
      // For content arrays, we rely on the panel editor
      // Full inline sync would require data-wbs-field attributes in templates
      this._commit();
    },

    // ════════════════════════════════════════════════════════════════════════
    // HIGHLIGHT SECTION IN IFRAME
    // ════════════════════════════════════════════════════════════════════════

    highlightSection(sectionName) {
      const frame = document.getElementById('previewFrame');
      if (!frame) return;
      // Find the section id that matches the name
      const id = sectionName + '_0'; // best guess — bridge uses tag_index
      try {
        frame.contentWindow.postMessage({ type:'wbs-select-section', id }, '*');
      } catch(e) {}
    },

    // ════════════════════════════════════════════════════════════════════════
    // THEME ENGINE
    // ════════════════════════════════════════════════════════════════════════

    onThemeChange() {
      injectThemeVars(this.cfg.primary_color, this.cfg.secondary_color, this.cfg.font);
      const frame = document.getElementById('previewFrame');
      if (frame) pushThemeToFrame(frame, this.cfg.primary_color, this.cfg.secondary_color);
      this._commit();
    },

    // ════════════════════════════════════════════════════════════════════════
    // PREVIEW — srcdoc OR url mode
    // ════════════════════════════════════════════════════════════════════════

    triggerPreview() { this.debouncedPreview(); },

    async _buildPreview() {
      const key = JSON.stringify({ cfg: this._activeCfg(), page: this.previewPage, mode: this.previewMode });
      if (key === this._lastKey) return;
      this._lastKey = key;
      this.previewing = true;

      if (this.previewMode === 'url') {
        await this._buildPreviewUrl();
      } else {
        await this._buildPreviewSrcdoc();
      }
      this.previewing = false;
    },

    async _buildPreviewSrcdoc() {
      try {
        const res = await fetch('/api/preview', {
          method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({ config: this._activeCfg(), page: this.previewPage, visual: true })
        });
        const data = await res.json();
        if (data.ok) {
          const frame = document.getElementById('previewFrame');
          if (frame) {
            frame.srcdoc = data.html;
            frame.onload = () => pushThemeToFrame(frame, this.cfg.primary_color, this.cfg.secondary_color);
          }
        } else {
          this._toast('Preview error: ' + (data.error||'unknown'), 'error');
        }
      } catch(e) {
        const frame = document.getElementById('previewFrame');
        if (frame) frame.srcdoc = this._offlinePage();
      }
    },

    async _buildPreviewUrl() {
      try {
        const res = await fetch('/api/preview-url', {
          method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({ config: this._activeCfg(), project_id: this.projectId })
        });
        const data = await res.json();
        if (data.ok) {
          const pages = data.pages || {};
          const url   = pages[this.previewPage] || data.base_url + 'index.html';
          const frame = document.getElementById('previewFrame');
          if (frame) {
            frame.src = url;
            frame.onload = () => pushThemeToFrame(frame, this.cfg.primary_color, this.cfg.secondary_color);
          }
          this.previewUrl = url;
        }
      } catch(e) {
        this._toast('URL preview failed', 'error');
      }
    },

    switchPreviewPage(pageKey) {
      this.previewPage = pageKey;
      this._lastKey = '';   // force rebuild
      this._buildPreview();
    },

    _offlinePage() {
      return `<!DOCTYPE html><html><body style="font-family:system-ui;padding:2rem;background:#0f0f1a;color:#a5d6a7">
        <div style="max-width:480px;margin:4rem auto;text-align:center">
          <div style="font-size:3rem;margin-bottom:1rem">🔌</div>
          <h2 style="color:#bb86fc;margin-bottom:.5rem">Preview Server Offline</h2>
          <p style="color:#888;font-size:.9rem;margin-bottom:1.5rem">Start the backend to see live preview:</p>
          <code style="background:#1a1a2e;color:#03dac6;padding:.75rem 1.25rem;border-radius:.5rem;display:block;font-size:.85rem">
            cd static-site/builder/ui<br>python server.py
          </code>
        </div></body></html>`;
    },

    // ════════════════════════════════════════════════════════════════════════
    // IMAGE UPLOAD
    // ════════════════════════════════════════════════════════════════════════

    async uploadImage(event) {
      const file = event.target.files[0];
      if (!file) return;
      this.uploading = true;
      try {
        const fd = new FormData();
        fd.append('file', file);
        const res  = await fetch('/api/upload', { method:'POST', body: fd });
        const data = await res.json();
        if (data.ok) {
          this.uploadedImages.unshift({ url: data.url, filename: data.filename });
          this._toast('Image uploaded ✓');
          // If we have an upload target, apply it
          if (this.uploadTarget) {
            this._applyUploadedImage(data.url);
          }
        } else {
          this._toast('Upload failed: ' + data.error, 'error');
        }
      } catch(e) {
        this._toast('Upload failed (server offline)', 'error');
      }
      this.uploading = false;
    },

    _applyUploadedImage(url) {
      // Inject image URL into iframe
      const frame = document.getElementById('previewFrame');
      if (frame && this.uploadTarget) {
        try {
          frame.contentWindow.postMessage({ type:'wbs-replace-image', oldSrc: this.uploadTarget.src, newSrc: url }, '*');
        } catch(e) {}
      }
      this.uploadTarget    = null;
      this.showImageUpload = false;
      this._commit();
    },

    selectUploadedImage(url) {
      this._applyUploadedImage(url);
    },

    // ════════════════════════════════════════════════════════════════════════
    // EXPORT
    // ════════════════════════════════════════════════════════════════════════

    async exportSite() {
      if (this.busy) return;
      this.exporting = true; this.busy = true;
      try {
        const res = await fetch('/api/export', {
          method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({ config: this._activeCfg(), mode: this.exportMode, minify: false })
        });
        if (!res.ok) { const e=await res.json().catch(()=>({})); this._toast('Export failed: '+(e.error||''), 'error'); return; }
        const blob = await res.blob();
        const url  = URL.createObjectURL(blob);
        const a    = document.createElement('a');
        a.href=url; a.download=(this.cfg.site_name||'website').toLowerCase().replace(/\s+/g,'_')+'.zip'; a.click();
        URL.revokeObjectURL(url);
        this._toast(`Downloaded as ${this.exportMode} ✓`);
      } catch(e) { this._toast('Server offline. Run server.py first.', 'error'); }
      this.exporting = false; this.busy = false;
    },

    // ════════════════════════════════════════════════════════════════════════
    // SAVE
    // ════════════════════════════════════════════════════════════════════════

    async saveProject() {
      this._saveLocal();
      this.saving = true;
      try {
        await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ config: this.cfg }) });
        this._toast('Project saved ✓');
      } catch(e) { this._toast('Saved locally (server offline)', 'info'); }
      this.saving = false;
    },

    // ════════════════════════════════════════════════════════════════════════
    // HISTORY
    // ════════════════════════════════════════════════════════════════════════

    _pushHistory() {
      this._history = this._history.slice(0, this._historyIdx + 1);
      this._history.push(clone(this.cfg));
      this._historyIdx = this._history.length - 1;
      if (this._history.length > 60) { this._history.shift(); this._historyIdx--; }
    },
    undo() {
      if (!this.canUndo) return;
      this._historyIdx--;
      this.cfg = clone(this._history[this._historyIdx]);
      this._afterRestore();
    },
    redo() {
      if (!this.canRedo) return;
      this._historyIdx++;
      this.cfg = clone(this._history[this._historyIdx]);
      this._afterRestore();
    },
    _afterRestore() {
      this.loadSectionPage();
      injectThemeVars(this.cfg.primary_color, this.cfg.secondary_color, this.cfg.font);
      this.debouncedPreview();
    },

    // ════════════════════════════════════════════════════════════════════════
    // PAGES
    // ════════════════════════════════════════════════════════════════════════

    togglePage(key) {
      if (this.disabledPages.includes(key)) this.disabledPages = this.disabledPages.filter(p=>p!==key);
      else this.disabledPages.push(key);
      this._commit();
    },

    // ════════════════════════════════════════════════════════════════════════
    // SECTIONS
    // ════════════════════════════════════════════════════════════════════════

    loadSectionPage() {
      const p = this.cfg.pages[this.sectionPage];
      this.currentSections = p ? clone(p.sections||[]) : [];
    },
    _saveSections() {
      if (this.cfg.pages[this.sectionPage]) this.cfg.pages[this.sectionPage].sections = clone(this.currentSections);
    },
    addSection(name) {
      if (!this.currentSections.includes(name)) { this.currentSections.push(name); this._saveSections(); this._commit(); }
    },
    async removeSection(idx) {
      if (!window.confirm(`Remove "${this.currentSections[idx]}" section?`)) return;
      this.currentSections.splice(idx,1); this._saveSections(); this._commit();
    },
    duplicateSection(idx) {
      const copy = this.currentSections[idx];
      this.currentSections.splice(idx+1,0,copy);
      this._saveSections(); this._commit();
      this._toast('Section duplicated');
    },
    toggleSectionVisibility(name) {
      const p = this.sectionPage;
      if (!this.hiddenSections[p]) this.hiddenSections[p] = new Set();
      if (this.hiddenSections[p].has(name)) this.hiddenSections[p].delete(name);
      else this.hiddenSections[p].add(name);
      this._commit();
    },
    isSectionHidden(name) { return !!(this.hiddenSections[this.sectionPage]?.has(name)); },

    // Drag-and-drop
    dragStart(idx) { this._dragIdx = idx; },
    dragOver(idx) {
      if (this._dragIdx===null||this._dragIdx===idx) return;
      const item = this.currentSections.splice(this._dragIdx,1)[0];
      this.currentSections.splice(idx,0,item);
      this._dragIdx = idx;
    },
    dragDrop() { this._saveSections(); this._commit(); },
    dragEnd() { this._dragIdx = null; },

    // ════════════════════════════════════════════════════════════════════════
    // CONTENT
    // ════════════════════════════════════════════════════════════════════════

    addItem(key, tpl) {
      if (!this.cfg.content[key]) this.cfg.content[key]=[];
      this.cfg.content[key].push(clone(tpl)); this._commit();
    },
    async removeItem(key, idx) {
      if (!window.confirm('Remove this item?')) return;
      this.cfg.content[key].splice(idx,1); this._commit();
    },

    // ════════════════════════════════════════════════════════════════════════
    // TEMPLATES
    // ════════════════════════════════════════════════════════════════════════

    applyTemplate(tpl) {
      this.cfg.primary_color=tpl.primary; this.cfg.secondary_color=tpl.secondary;
      this.cfg.site_name=tpl.site_name; this.cfg.tagline=tpl.tagline;
      this.showTemplates=false;
      injectThemeVars(tpl.primary, tpl.secondary, this.cfg.font);
      this._commit(); this._toast(`Template "${tpl.name}" applied ✓`);
    },

    // ════════════════════════════════════════════════════════════════════════
    // MISC
    // ════════════════════════════════════════════════════════════════════════

    copyJson() {
      navigator.clipboard.writeText(JSON.stringify(this._activeCfg(),null,2))
        .then(()=>this._toast('Config copied ✓')).catch(()=>this._toast('Copy failed','error'));
    },

    // ════════════════════════════════════════════════════════════════════════
    // PRIVATE
    // ════════════════════════════════════════════════════════════════════════

    _commit() { this._pushHistory(); this._saveLocal(); this.debouncedPreview(); },

    _activeCfg() {
      const c = clone(this.cfg);
      for (const k of this.disabledPages) delete c.pages[k];
      for (const [pk, hidden] of Object.entries(this.hiddenSections)) {
        if (c.pages[pk] && hidden.size>0)
          c.pages[pk].sections = (c.pages[pk].sections||[]).filter(s=>!hidden.has(s));
      }
      return c;
    },

    _saveLocal() {
      try {
        localStorage.setItem('wbs_cfg', JSON.stringify(this.cfg));
        localStorage.setItem('wbs_disabled', JSON.stringify(this.disabledPages));
        localStorage.setItem('wbs_hidden', JSON.stringify(
          Object.fromEntries(Object.entries(this.hiddenSections).map(([k,v])=>[k,[...v]]))
        ));
        localStorage.setItem('wbs_images', JSON.stringify(this.uploadedImages));
      } catch(e) {}
    },

    _loadLocal() {
      try {
        const c=localStorage.getItem('wbs_cfg'); if(c) this.cfg=JSON.parse(c);
        const d=localStorage.getItem('wbs_disabled'); if(d) this.disabledPages=JSON.parse(d);
        const h=localStorage.getItem('wbs_hidden');
        if(h){ const r=JSON.parse(h); this.hiddenSections=Object.fromEntries(Object.entries(r).map(([k,v])=>[k,new Set(v)])); }
        const i=localStorage.getItem('wbs_images'); if(i) this.uploadedImages=JSON.parse(i);
      } catch(e) {}
    },

    _toast(msg, type='success') {
      if (this._rmToast) this._rmToast();
      this._rmToast = createToast(msg, type);
    }

  }));
});
