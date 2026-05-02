
def _mv_admin_kyc_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}KYC Queue — Admin{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>🪪 KYC Approval Queue</h2>
    <a href="{{ url_for('admin_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-table-wrap">
    <table class="mv-table">
      <thead><tr><th>Seller</th><th>Email</th><th>Shop Name</th><th>KYC Status</th><th>Joined</th><th>Action</th></tr></thead>
      <tbody>
        {%- for s in sellers %}
        <tr>
          <td style="font-weight:700">{{ s.name }}</td>
          <td style="color:#888;font-size:.85rem">{{ s.email }}</td>
          <td>{{ s.shop_name or '—' }}</td>
          <td><span class="badge badge-pending">{{ s.kyc_status|capitalize }}</span></td>
          <td style="color:#888;font-size:.82rem">{{ s.created_at[:10] }}</td>
          <td>
            <form method="POST" action="{{ url_for('admin_kyc_action', uid=s.id) }}" style="display:flex;gap:.4rem;align-items:center">
              <input type="text" name="reason" placeholder="Reason (for rejection)" style="width:160px;padding:.3rem .6rem;border:1.5px solid #eee;border-radius:6px;font-size:.8rem"/>
              <button name="action" value="approve" class="mv-btn mv-btn-primary mv-btn-sm">Approve</button>
              <button name="action" value="reject" class="mv-btn mv-btn-danger mv-btn-sm">Reject</button>
            </form>
          </td>
        </tr>
        {%- else %}
        <tr><td colspan="6" style="text-align:center;color:#888;padding:2rem">No pending KYC submissions.</td></tr>
        {%- endfor %}
      </tbody>
    </table>
  </div>
</div>
{%- endblock %}"""


def _mv_admin_disputes_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Disputes — Admin{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>⚖️ Disputes & Returns</h2>
    <a href="{{ url_for('admin_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-table-wrap">
    <table class="mv-table">
      <thead><tr><th>#</th><th>Order</th><th>Customer</th><th>Reason</th><th>Status</th><th>Date</th><th>Action</th></tr></thead>
      <tbody>
        {%- for r in returns %}
        <tr>
          <td>{{ r.id }}</td>
          <td style="font-weight:700">#{{ r.order_id }}</td>
          <td>{{ r.customer_name }}</td>
          <td style="max-width:180px;font-size:.85rem;color:#555">{{ r.reason[:80] }}{% if r.reason|length > 80 %}…{% endif %}</td>
          <td><span class="badge badge-{{ 'paid' if r.status=='refunded' else 'pending' if r.status=='requested' else 'confirmed' if r.status=='approved' else 'cancelled' }}">{{ r.status|capitalize }}</span></td>
          <td style="color:#888;font-size:.82rem">{{ r.created_at[:10] }}</td>
          <td>
            {%- if r.status in ['requested','approved'] %}
            <form method="POST" action="{{ url_for('admin_dispute_action', rid=r.id) }}" style="display:flex;gap:.4rem;flex-wrap:wrap">
              <input type="number" name="refund_amount" placeholder="Refund ₹" step="0.01" style="width:90px;padding:.3rem .5rem;border:1.5px solid #eee;border-radius:6px;font-size:.8rem"/>
              <input type="text" name="admin_note" placeholder="Note" style="width:110px;padding:.3rem .5rem;border:1.5px solid #eee;border-radius:6px;font-size:.8rem"/>
              <button name="action" value="approve" class="mv-btn mv-btn-primary mv-btn-sm">Approve</button>
              <button name="action" value="refund" class="mv-btn mv-btn-outline mv-btn-sm">Refund</button>
              <button name="action" value="reject" class="mv-btn mv-btn-danger mv-btn-sm">Reject</button>
            </form>
            {%- else %}
            <span style="color:#888;font-size:.82rem">{{ r.admin_note or '—' }}</span>
            {%- endif %}
          </td>
        </tr>
        {%- else %}
        <tr><td colspan="7" style="text-align:center;color:#888;padding:2rem">No disputes.</td></tr>
        {%- endfor %}
      </tbody>
    </table>
  </div>
</div>
{%- endblock %}"""


def _mv_admin_banners_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Banners — Admin{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>🖼️ Banner Management</h2>
    <a href="{{ url_for('admin_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-table-wrap" style="margin-bottom:1.5rem">
    <div style="padding:1.25rem;border-bottom:1px solid #eee;font-weight:700">Add New Banner (max 3 active)</div>
    <div style="padding:1.25rem">
      <form method="POST" action="{{ url_for('admin_add_banner') }}" enctype="multipart/form-data"
            style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:.75rem;align-items:end">
        <div><label style="font-size:.82rem;font-weight:600;display:block;margin-bottom:.3rem">Title *</label>
          <input type="text" name="title" class="mv-form-input" placeholder="Banner title" required/></div>
        <div><label style="font-size:.82rem;font-weight:600;display:block;margin-bottom:.3rem">Link URL</label>
          <input type="text" name="link" class="mv-form-input" placeholder="/deals/"/></div>
        <div><label style="font-size:.82rem;font-weight:600;display:block;margin-bottom:.3rem">Position</label>
          <input type="number" name="position" class="mv-form-input" value="0" min="0"/></div>
        <div><label style="font-size:.82rem;font-weight:600;display:block;margin-bottom:.3rem">Image *</label>
          <input type="file" name="image" accept="image/*" required style="width:100%"/></div>
        <div><button type="submit" class="mv-btn mv-btn-primary" style="width:100%">Add Banner</button></div>
      </form>
    </div>
  </div>
  <div class="mv-table-wrap">
    <table class="mv-table">
      <thead><tr><th>Preview</th><th>Title</th><th>Link</th><th>Position</th><th>Status</th><th>Action</th></tr></thead>
      <tbody>
        {%- for b in banners %}
        <tr>
          <td><img src="{{ url_for('static', filename='uploads/' + b.image) }}"
                   style="width:80px;height:44px;object-fit:cover;border-radius:6px"
                   onerror="this.src='https://placehold.co/80x44/eee/999?text=Banner'"/></td>
          <td style="font-weight:700">{{ b.title }}</td>
          <td style="font-size:.82rem;color:#888">{{ b.link or '—' }}</td>
          <td>{{ b.position }}</td>
          <td><span class="badge badge-{{ 'paid' if b.is_active else 'cancelled' }}">{{ 'Active' if b.is_active else 'Inactive' }}</span></td>
          <td>
            <form method="POST" action="{{ url_for('admin_delete_banner', bid=b.id) }}" onsubmit="return confirm('Delete banner?')">
              <button class="mv-btn mv-btn-danger mv-btn-sm">Delete</button>
            </form>
          </td>
        </tr>
        {%- else %}
        <tr><td colspan="6" style="text-align:center;color:#888;padding:2rem">No banners yet.</td></tr>
        {%- endfor %}
      </tbody>
    </table>
  </div>
</div>
{%- endblock %}"""


def _mv_admin_newsletter_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Newsletter — Admin{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>📧 Newsletter Subscribers</h2>
    <a href="{{ url_for('admin_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-table-wrap">
    <div class="mv-table-head">
      <h3>Subscribers ({{ subscribers|length }})</h3>
    </div>
    <table class="mv-table">
      <thead><tr><th>#</th><th>Email</th><th>Status</th><th>Subscribed</th></tr></thead>
      <tbody>
        {%- for s in subscribers %}
        <tr>
          <td style="color:#888">{{ loop.index }}</td>
          <td>{{ s.email }}</td>
          <td><span class="badge badge-{{ 'paid' if s.is_active else 'cancelled' }}">{{ 'Active' if s.is_active else 'Unsubscribed' }}</span></td>
          <td style="color:#888;font-size:.82rem">{{ s.subscribed_at[:10] }}</td>
        </tr>
        {%- else %}
        <tr><td colspan="4" style="text-align:center;color:#888;padding:2rem">No subscribers yet.</td></tr>
        {%- endfor %}
      </tbody>
    </table>
  </div>
</div>
{%- endblock %}"""
