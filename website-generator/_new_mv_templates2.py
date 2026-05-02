
def _mv_become_supplier_html(site_name: str) -> str:
    return f"""{{% extends 'base.html' %}}
{{% block title %}}Become a Seller — {site_name}{{% endblock %}}
{{% block content %}}
<div style="max-width:900px;margin:0 auto;padding:2rem 1rem">
  <div style="text-align:center;padding:3rem 1rem;background:linear-gradient(135deg,var(--mv-pink),#ff5722);border-radius:20px;color:#fff;margin-bottom:2.5rem">
    <h1 style="font-size:2.2rem;font-weight:800;margin-bottom:.75rem">Start Selling on {site_name}</h1>
    <p style="opacity:.9;font-size:1.05rem;margin-bottom:1.5rem">Join {{{{ stats.sellers }}}}+ sellers already earning on our platform</p>
    <a href="{{{{ url_for('signup') }}}}?role=seller" style="background:#fff;color:var(--mv-pink);padding:.85rem 2.5rem;border-radius:30px;font-weight:800;font-size:1.05rem;text-decoration:none">Register as Seller →</a>
  </div>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1.5rem;margin-bottom:2.5rem">
    <div class="mv-stat" style="border-top:4px solid var(--mv-pink)">
      <div class="mv-stat-val">{{{{ stats.sellers }}}}+</div><div class="mv-stat-label">Active Sellers</div>
    </div>
    <div class="mv-stat" style="border-top:4px solid #ff5722">
      <div class="mv-stat-val">{{{{ stats.products }}}}+</div><div class="mv-stat-label">Products Listed</div>
    </div>
    <div class="mv-stat" style="border-top:4px solid #4caf50">
      <div class="mv-stat-val">{{{{ stats.orders }}}}+</div><div class="mv-stat-label">Orders Placed</div>
    </div>
    <div class="mv-stat" style="border-top:4px solid #2196f3">
      <div class="mv-stat-val">90%</div><div class="mv-stat-label">Seller Payout</div>
    </div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin-bottom:2.5rem">
    {{% for icon, title, desc in [
      ('🚀','Easy Onboarding','Register, complete KYC, and start listing products in minutes.'),
      ('💰','High Payouts','Earn 90% of every sale. Withdraw to your bank anytime.'),
      ('📦','Logistics Support','We handle shipping tracking and returns for you.'),
      ('📊','Real-time Dashboard','Track orders, earnings, and inventory in one place.')
    ] %}}
    <div style="background:#fff;border-radius:14px;padding:1.5rem;box-shadow:0 2px 8px rgba(0,0,0,.06)">
      <div style="font-size:2rem;margin-bottom:.5rem">{{{{ icon }}}}</div>
      <h4 style="font-weight:700;margin-bottom:.4rem">{{{{ title }}}}</h4>
      <p style="color:#666;font-size:.88rem;line-height:1.6">{{{{ desc }}}}</p>
    </div>
    {{% endfor %}}
  </div>
  <div style="text-align:center">
    <a href="{{{{ url_for('signup') }}}}?role=seller" class="mv-btn mv-btn-primary" style="font-size:1.05rem;padding:.85rem 2.5rem">Get Started Free →</a>
  </div>
</div>
{{% endblock %}}"""


def _mv_otp_request_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Login with OTP{%- endblock %}
{%- block content %}
<div class="mv-auth">
  <div class="mv-auth-card">
    <h2>Login with OTP</h2>
    <p class="subtitle">Enter your mobile number to receive a 6-digit OTP</p>
    <form method="POST" action="{{ url_for('otp_request') }}">
      <div class="mv-form-group">
        <label>Mobile Number</label>
        <input type="tel" name="mobile" placeholder="10-digit mobile number"
               pattern="[0-9]{10}" maxlength="10" required autofocus
               style="letter-spacing:.1em;font-size:1.1rem"/>
      </div>
      <button type="submit" class="mv-btn mv-btn-primary" style="width:100%">Send OTP</button>
    </form>
    <p class="mv-auth-switch">
      Or <a href="{{ url_for('login') }}">login with email & password</a>
    </p>
    <p class="mv-auth-switch">
      New here? <a href="{{ url_for('signup') }}">Create account</a>
    </p>
  </div>
</div>
{%- endblock %}"""


def _mv_otp_verify_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Verify OTP{%- endblock %}
{%- block content %}
<div class="mv-auth">
  <div class="mv-auth-card">
    <h2>Enter OTP</h2>
    <p class="subtitle">
      We sent a 6-digit code to
      <strong>{{ mobile[:4] }}****{{ mobile[-2:] }}</strong>
    </p>
    <form method="POST" action="{{ url_for('otp_verify') }}">
      <div class="mv-form-group">
        <label>6-Digit OTP</label>
        <input type="text" name="code" placeholder="Enter OTP"
               pattern="[0-9]{6}" maxlength="6" required autofocus
               style="letter-spacing:.3em;font-size:1.4rem;text-align:center"/>
      </div>
      <button type="submit" class="mv-btn mv-btn-primary" style="width:100%">Verify & Login</button>
    </form>
    <p class="mv-auth-switch">
      Wrong number? <a href="{{ url_for('otp_request') }}">Go back</a>
    </p>
    <p style="text-align:center;font-size:.78rem;color:#aaa;margin-top:.75rem">OTP expires in 10 minutes</p>
  </div>
</div>
{%- endblock %}"""


def _mv_seller_inventory_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Inventory — Seller{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>📦 Inventory Management</h2>
    <a href="{{ url_for('seller_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-table-wrap">
    <div class="mv-table-head"><h3>Stock Levels</h3></div>
    {%- if products %}
    <table class="mv-table">
      <thead><tr><th>Image</th><th>Product</th><th>Category</th><th>Current Stock</th><th>Status</th><th>Update Stock</th></tr></thead>
      <tbody>
        {%- for p in products %}
        <tr>
          <td><img src="{{ url_for('static', filename='uploads/' + (p.image or 'default.png')) }}"
                   style="width:44px;height:44px;object-fit:cover;border-radius:8px"
                   onerror="this.src='https://placehold.co/44x44/fce4ec/e91e63?text=?'"/></td>
          <td style="font-weight:700">{{ p.name }}</td>
          <td><span class="badge badge-confirmed">{{ p.category }}</span></td>
          <td>
            <span class="badge {% if p.stock == 0 %}badge-cancelled{% elif p.stock < 5 %}badge-pending{% else %}badge-paid{% endif %}">
              {{ p.stock }} units
            </span>
          </td>
          <td>
            {%- if p.stock == 0 %}<span style="color:#e53935;font-size:.82rem">Out of Stock</span>
            {%- elif p.stock < 5 %}<span style="color:#ff9800;font-size:.82rem">⚠ Low Stock</span>
            {%- else %}<span style="color:#4caf50;font-size:.82rem">In Stock</span>{%- endif %}
          </td>
          <td>
            <form method="POST" action="{{ url_for('update_inventory', pid=p.id) }}" style="display:flex;gap:.4rem">
              <input type="number" name="stock" value="{{ p.stock }}" min="0"
                     style="width:80px;padding:.35rem .6rem;border:1.5px solid #eee;border-radius:6px;font-size:.88rem"/>
              <button type="submit" class="mv-btn mv-btn-primary mv-btn-sm">Save</button>
            </form>
          </td>
        </tr>
        {%- endfor %}
      </tbody>
    </table>
    {%- else %}
    <div style="text-align:center;padding:3rem"><p style="color:#888">No products yet.</p></div>
    {%- endif %}
  </div>
</div>
{%- endblock %}"""


def _mv_seller_shipments_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Shipments — Seller{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>🚚 Shipment Tracking</h2>
    <a href="{{ url_for('seller_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-table-wrap">
    <div class="mv-table-head"><h3>All Shipments</h3></div>
    {%- if shipments %}
    <table class="mv-table">
      <thead><tr><th>Order #</th><th>Carrier</th><th>Tracking No.</th><th>Status</th><th>Est. Delivery</th><th>Update</th></tr></thead>
      <tbody>
        {%- for s in shipments %}
        <tr>
          <td style="font-weight:700">#{{ s.order_id }}</td>
          <td>{{ s.carrier or '—' }}</td>
          <td style="font-family:monospace;font-size:.85rem">{{ s.tracking_number or '—' }}</td>
          <td><span class="badge badge-{{ 'paid' if s.status=='delivered' else 'confirmed' if s.status=='in_transit' else 'pending' }}">{{ s.status|capitalize }}</span></td>
          <td style="color:#888;font-size:.82rem">{{ s.estimated_delivery[:10] if s.estimated_delivery else '—' }}</td>
          <td>
            <form method="POST" action="{{ url_for('update_shipment', oid=s.order_id) }}" style="display:flex;gap:.4rem;flex-wrap:wrap">
              <input type="text" name="carrier" value="{{ s.carrier or '' }}" placeholder="Carrier" style="width:90px;padding:.3rem .5rem;border:1.5px solid #eee;border-radius:6px;font-size:.8rem"/>
              <input type="text" name="tracking_number" value="{{ s.tracking_number or '' }}" placeholder="Tracking #" style="width:110px;padding:.3rem .5rem;border:1.5px solid #eee;border-radius:6px;font-size:.8rem"/>
              <select name="status" style="padding:.3rem .5rem;border:1.5px solid #eee;border-radius:6px;font-size:.8rem">
                {%- for st in ['pending','dispatched','in_transit','out_for_delivery','delivered'] %}
                <option value="{{ st }}" {{ 'selected' if s.status==st else '' }}>{{ st|replace('_',' ')|capitalize }}</option>
                {%- endfor %}
              </select>
              <button type="submit" class="mv-btn mv-btn-primary mv-btn-sm">Update</button>
            </form>
          </td>
        </tr>
        {%- endfor %}
      </tbody>
    </table>
    {%- else %}
    <div style="text-align:center;padding:3rem"><p style="color:#888">No shipments yet.</p></div>
    {%- endif %}
  </div>
</div>
{%- endblock %}"""


def _mv_seller_returns_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Returns — Seller{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>↩️ Return Requests</h2>
    <a href="{{ url_for('seller_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  {%- if returns %}
  {%- for r in returns %}
  <div class="mv-table-wrap" style="margin-bottom:1rem">
    <div class="mv-table-head">
      <div>
        <strong>Return #{{ r.id }}</strong> — Order #{{ r.order_id }}
        <span style="color:#888;font-size:.82rem;margin-left:.75rem">{{ r.created_at[:10] }}</span>
        <span style="margin-left:.75rem">Customer: <strong>{{ r.customer_name }}</strong></span>
      </div>
      <span class="badge badge-{{ 'paid' if r.status=='refunded' else 'pending' if r.status=='requested' else 'confirmed' }}">{{ r.status|capitalize }}</span>
    </div>
    <div style="padding:1rem">
      <p style="color:#555;margin-bottom:.75rem"><strong>Reason:</strong> {{ r.reason }}</p>
      {%- if r.status == 'requested' %}
      <form method="POST" action="{{ url_for('respond_return', rid=r.id) }}" style="display:flex;gap:.5rem;align-items:center;flex-wrap:wrap">
        <input type="text" name="note" placeholder="Add a note (optional)" style="flex:1;min-width:200px;padding:.4rem .75rem;border:1.5px solid #eee;border-radius:8px;font-size:.88rem"/>
        <button name="action" value="approve" class="mv-btn mv-btn-primary mv-btn-sm">Approve</button>
        <button name="action" value="reject" class="mv-btn mv-btn-danger mv-btn-sm">Reject</button>
      </form>
      {%- else %}
      <p style="color:#888;font-size:.85rem">Admin note: {{ r.admin_note or '—' }}</p>
      {%- endif %}
    </div>
  </div>
  {%- endfor %}
  {%- else %}
  <div style="text-align:center;padding:4rem 1rem">
    <div style="font-size:4rem">✅</div>
    <h5 style="margin:.75rem 0;color:#555">No return requests</h5>
  </div>
  {%- endif %}
</div>
{%- endblock %}"""


def _mv_seller_support_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Support Tickets — Seller{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>🎫 Support Tickets</h2>
    <a href="{{ url_for('seller_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-table-wrap" style="margin-bottom:1.5rem">
    <div class="mv-table-head"><h3>New Ticket</h3></div>
    <div style="padding:1.25rem">
      <form method="POST" action="{{ url_for('create_support_ticket') }}" style="display:grid;grid-template-columns:1fr 1fr auto;gap:.75rem;align-items:end">
        <div>
          <label style="font-size:.82rem;font-weight:600;display:block;margin-bottom:.3rem">Subject *</label>
          <input type="text" name="subject" class="mv-form-input" placeholder="Describe your issue" required/>
        </div>
        <div>
          <label style="font-size:.82rem;font-weight:600;display:block;margin-bottom:.3rem">Priority</label>
          <select name="priority" class="mv-form-input">
            <option value="low">Low</option>
            <option value="normal" selected>Normal</option>
            <option value="high">High</option>
          </select>
        </div>
        <button type="submit" class="mv-btn mv-btn-primary">Submit</button>
        <div style="grid-column:1/-1">
          <label style="font-size:.82rem;font-weight:600;display:block;margin-bottom:.3rem">Description *</label>
          <textarea name="description" class="mv-form-input" rows="3" placeholder="Provide details…" required></textarea>
        </div>
      </form>
    </div>
  </div>
  <div class="mv-table-wrap">
    <div class="mv-table-head"><h3>My Tickets</h3></div>
    {%- if tickets %}
    <table class="mv-table">
      <thead><tr><th>#</th><th>Subject</th><th>Priority</th><th>Status</th><th>Admin Reply</th><th>Date</th></tr></thead>
      <tbody>
        {%- for t in tickets %}
        <tr>
          <td>{{ t.id }}</td>
          <td style="font-weight:600">{{ t.subject }}</td>
          <td><span class="badge badge-{{ 'cancelled' if t.priority=='high' else 'pending' if t.priority=='normal' else 'confirmed' }}">{{ t.priority|capitalize }}</span></td>
          <td><span class="badge badge-{{ 'paid' if t.status=='resolved' else 'confirmed' if t.status=='in_progress' else 'pending' }}">{{ t.status|replace('_',' ')|capitalize }}</span></td>
          <td style="color:#666;font-size:.85rem">{{ t.admin_reply or '—' }}</td>
          <td style="color:#888;font-size:.82rem">{{ t.created_at[:10] }}</td>
        </tr>
        {%- endfor %}
      </tbody>
    </table>
    {%- else %}
    <div style="text-align:center;padding:2rem"><p style="color:#888">No tickets yet.</p></div>
    {%- endif %}
  </div>
</div>
{%- endblock %}"""
